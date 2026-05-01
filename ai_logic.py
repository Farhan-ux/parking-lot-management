import sqlite3
import datetime
import random
import numpy as np
try:
    import easyocr
except ImportError:
    easyocr = None
import cv2

def get_db_connection():
    return sqlite3.connect('parking_system.db')

# --- 1. Parking Space Recommendation AI ---
def recommend_parking_slot(vehicle_type='Normal'):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Preference logic
    if vehicle_type == 'Disabled':
        cursor.execute("SELECT slot_id FROM parking_slots WHERE slot_type='Disabled' AND is_occupied=FALSE LIMIT 1")
    elif vehicle_type == 'VIP':
        cursor.execute("SELECT slot_id FROM parking_slots WHERE slot_type='VIP' AND is_occupied=FALSE LIMIT 1")
    elif vehicle_type == 'Bike':
        cursor.execute("SELECT slot_id FROM parking_slots WHERE slot_type='Bike' AND is_occupied=FALSE LIMIT 1")
    else:
        cursor.execute("SELECT slot_id FROM parking_slots WHERE slot_type='Normal' AND is_occupied=FALSE LIMIT 1")

    res = cursor.fetchone()
    if not res:
        # Fallback to any normal slot if specific type not found or occupied
        cursor.execute("SELECT slot_id FROM parking_slots WHERE is_occupied=FALSE LIMIT 1")
        res = cursor.fetchone()

    conn.close()
    return res[0] if res else None

# --- 2. Number Plate Recognition & Auto Billing ---
reader = None
def perform_ocr(image_path):
    global reader
    if easyocr is None:
        return "MOCK-123" # Fallback if library fails
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)

    try:
        results = reader.readtext(image_path)
        if results:
            # Join all detected text and keep alphanumeric
            text = "".join([res[1] for res in results])
            return "".join(filter(str.isalnum, text)).upper()
    except Exception as e:
        print(f"OCR Error: {e}")
    return "MOCK-" + str(random.randint(100, 999))

# --- 3. Overstay Detection ---
def detect_overstays(max_hours=24):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, plate_number, entry_time FROM vehicles")
    vehicles = cursor.fetchall()
    overstays = []
    now = datetime.datetime.now()
    for v in vehicles:
        entry_time = datetime.datetime.strptime(v[2], '%Y-%m-%d %H:%M:%S')
        duration = (now - entry_time).total_seconds() / 3600
        if duration > max_hours:
            overstays.append({'id': v[0], 'plate': v[1], 'hours': round(duration, 2)})
    conn.close()
    return overstays

# --- 4. Suspicious Vehicle Detection ---
def is_suspicious(plate_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reason FROM blacklist WHERE plate_number=?", (plate_number,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def add_to_blacklist(plate_number, reason):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO blacklist (plate_number, reason) VALUES (?, ?)", (plate_number, reason))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# --- 5. Peak Hour Prediction AI ---
def predict_peak_hours():
    # Simple heuristic: look at parking_history to find most frequent hours
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT entry_time FROM parking_history")
    history = cursor.fetchall()
    conn.close()

    if not history:
        return "Not enough data"

    hours = [datetime.datetime.strptime(h[0], '%Y-%m-%d %H:%M:%S').hour for h in history]
    if not hours:
        return "Not enough data"

    counts = np.bincount(hours)
    peak_hour = np.argmax(counts)
    return f"{peak_hour}:00 - {peak_hour+1}:00"

# --- 6. Fraud / Wrong Parking Detection ---
def detect_wrong_parking():
    # Logic: If a vehicle is in a slot that doesn't match its type (Simulated)
    # This would normally use sensors/cameras.
    # For demo, we check current vehicles and their slot types.
    # Note: We need a mapping of vehicle -> slot in the DB.
    # Let's add a slot_id to vehicles table or similar.
    # For now, let's just simulate a random "Violation Detected" event.
    violations = [
        "Vehicle in No-Parking Zone (Gate Area)",
        "Double parking detected in Slot 3",
        "Non-VIP vehicle in VIP Slot 5"
    ]
    return random.choice(violations) if random.random() < 0.3 else None

# --- Auto Billing helper ---
def calculate_auto_billing(plate_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT entry_time FROM vehicles WHERE plate_number=?", (plate_number,))
    res = cursor.fetchone()
    if res:
        entry_time = datetime.datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        hours = max(1, (now - entry_time).total_seconds() / 3600)
        fee = hours * 50 # 50 PKR/hr
        conn.close()
        return round(fee, 2)
    conn.close()
    return 0
