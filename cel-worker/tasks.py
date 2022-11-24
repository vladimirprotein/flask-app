from flask import Flask
from time import sleep
from celery import Celery
from flask_mysqldb import MySQL
from mysql.connector import connection

cel = Celery('task', broker="redis://redis:6379/0", backend="redis://redis:6379/0")
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flask'

# mysql = MySQL(app)
# cnx = connection.MySQLConnection(user='root', password='password',
#                                  host='db', port='3306',
#                                  database='flask')


@cel.task()
def add_employee_sql(obj):
    sleep(5)
    try:
        # with app.app_context():
        cnx = connection.MySQLConnection(user='ani', password='password',
                                         host='db', port='3306',
                                         database='flask')
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO employees(id, name, email) VALUES(%s, %s, %s)", (obj["id"], obj["name"], obj["email"]))
        cnx.commit()
        cursor.close()
    except Exception as e_x:
        return e_x
    return 'DONE'

@cel.task()
def sample_task():
    sleep(5)
    return 'heyy from sample'
