from flask_mysqldb import MySQL
import os

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_HOST']        = os.environ.get('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER']        = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD']    = os.environ.get('MYSQL_PASSWORD', 'Mysql@2026')
    app.config['MYSQL_DB']          = os.environ.get('MYSQL_DB', 'canteen_expresss')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    mysql.init_app(app)