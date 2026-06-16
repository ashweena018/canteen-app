from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import get_db, init_db

app = Flask(__name__)
app.secret_key = 'canteen_express_2024'
init_db(app)


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('full_name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        role     = request.form.get('role', 'user')

        if not name or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return render_template('register.html')

        try:
            cursor = get_db().cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered! Please login.', 'warning')
                cursor.close()
                return render_template('register.html')

            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)",
                (name, email, hashed, role)
            )
            get_db().commit()
            cursor.close()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash('Error: ' + str(e), 'danger')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password!', 'danger')
            return render_template('login.html')

        try:
            cursor = get_db().cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user['password'], password):
                session['user_id']   = user['id']
                session['full_name'] = user['name']
                session['role']      = user['role']
                flash('Welcome ' + user['name'] + '!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong email or password!', 'danger')
                return render_template('login.html')

        except Exception as e:
            flash('Error: ' + str(e), 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    try:
        cursor = get_db().cursor()

        # Fetch all available menu items from database
        # We order by category so food, drinks, snacks are grouped
        cursor.execute("""
            SELECT * FROM menu 
            ORDER BY id ASC
        """)
        menu_items = cursor.fetchall()
        cursor.close()

        # Pass menu_items to template
        # Template can now loop through this list
        return render_template('dashboard.html', menu_items=menu_items)

    except Exception as e:
        flash('Error loading menu: ' + str(e), 'danger')
        return render_template('dashboard.html', menu_items=[])


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/test-db')
def test_db():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT VERSION()")
        data = cursor.fetchone()
        cursor.close()
        return '<h2>Connected!</h2><p>' + str(data) + '</p>'
    except Exception as e:
        return '<h2>Failed</h2><p>' + str(e) + '</p>'

# ══════════════════════════════════════════
# ADD TO CART
# ══════════════════════════════════════════
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    # Check login
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    # Read form data sent from dashboard
    menu_id   = int(request.form.get('menu_id'))
    item_name = request.form.get('item_name')
    price     = float(request.form.get('price'))
    quantity  = int(request.form.get('quantity', 1))

    # Get existing cart from session
    # If no cart exists yet, start with empty list
    cart = session.get('cart', [])

    # Check if item already in cart
    # If yes, just increase quantity
    item_found = False
    for item in cart:
        if item['menu_id'] == menu_id:
            item['quantity'] += quantity
            item_found = True
            break

    # If item not in cart, add it as new item
    if not item_found:
        cart.append({
            'menu_id'  : menu_id,
            'item_name': item_name,
            'price'    : price,
            'quantity' : quantity
        })

    # Save updated cart back to session
    session['cart'] = cart

    # IMPORTANT: Tell Flask session was modified
    session.modified = True

    flash(item_name + ' added to cart!', 'success')
    return redirect(url_for('dashboard'))


# ══════════════════════════════════════════
# VIEW CART
# ══════════════════════════════════════════
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    # Get cart from session
    cart_items = session.get('cart', [])

    # Calculate total price
    # total = sum of (price * quantity) for each item
    total = sum(
        item['price'] * item['quantity'] 
        for item in cart_items
    )

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )


