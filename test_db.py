import mysql.connector

print("Starting DB test...")   # <--- Add this

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="elite_parking"
    )
    cursor = db.cursor()
    print("Database connection OK")
except Exception as e:
    print("Database connection FAILED:", e)
