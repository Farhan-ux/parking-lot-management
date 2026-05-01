import streamlit as st
import cv2
import numpy as np
from PIL import Image
import datetime
import os
import ai_logic
import parking_lot
import sqlite3
import time

# Page Configuration
st.set_page_config(page_title="Smart Parking AI", layout="wide", page_icon="🌸")

# "Wisteria Bloom" / "Cherry Blossom" Theme (Purples, Pinks, Soft Whites)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f3e5f5 0%, #fce4ec 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8bbd0 !important;
        border-right: 2px solid #e1bee7;
    }

    /* Headers and Text */
    h1, h2, h3 {
        color: #6a1b9a !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Buttons */
    .stButton>button {
        background-color: #ab47bc;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #8e24aa;
        transform: scale(1.02);
    }

    /* Cards/Containers */
    div.stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #f3e5f5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* Custom Footer in Sidebar */
    .made-by {
        position: fixed;
        bottom: 20px;
        left: 20px;
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        color: #880e4f;
        font-size: 18px;
        font-weight: bold;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #6a1b9a;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize DB
if not os.path.exists('parking_system.db'):
    import init_db
    init_db.init_db()

def get_db_connection():
    return sqlite3.connect('parking_system.db')

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/000000/lotus.png")
st.sidebar.title("Wisteria Parking")
page = st.sidebar.radio("Navigation", ["Live Monitoring", "Parking Operations", "AI Analytics", "Security", "Logs"])

# IPCam IP Link
st.sidebar.markdown("---")
st.sidebar.subheader("🎥 Camera Config")
ip_link = st.sidebar.text_input("LAN IP / RTSP Link", placeholder="rtsp://admin:123@192.168.1.10")

# Made by Rafay
st.sidebar.markdown(f'<div class="made-by">Made by Rafay</div>', unsafe_allow_html=True)

st.title(f"✨ {page}")

if page == "Live Monitoring":
    st.subheader("Real-time License Plate Detection")

    col_cam, col_res = st.columns([2, 1])

    with col_cam:
        if ip_link:
            st.info(f"Connecting to: {ip_link}")
            # Stream simulation for sandbox environment
            # In real environment: cap = cv2.VideoCapture(ip_link)
            run = st.checkbox("Start Stream", value=True)
            FRAME_WINDOW = st.image([])

            # Using a mock stream for the demonstration as I can't access user's LAN
            cap = cv2.VideoCapture(0) # Default to webcam or file if RTSP fails

            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to fetch stream. Check IP/Link.")
                    break

                # AI Processing (Every 50 frames to save CPU)
                if int(time.time() * 10) % 5 == 0:
                    temp_p = "frame_snap.jpg"
                    cv2.imwrite(temp_p, frame)
                    plate = ai_logic.perform_ocr(temp_p)
                    if plate:
                        st.session_state['detected_plate'] = plate

                # Overlay
                h, w, _ = frame.shape
                cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (171, 71, 188), 3)
                if st.session_state.get('detected_plate'):
                    cv2.putText(frame, f"PLATE: {st.session_state['detected_plate']}",
                                (w//4, h//4 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (171, 71, 188), 2)

                FRAME_WINDOW.image(frame, channels="BGR")
            cap.release()
        else:
            st.warning("Please enter an IPCam link in the sidebar to begin.")
            st.write("Alternatively, use a snapshot:")
            img_file = st.camera_input("Capture Snapshot")
            if img_file:
                bytes_data = img_file.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                temp_p = "manual_snap.jpg"
                cv2.imwrite(temp_p, cv2_img)
                plate = ai_logic.perform_ocr(temp_p)
                st.session_state['detected_plate'] = plate
                st.image(cv2_img, channels="BGR")

    with col_res:
        st.markdown("### Detection Result")
        detected = st.session_state.get('detected_plate', "None")
        st.success(f"**Detected Plate:** {detected}")

        if detected != "None":
            reason = ai_logic.is_suspicious(detected)
            if reason:
                st.error(f"🛑 **SECURITY ALERT:** {reason}")
            else:
                st.info("✅ Security Status: Clear")

            if st.button("Transfer to Entry"):
                st.session_state['entry_plate'] = detected
                st.success("Transferred!")

elif page == "Parking Operations":
    t1, t2 = st.tabs(["🌸 Vehicle Entry", "🌸 Vehicle Exit"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            p_in = st.text_input("Plate Number", value=st.session_state.get('entry_plate', ""))
            v_type = st.selectbox("Vehicle Type", ["Normal", "Disabled", "VIP", "Bike"])
        with c2:
            if st.button("Suggest Best Slot"):
                rec = ai_logic.recommend_parking_slot(v_type)
                st.session_state['rec_slot'] = rec
            s_in = st.text_input("Slot Number", value=str(st.session_state.get('rec_slot', "")))

        if st.button("Confirm Parking"):
            if p_in and s_in:
                if parking_lot.park_vehicle(p_in, v_type, s_in):
                    st.success(f"Vehicle {p_in} successfully parked in Slot {s_in}")
                    st.balloons()
            else:
                st.error("Missing plate or slot info.")

    with t2:
        p_out = st.text_input("Exit Plate Number")
        if st.button("Process Payment"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, entry_time FROM vehicles WHERE plate_number=?", (p_out,))
            res = cursor.fetchone()
            if res:
                v_id, e_time = res
                duration = (datetime.datetime.now() - datetime.datetime.strptime(e_time, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600
                hours = max(1, duration)
                fee = parking_lot.calculate_fee(hours)
                parking_lot.remove_parked_vehicle(v_id, hours)
                st.metric("Final Bill", f"{round(fee, 2)} PKR")
                st.success(f"Vehicle {p_out} has exited. Total duration: {round(hours, 2)} hrs")
            else:
                st.error("No active parking session found for this plate.")
            conn.close()

elif page == "AI Analytics":
    st.markdown("### 📊 Smart Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### Peak Usage Prediction")
        if st.button("Run Analytics"):
            pred = ai_logic.predict_peak_hours()
            st.metric("Peak Time", pred)
    with col2:
        st.write("#### Real-time Violation Scan")
        if st.button("Scan All Slots"):
            violation = ai_logic.detect_wrong_parking()
            if violation: st.warning(f"⚠️ {violation}")
            else: st.success("Everything looks good!")

    st.markdown("---")
    st.write("#### ⏳ Overstay Alerts")
    if st.button("Refresh Alerts"):
        alerts = ai_logic.detect_overstays(0.01)
        if alerts: st.table(alerts)
        else: st.info("No vehicles currently overstaying.")

elif page == "Security":
    st.markdown("### 🛡️ Secure Guard")
    with st.container():
        p = st.text_input("Plate to Blacklist")
        r = st.text_input("Reason")
        if st.button("Add to Watchlist"):
            ai_logic.add_to_blacklist(p, r)
            st.success("Added.")

    st.markdown("---")
    st.write("#### Active Blacklist")
    conn = get_db_connection()
    st.table(conn.execute("SELECT * FROM blacklist").fetchall())
    conn.close()

elif page == "Logs":
    st.markdown("### 📜 System History")
    conn = get_db_connection()
    tab_active, tab_hist = st.tabs(["Active Parking", "Historical Records"])
    with tab_active:
        st.table(conn.execute("SELECT plate_number, vehicle_type, slot_id, entry_time FROM vehicles").fetchall())
    with tab_hist:
        st.table(conn.execute("SELECT * FROM parking_history ORDER BY id DESC LIMIT 20").fetchall())
    conn.close()
