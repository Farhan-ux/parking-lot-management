import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="parking_system"
)
cursor = db.cursor()

def add_vehicle(plate_number, vehicle_type):
    query = "INSERT INTO vehicles (plate_number, vehicle_type) VALUES (%s, %s)"
    cursor.execute(query, (plate_number, vehicle_type))
    db.commit()
    return cursor.lastrowid

def remove_vehicle(vehicle_id):
    query = "DELETE FROM vehicles WHERE id=%s"
    cursor.execute(query, (vehicle_id,))
    db.commit()

def get_all_vehicles():
    cursor.execute("SELECT * FROM vehicles")
    return cursor.fetchall()
