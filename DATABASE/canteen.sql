-- ============================================================
-- Banbwu Cafe - Full Database Setup Script
-- Run this file once to set up your entire database
-- ============================================================

-- Step 1: Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS canteen_expresss;

-- Step 2: Tell MySQL to use this database for all commands below
USE canteen_expresss;

-- ============================================================
-- TABLE 1: users
-- Stores student and staff accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100)  NOT NULL,
    email    VARCHAR(100)  NOT NULL UNIQUE,
    password VARCHAR(255)  NOT NULL,
    role     ENUM('user','staff') DEFAULT 'user'
);

-- ============================================================
-- TABLE 2: menu
-- Stores all food items and prices
-- ============================================================
CREATE TABLE IF NOT EXISTS menu (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100)  NOT NULL,
    price     DECIMAL(10,2) NOT NULL
);

-- ============================================================
-- TABLE 3: orders
-- Each row = one complete order by a student
-- ============================================================
CREATE TABLE IF NOT EXISTS orders (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT         NOT NULL,
    token_no   INT         NOT NULL,
    status     VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================================================
-- TABLE 4: order_items
-- Each row = one item inside an order
-- ============================================================
CREATE TABLE IF NOT EXISTS order_items (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_id  INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_id)  REFERENCES menu(id)
);

-- ============================================================
-- SAMPLE MENU DATA
-- 15 items so the dashboard looks full and realistic
-- ============================================================
INSERT INTO menu (item_name, price) VALUES
('Chicken Biryani',     120.00),
('Beef Burger',          90.00),
('Vegetable Sandwich',   50.00),
('French Fries',         60.00),
('Chicken Roll',         80.00),
('Daal Chawal',          70.00),
('Zinger Burger',       110.00),
('Egg Fried Rice',       85.00),
('Cold Coffee',          60.00),
('Mango Lassi',          55.00),
('Mineral Water',        20.00),
('Samosa (2 pcs)',        30.00),
('Grilled Chicken',     130.00),
('Pasta Alfredo',       100.00),
('Chocolate Shake',      75.00);

-- ============================================================
-- VERIFY: Run these SELECT statements to confirm everything
-- ============================================================
SELECT 'Tables created successfully!' AS message;
SELECT COUNT(*) AS total_menu_items FROM menu;