# ══════════════════════════════════════════
# REMOVE FROM CART
# ══════════════════════════════════════════
@app.route('/remove-from-cart/<int:menu_id>')
def remove_from_cart(menu_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get cart
    cart = session.get('cart', [])

    # Keep all items EXCEPT the one we want to remove
    # This is called list comprehension in Python
    cart = [item for item in cart if item['menu_id'] != menu_id]

    # Save updated cart
    session['cart'] = cart
    session.modified = True

    flash('Item removed from cart!', 'warning')
    return redirect(url_for('cart'))


# ══════════════════════════════════════════
# CLEAR CART
# ══════════════════════════════════════════
@app.route('/clear-cart')
def clear_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    session.pop('cart', None)
    session.modified = True
    flash('Cart cleared!', 'warning')
    return redirect(url_for('cart'))

# ══════════════════════════════════════════
# PLACE ORDER
# ══════════════════════════════════════════
@app.route('/place-order')
def place_order():
    # Check login
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    # Get cart
    cart_items = session.get('cart', [])

    # Check cart is not empty
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    try:
        cursor = get_db().cursor()

        # ── Step 1: Generate Token Number ──────────
        # Get the highest token number currently in database
        # If no orders yet, MAX returns None → we use 0
        cursor.execute("SELECT MAX(token_no) as max_token FROM orders")
        result = cursor.fetchone()

        # If no orders exist yet, start from 0
        # next token = last token + 1
        last_token = result['max_token'] if result['max_token'] else 0
        new_token  = last_token + 1

        # ── Step 2: Calculate Total Price ──────────
        total_price = sum(
            item['price'] * item['quantity']
            for item in cart_items
        )

        # ── Step 3: Insert into orders table ───────
        cursor.execute(
            """
            INSERT INTO orders (user_id, token_no, status, total_price)
            VALUES (%s, %s, %s, %s)
            """,
            (session['user_id'], new_token, 'Pending', total_price)
        )

        # Get the ID of the order we just inserted
        # lastrowid = ID of last inserted row
        order_id = cursor.lastrowid

        # ── Step 4: Insert each cart item ──────────
        for item in cart_items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, menu_id, quantity)
                VALUES (%s, %s, %s)
                """,
                (order_id, item['menu_id'], item['quantity'])
            )

        # ── Step 5: Commit everything ───────────────
        # Both inserts save together (transaction)
        get_db().commit()
        cursor.close()

        # ── Step 6: Clear the cart ──────────────────
        session.pop('cart', None)
        session.modified = True

        # ── Step 7: Show token page ─────────────────
        return render_template(
            'token.html',
            token_number = new_token,
            total_price  = total_price,
            order_id     = order_id,
            cart_items   = cart_items
        )

    except Exception as e:
        flash('Error placing order: ' + str(e), 'danger')
        return redirect(url_for('cart'))


# ══════════════════════════════════════════
# ORDER HISTORY
# ══════════════════════════════════════════
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    try:
        cursor = get_db().cursor()

        # Get all orders for this user
        # Most recent first (ORDER BY created_at DESC)
        cursor.execute(
            """
            SELECT * FROM orders 
            WHERE user_id = %s 
            ORDER BY created_at DESC
            """,
            (session['user_id'],)
        )
        orders = cursor.fetchall()
        cursor.close()

        return render_template('history.html', orders=orders)

    except Exception as e:
        flash('Error: ' + str(e), 'danger')
        return render_template('history.html', orders=[])

# ══════════════════════════════════════════
# KITCHEN DASHBOARD
# ══════════════════════════════════════════
@app.route('/kitchen')
def kitchen():
    # Only staff can access kitchen
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    if session.get('role') != 'staff':
        flash('Access denied! Staff only.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        cursor = get_db().cursor()

        # Get all orders with user names
        # JOIN connects orders table with users table
        # So we can show customer name with each order
        cursor.execute("""
            SELECT 
                o.id,
                o.token_no,
                o.status,
                o.total_price,
                o.created_at,
                u.name as customer_name
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
        """)
        orders = cursor.fetchall()
        cursor.close()

        return render_template('kitchen.html', orders=orders)

    except Exception as e:
        flash('Error: ' + str(e), 'danger')
        return render_template('kitchen.html', orders=[])


# ══════════════════════════════════════════
# UPDATE ORDER STATUS
# ══════════════════════════════════════════
@app.route('/update-status/<int:order_id>/<string:new_status>')
def update_status(order_id, new_status):
    # Only staff can update status
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'staff':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))

    # Only allow valid status values
    allowed = ['Pending', 'Preparing', 'Ready', 'Completed']
    if new_status not in allowed:
        flash('Invalid status!', 'danger')
        return redirect(url_for('kitchen'))

    try:
        cursor = get_db().cursor()
        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (new_status, order_id)
        )
        get_db().commit()
        cursor.close()
        flash('Order #' + str(order_id) + ' updated to ' + new_status, 'success')

    except Exception as e:
        flash('Error: ' + str(e), 'danger')

    return redirect(url_for('kitchen'))

if __name__ == '__main__':
    app.run(debug=True)
    