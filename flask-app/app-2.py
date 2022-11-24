from flask import Flask, request
from celery import Celery
from time import sleep
from flask_mysqldb import MySQL
import uuid

app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379"
app.config["CELERY_BACKEND_URL"] = 'db+mysql://root:password@localhost/flask'

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"], backend=app.config["CELERY_BACKEND_URL"])
celery.conf.update(app.config)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flask'

mysql = MySQL(app)


@app.post("/employee")
def add_employee():
    request_data = request.get_json()
    new_id = uuid.uuid4().hex[:15]
    name, email = request_data["name"], request_data["email"]
    new_employee = {"id": new_id, "name": name, "email": email}
    res = add_employee_sql.delay(new_employee)
    return {"message": "Employee added to queue successfully", "employee": new_employee}, 200


@celery.task()
def add_employee_sql(obj):
    sleep(10)
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO employees(id, name, email) VALUES(%s, %s, %s)", (obj["id"], obj["name"], obj["email"]))
            mysql.connection.commit()
            cursor.close()
    except Exception as e_x:
        return e_x
    return 'DONE'


@app.get("/employee")
def get_employees():
    cursor = mysql.connection.cursor()
    rows = cursor.execute("SELECT * FROM employees")
    if rows:
        result = list(cursor.fetchall())
        employees = [{"id": i[0], "name": i[1], "email": i[2]} for i in result]
        return {"message": "Employees fetched successfully", "employees": employees}
    return {"message": "No employees found", "employees": []}


@app.get("/employee/<string:idx>")
def get_employee(idx):
    cursor = mysql.connection.cursor()
    row = cursor.execute("SELECT * FROM employees WHERE id = %s", (idx,))
    if row:
        result = list(cursor.fetchall())[0]
        employee = {"id": result[0], "name": result[1], "email": result[2]}
        return {"message": "Employee found", "employee": employee}
    return {"message": "Employee does not exist"}, 404


@app.put("/employee/<string:idx>")
def update_employee(idx):
    request_data = request.get_json()
    name, email = request_data["name"], request_data["email"]
    new_employee = {"id": idx, "name": name, "email": email}
    try:
        cursor = mysql.connection.cursor()
        res = cursor.execute("UPDATE employees SET name = %s, email = %s WHERE id = %s", (name, email, idx))
        if res:
            mysql.connection.commit()
            return {"message": "Employee updated successfully", "employee": new_employee}
        return {"message": "Invalid id or no change in updated data"}
    except Exception as e_x:
        return {"message": "Failed to edit employee"}, 400


@app.delete("/employee/<string:idx>")
def delete_employee(idx):
    try:
        cursor = mysql.connection.cursor()
        res = cursor.execute("DELETE FROM employees WHERE id = %s", (idx,))
        if res:
            mysql.connection.commit()
            return {"message": "Employee id deleted successfully"}
        return {"message": "Employee id does not exist"}

    except Exception as e_x:
        return {"message": "Failed to delete employee"}, 400
