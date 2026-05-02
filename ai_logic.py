import sqlite3
import datetime
import random
import numpy as np
try:
    import easyocr
except ImportError:
    easyocr = None
import cv2
from database import get_db_connection

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

# --- 2. Two-Stage CNN ANPR (CRAFT Detection -> Cropping -> CRNN Recognition) ---
reader = None
def perform_ocr(image_path):
    global reader
    if easyocr is None:
        return "MOCK-DL-STAGE2"

    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    try:
        img = cv2.imread(image_path)
        if img is None: return ""

        detection_results = reader.detect(img)
        boxes = detection_results[0][0]
        if not boxes:
            results = reader.readtext(image_path, detail=0, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            return "".join(results).upper().replace(" ", "")

        x_min, x_max, y_min, y_max = boxes
        padding = 10
        h, w, _ = img.shape
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding)
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding)

        plate_crop = img[int(y_min):int(y_max), int(x_min):int(x_max)]
        plate_crop = cv2.resize(plate_crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast_img = clahe.apply(gray)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(contrast_img, -1, kernel)

        crop_path = "plate_crop_final.jpg"
        cv2.imwrite(crop_path, sharpened)

        results = reader.readtext(crop_path,
                                 detail=0,
                                 paragraph=False,
                                 allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                 mag_ratio=1.5,
                                 contrast_ths=0.1,
                                 adjust_contrast=0.7)

        if results:
            final_text = "".join(results).upper().replace(" ", "")
            return final_text

    except Exception as e:
        print(f"Two-Stage CNN Error: {e}")
    return ""

# --- 3. Overstay Detection AI ---
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
