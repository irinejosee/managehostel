import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysqlmaggie@1234",
        database="hostelm"   # <-- Use the exact DB name you created
    )