print("THIS IS THE CORRECT APP FILE")
from flask import Flask, render_template, request, redirect, url_for
from db import connect_db

app = Flask(__name__)

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='Full'")
    full_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM payments")
    revenue = cursor.fetchone()[0]
    revenue = revenue if revenue else 0

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_rooms=total_rooms,
        full_rooms=full_rooms,
        revenue=revenue
    )


# ================= ROOMS =================
@app.route("/rooms")
def rooms():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("rooms.html", rooms=rooms)


@app.route("/add_room", methods=["POST"])
def add_room():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO rooms (room_no, type, capacity, rent)
            VALUES (%s, %s, %s, %s)
        """, (
            request.form["room_no"],
            request.form["type"],
            request.form["capacity"],
            request.form["rent"]
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("rooms"))


@app.route("/delete_room/<int:id>")
def delete_room(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM rooms WHERE room_id=%s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("rooms"))


# ================= STUDENTS =================
@app.route("/students")
def students():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT room_id, room_no FROM rooms")
    rooms = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "students.html",
        students=students,
        rooms=rooms
    )


@app.route("/add_student", methods=["POST"])
def add_student():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO students
            (student_id, name, age, gender, room_id, admission_date, contact, email)
            VALUES (%s, %s, %s, %s, %s, CURDATE(), %s, %s)
        """, (
            request.form["student_id"],
            request.form["name"],
            request.form["age"],
            request.form["gender"],
            request.form["room_id"],
            request.form["contact"],
            request.form["email"]
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("students"))


@app.route("/delete_student/<string:id>")
def delete_student(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM students WHERE student_id=%s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("students"))


# ================= PAYMENTS =================
@app.route("/payments")
def payments():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()

    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "payments.html",
        payments=payments,
        students=students
    )


@app.route("/add_payment", methods=["POST"])
def add_payment():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO payments
            (student_id, amount, payment_date, month)
            VALUES (%s, %s, CURDATE(), %s)
        """, (
            request.form["student_id"],
            request.form["amount"],
            request.form["month"]
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("payments"))


@app.route("/delete_payment/<int:id>")
def delete_payment(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM payments WHERE payment_id=%s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("payments"))
# ================= ATTENDANCE =================
from datetime import date

@app.route("/attendance")
def attendance():
    conn = connect_db()
    cursor = conn.cursor()

    selected_date = request.args.get("date", str(date.today()))

    # Get all students
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()

    # Get attendance for selected date
    cursor.execute("""
        SELECT student_id, status
        FROM attendance
        WHERE date=%s
    """, (selected_date,))
    attendance_records = dict(cursor.fetchall())

    cursor.close()
    conn.close()

    return render_template(
        "attendance.html",
        students=students,
        attendance_records=attendance_records,
        selected_date=selected_date
    )


@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    conn = connect_db()
    cursor = conn.cursor()

    selected_date = request.form["date"]

    try:
        for student_id in request.form.getlist("student_id"):
            status = request.form.get(f"status_{student_id}", "Absent")

            cursor.execute("""
                INSERT INTO attendance (student_id, date, status)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE status=%s
            """, (student_id, selected_date, status, status))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("attendance", date=selected_date))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
   