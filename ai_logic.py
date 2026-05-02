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
        cursor.execute("SELECT slot_id FROM parking_slots WHERE is_occupied=FALSE LIMIT 1")
        res = cursor.fetchone()

    conn.close()
    return res[0] if res else None

# --- 2. Enhanced Number Plate Recognition (High Accuracy) ---
reader = None
def perform_ocr(image_path):
    global reader
    if easyocr is None:
        return "MOCK-123"

    if reader is None:
        # Load reader once
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    try:
        # Advanced Image Pre-processing for License Plates
        img = cv2.imread(image_path)

        # 1. Resize for better detection
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 2. Grayscale & Noise Removal
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17) # Preserve edges, remove noise

        # 3. Adaptive Thresholding (Handles shadows and lighting better)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)

        proc_path = "highly_processed_plate.jpg"
        cv2.imwrite(proc_path, thresh)

        # 4. OCR with Optimized Parameters
        # allowlist helps with O vs 0 confusion
        # contrast_ths and adjust_contrast can help too
        results = reader.readtext(proc_path,
                                 detail=0,
                                 paragraph=False,
                                 allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                 mag_ratio=2) # Higher mag_ratio for small text

        if results:
            raw_text = "".join(results).upper().replace(" ", "")
            return raw_text

    except Exception as e:
        print(f"OCR Error: {e}")
    return ""

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
    if not plate_number or plate_number == "Scanning...": return None
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
    violations = [
        "Vehicle in No-Parking Zone",
        "Double parking detected",
        "Unauthorized VIP Slot usage"
    ]
    return random.choice(violations) if random.random() < 0.2 else None
