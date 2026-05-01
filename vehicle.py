import sqlite3

def get_db_connection():
    return sqlite3.connect('parking_system.db')

def add_vehicle(plate_number, vehicle_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO vehicles (plate_number, vehicle_type) VALUES (?, ?)"
    cursor.execute(query, (plate_number, vehicle_type))
    conn.commit()
    vehicle_id = cursor.lastrowid
    conn.close()
    return vehicle_id

def remove_vehicle(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM vehicles WHERE id=?"
    cursor.execute(query, (vehicle_id,))
    conn.commit()
    conn.close()

def get_all_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    conn.close()
    return vehicles
