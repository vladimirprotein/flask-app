from flask import Flask, request
from celery import Celery
from flask_mysqldb import MySQL
from mysql.connector import connection
import uuid

app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = "redis://redis:6379/0"
app.config["CELERY_BACKEND_URL"] = "redis://redis:6379/0"

celery = Celery('cel-worker', broker=app.config["CELERY_BROKER_URL"], backend=app.config["CELERY_BACKEND_URL"])
# celery.conf.update(app.config)

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'password'
# app.config['MYSQL_DB'] = 'flask'
# mysql = MySQL(app)

# cnx = connection.MySQLConnection(user='root', password='password',
#                                  host='db', port='3306',
#                                  database='flask')


@app.get("/")
def test():
    return "all ok"


@app.get("/sample")
def test_sample():
    res = celery.send_task('tasks.sample_task')
    return res.id


@app.post("/employee")
def add_employee():
    request_data = request.get_json()
    new_id = uuid.uuid4().hex[:15]
    name, email = request_data["name"], request_data["email"]
    new_employee = {"id": new_id, "name": name, "email": email}
    res = celery.send_task('tasks.add_employee_sql', kwargs={'obj': new_employee})
    return {"message": f"Employee added to queue successfully (id: {res.id})", "employee": new_employee}, 200


@app.get("/employee")
def get_employees():
    cnx = connection.MySQLConnection(user='ani', password='password',
                                     host='db', port='3306',
                                     database='flask')
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM employees")
    res = list(cursor.fetchall())
    if len(res):
        employees = [{"id": i[0], "name": i[1], "email": i[2]} for i in res]
        return {"message": "Employees fetched successfully", "employees": employees}
    return {"message": "No employees found", "employees": []}


@app.get("/employee/<string:idx>")
def get_employee(idx):
    cnx = connection.MySQLConnection(user='root', password='password',
                                     host='db', port='3306',
                                     database='flask')
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = %s", (idx,))
    res = list(cursor.fetchall())
    print(res)
    if len(res):
        result = res[0]
        employee = {"id": result[0], "name": result[1], "email": result[2]}
        return {"message": "Employee found", "employee": employee}
    return {"message": "Employee does not exist"}, 404


@app.put("/employee/<string:idx>")
def update_employee(idx):
    request_data = request.get_json()
    name, email = request_data["name"], request_data["email"]
    new_employee = {"id": idx, "name": name, "email": email}
    try:
        cnx = connection.MySQLConnection(user='root', password='password',
                                         host='db', port='3306',
                                         database='flask')
        cursor = cnx.cursor()
        cursor.execute("UPDATE employees SET name = %s, email = %s WHERE id = %s", (name, email, idx))
        cnx.commit()
        return {"message": "Employee updated successfully", "employee": new_employee}
    except Exception as e_x:
        return {"message": "Failed to edit employee"}, 400


@app.delete("/employee/<string:idx>")
def delete_employee(idx):
    try:
        cnx = connection.MySQLConnection(user='root', password='password',
                                         host='db', port='3306',
                                         database='flask')
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (idx,))
        cnx.commit()
        return {"message": "Employee id deleted successfully"}

    except Exception as e_x:
        return {"message": "Failed to delete employee"}, 400
