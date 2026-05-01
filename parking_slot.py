import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="parking_system"
)
cursor = db.cursor()

def add_slot(slot_id):
    query = "INSERT INTO parking_slots (slot_id) VALUES (%s)"
    cursor.execute(query, (slot_id,))
    db.commit()
    return cursor.lastrowid

def occupy_slot(slot_id):
    query = "UPDATE parking_slots SET is_occupied=TRUE WHERE slot_id=%s"
    cursor.execute(query, (slot_id,))
    db.commit()

def free_slot(slot_id):
    query = "UPDATE parking_slots SET is_occupied=FALSE WHERE slot_id=%s"
    cursor.execute(query, (slot_id,))
    db.commit()

def get_available_slots():
    cursor.execute("SELECT slot_id, is_occupied FROM parking_slots WHERE is_occupied=FALSE")
    return cursor.fetchall()
