import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="parking_system"
)
cursor = db.cursor()

def add_payment(vehicle_id, amount):
    query = "INSERT INTO receipts (slot_number, amount) VALUES (%s, %s)"
    cursor.execute(query, (vehicle_id, amount))
    db.commit()

def calculate_fee(hours_parked):
    rate_per_hour = 50  # PKR
    return hours_parked * rate_per_hour
