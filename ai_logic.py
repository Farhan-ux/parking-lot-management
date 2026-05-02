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

# --- 2. Advanced Deep Learning ANPR (Using CRAFT + CRNN) ---
reader = None
def perform_ocr(image_path):
    global reader
    if easyocr is None:
        return "MOCK-DL-123"

    if reader is None:
        # EasyOCR uses CRAFT (Convolutional Character Region Awareness) for detection
        # and CRNN (Convolutional Recurrent Neural Network) for recognition.
        # This is a state-of-the-art Deep Learning pipeline.
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    try:
        # Load and Pre-process image for DL Model
        img = cv2.imread(image_path)

        # 1. Upscale for better resolution (DL models like high-res features)
        img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

        # 2. Convert to Gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Bilateral Filter to remove noise while keeping edges sharp
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # 4. Sharpening filter to enhance character edges
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(gray, -1, kernel)

        proc_path = "dl_processed_plate.jpg"
        cv2.imwrite(proc_path, sharpened)

        # 5. Run Deep Learning Recognition
        # paragraph=False: find single lines
        # mag_ratio=2: internal magnification
        results = reader.readtext(proc_path,
                                 detail=0,
                                 paragraph=False,
                                 allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                 mag_ratio=2,
                                 contrast_ths=0.1,
                                 adjust_contrast=0.5)

        if results:
            # DL models often return multiple fragments; we combine them
            raw_text = "".join(results).upper().replace(" ", "")
            return raw_text

    except Exception as e:
        print(f"Deep Learning Model Error: {e}")
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

# --- 4. Deep-Check Suspicious Vehicle Detection ---
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

# --- 5. Peak Hour Prediction AI (Statistical Learning) ---
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

# --- 6. Fraud / Wrong Parking Detection (Computer Vision Simulation) ---
def detect_wrong_parking():
    violations = [
        "Vehicle in No-Parking Zone",
        "Double parking detected",
        "Unauthorized VIP Slot usage"
    ]
    return random.choice(violations) if random.random() < 0.2 else None
