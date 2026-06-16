import pymysql
import pymysql.cursors
from flask import g
import os

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'Mysql@2026'),
            database=os.environ.get('MYSQL_DB', 'canteen_expresss'),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def init_db(app):
    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()