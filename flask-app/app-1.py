from flask import Flask, request
from flask_mysqldb import MySQL
import uuid

app = Flask(__name__)

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
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO employees(id, name, email) VALUES(%s, %s, %s)", (new_id, name, email))
        mysql.connection.commit()
        cursor.close()
        return {"message": "Employee added successfully", "employee": new_employee}, 201
    except Exception as e_x:
        print(e_x)
        return {"message": "Failed to add employee"}, 400


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
    return {"message": f"Employee id {idx} does not exist"}, 404


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
            return {"message": f"Employee id {idx} deleted successfully"}
        return {"message": f"Employee id {idx} does not exist"}

    except Exception as e_x:
        return {"message": "Failed to delete employee"}, 400
