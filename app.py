import streamlit as st
import cv2
import numpy as np
from PIL import Image
import datetime
import os
import ai_logic
import parking_lot
import sqlite3
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# Page Configuration
st.set_page_config(page_title="Smart Parking AI", layout="wide", page_icon="🚗")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize DB
if not os.path.exists('parking_system.db'):
    import init_db
    init_db.init_db()

def get_db_connection():
    return sqlite3.connect('parking_system.db')

# --- Video Processor for Real-time OCR ---
class PlateDetector(VideoProcessorBase):
    def __init__(self):
        self.last_plate = ""
        self.frame_count = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1

        # Every 30 frames, attempt OCR
        if self.frame_count % 30 == 0:
            temp_p = "stream_snap.jpg"
            cv2.imwrite(temp_p, img)
            self.last_plate = ai_logic.perform_ocr(temp_p)

        # Draw overlay
        h, w, _ = img.shape
        cv2.rectangle(img, (w//4, h//4), (3*w//4, 3*h//4), (255, 0, 0), 2)
        if self.last_plate:
            cv2.putText(img, f"Detected: {self.last_plate}", (w//4, h//4 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        return frame.from_ndarray(img, format="bgr24")

# Sidebar
st.sidebar.image("https://img.icons8.com/clouds/100/000000/car.png")
st.sidebar.title("Smart Parking AI")
page = st.sidebar.radio("Navigation", ["Live Monitoring", "Parking Operations", "AI Analytics", "Security", "Logs"])

st.title(f"🚘 {page}")

if page == "Live Monitoring":
    st.subheader("Live IPCam Stream & Auto-Detection")
    ctx = webrtc_streamer(key="plate-detector", video_processor_factory=PlateDetector)

    if ctx.video_processor:
        plate = ctx.video_processor.last_plate
        if plate:
            st.success(f"Latest Detected Plate: **{plate}**")
            reason = ai_logic.is_suspicious(plate)
            if reason:
                st.error(f"🛑 SECURITY ALERT: {reason}")

            if st.button("Use this plate for Entry"):
                st.session_state['entry_plate'] = plate
                st.info("Plate saved. Go to Parking Operations tab.")

elif page == "Parking Operations":
    t1, t2 = st.tabs(["Entry", "Exit"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            p_in = st.text_input("Plate Number", value=st.session_state.get('entry_plate', ""))
            v_type = st.selectbox("Vehicle Type", ["Normal", "Disabled", "VIP", "Bike"])
        with c2:
            if st.button("Auto-Recommend Slot"):
                rec = ai_logic.recommend_parking_slot(v_type)
                st.session_state['rec_slot'] = rec
            s_in = st.text_input("Slot Number", value=str(st.session_state.get('rec_slot', "")))

        if st.button("Park Vehicle"):
            if p_in and s_in:
                if parking_lot.park_vehicle(p_in, v_type, s_in):
                    st.success(f"Parked {p_in} in {s_in}")
                    st.balloons()

    with t2:
        p_out = st.text_input("Plate Number to Exit")
        if st.button("Check-out & Pay"):
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
                st.write(f"### Fee: {round(fee, 2)} PKR")
                st.write(f"Duration: {round(hours, 2)} hours")
                st.success("Vehicle removed.")
            else:
                st.error("Not found")
            conn.close()

elif page == "AI Analytics":
    col1, col2 = st.columns(2)
    with col1:
        st.info("Peak Hour Prediction")
        if st.button("Run AI Model"):
            st.metric("Predicted Peak", ai_logic.predict_peak_hours())
    with col2:
        st.info("Fraud Detection")
        if st.button("Simulate Camera Scan"):
            violation = ai_logic.detect_wrong_parking()
            if violation: st.warning(violation)
            else: st.success("No violations")

    st.markdown("---")
    if st.button("Refresh Overstay List"):
        st.table(ai_logic.detect_overstays(0.01))

elif page == "Security":
    st.subheader("Manage Blacklist")
    p = st.text_input("Plate")
    r = st.text_input("Reason")
    if st.button("Add"):
        ai_logic.add_to_blacklist(p, r)

    conn = get_db_connection()
    st.table(conn.execute("SELECT * FROM blacklist").fetchall())
    conn.close()

elif page == "Logs":
    conn = get_db_connection()
    st.write("### Active Vehicles")
    st.table(conn.execute("SELECT * FROM vehicles").fetchall())
    st.write("### History")
    st.table(conn.execute("SELECT * FROM parking_history ORDER BY id DESC LIMIT 20").fetchall())
    conn.close()
