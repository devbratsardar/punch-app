import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages

# Read DB config from environment variables
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", ""),
    database=os.environ.get("DB_NAME", "punching_app")
)
cursor = db.cursor()

# Home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        emp_id = request.form['employee_id']
        action = request.form['action']  # 'in' or 'out'
        # Check if employee exists
        cursor.execute("SELECT name FROM employees WHERE id = %s", (emp_id,))
        emp = cursor.fetchone()

        if not emp:
            flash("Employee ID not found!", "error")
            return redirect(url_for('home'))

        # Record punch
        cursor.execute(
            "INSERT INTO punches (employee_id, punch_type) VALUES (%s, %s)",
            (emp_id, action)
        )
        db.commit()
        flash(f"Successfully punched {action} for {emp[0]} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "success")
        return redirect(url_for('home'))

    return render_template('index.html')
# Employee list page
@app.route('/employees')
def employee_list():
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()
    return render_template('employees.html', employees=employees)

# punch data list page
@app.route('/punch')
def punch_list():
    cursor.execute("SELECT p.id,e.name,p.punch_type,p.punch_time FROM punches p left join employees e on e.id=p.employee_id")
    punch = cursor.fetchall()
    return render_template('punch.html', punch=punch)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
