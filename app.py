import os
import time
import mysql.connector
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student123"),
        database=os.getenv("DB_NAME", "studentdb")
    )

def init_db():
    for attempt in range(30):
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL
                )
            """)
            db.commit()
            cursor.close()
            db.close()
            return
        except mysql.connector.Error:
            if attempt == 29:
                raise
            time.sleep(2)

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", students=students)

@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    email = request.form["email"].strip()

    if name and email:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO students (name, email) VALUES (%s, %s)",
            (name, email)
        )
        db.commit()
        cursor.close()
        db.close()

    return redirect("/")

@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect("/")

@app.route("/health")
def health():
    try:
        db = get_db()
        db.close()
        return {"status": "healthy"}, 200
    except mysql.connector.Error:
        return {"status": "database unavailable"}, 503

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5678)
