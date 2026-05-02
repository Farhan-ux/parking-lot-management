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
from database import get_db_connection

# Page Configuration
st.set_page_config(page_title="Wisteria Smart Parking", layout="wide", page_icon="🌸")

# Initialize Session State
if 'live_plate' not in st.session_state:
    st.session_state['live_plate'] = "Waiting..."

# --- Theme Configuration ---
# Theme is fixed to Midnight Bloom (Dark) as per user request
primary_color = "#e1bee7"
bg_gradient = "linear-gradient(135deg, #0d001a 0%, #1a237e 100%)"
sidebar_bg = "#000051"
text_color = "#ffffff"
card_bg = "#121212"
btn_bg = "#7b1fa2"
footer_color = "#f48fb1"
input_bg = "#262730"
input_text = "#ffffff"

st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_gradient};
        color: {text_color} !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 3px solid {primary_color};
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stText, .stMetric label, .stChatMessage {{
        color: {text_color} !important;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 600 !important;
    }}

    /* Force Camera Input Button Visibility */
    [data-testid="stCameraInputButton"] {{
        background-color: {primary_color} !important;
        color: white !important;
        border: 2px solid white !important;
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {primary_color} !important;
        font-weight: bold;
    }}

    input, select, textarea {{
        color: {input_text} !important;
        background-color: {input_bg} !important;
        border: 1px solid {primary_color} !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}

    button[data-testid="baseButton-secondary"] {{
        background-color: {primary_color} !important;
        color: white !important;
        border: 2px solid white !important;
        font-weight: bold !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {text_color} !important;
        background-color: transparent !important;
        font-weight: 700 !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {primary_color} !important;
    }}

    .stButton>button {{
        background-color: {btn_bg};
        color: white !important;
        border-radius: 25px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-weight: 900;
        text-transform: uppercase;
    }}

    div.stMetric, .stTable, div[data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border: 2px solid {primary_color} !important;
        border-radius: 12px;
    }}

    .made-by {{
        margin-top: 50px;
        font-family: 'Comic Sans MS', cursive;
        color: {footer_color};
        font-size: 24px;
        font-weight: 900;
        text-align: center;
        width: 100%;
        display: block;
        padding-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Initialize DB
if not os.path.exists('parking_system.db'):
    import init_db
    init_db.init_db()

# Sidebar Content
st.sidebar.image("https://img.icons8.com/color/96/000000/lotus.png")
st.sidebar.markdown(f"### **Midnight Parking**")
page = st.sidebar.radio("Menu", ["Live Monitoring", "Parking Operations", "AI Analytics", "Security", "Logs"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎥 IPCam Setup")
ip_link = st.sidebar.text_input("Stream Link (IP/RTSP)", placeholder="e.g. 192.168.1.50")

# Made by Rafay Branding
st.sidebar.markdown("---")
st.sidebar.markdown(f'<div class="made-by">Made by Rafay</div>', unsafe_allow_html=True)

st.title(f"🌸 {page}")

if page == "Live Monitoring":
    st.subheader("Two-Stage Deep Learning Scanner")
    c_left, c_right = st.columns([2, 1])

    with c_left:
        if ip_link:
            st.info(f"Connecting to Stream: {ip_link}")
            run = st.checkbox("Enable Live Feed", value=True)
            FRAME_WIN = st.image([])
            source = ip_link if ip_link else 0
            cap = cv2.VideoCapture(source)
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to fetch stream. Falling back to primary camera...")
                    cap = cv2.VideoCapture(0)
                    ret, frame = cap.read()
                    if not ret: break

                # Run OCR every few frames
                if int(time.time() * 5) % 5 == 0:
                    cv2.imwrite("dl_frame.jpg", frame)
                    plate, box = ai_logic.perform_ocr("dl_frame.jpg", return_box=True)
                    if plate:
                        st.session_state['live_plate'] = plate
                        # Automate: if high confidence plate found, transfer it
                        st.session_state['entry_plate'] = plate
                    if box:
                        st.session_state['last_box'] = box

                h, w, _ = frame.shape
                if 'last_box' in st.session_state and st.session_state['last_box']:
                    xmin, xmax, ymin, ymax = st.session_state['last_box']
                    cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 3)
                else:
                    cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (255, 0, 255), 2)

                if st.session_state.get('live_plate') and st.session_state['live_plate'] != "Waiting...":
                    msg = f"DETECTED: {st.session_state['live_plate']}"
                    cv2.putText(frame, msg, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

                FRAME_WIN.image(frame, channels="BGR")
            cap.release()
        else:
            st.warning("Connect IPCam in sidebar or use local camera:")
            img = st.camera_input("Scan License Plate")
            if img:
                b = img.getvalue()
                cimg = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                cv2.imwrite("dl_snap.jpg", cimg)
                plate = ai_logic.perform_ocr("dl_snap.jpg")
                if plate:
                    st.session_state['live_plate'] = plate
                else:
                    st.session_state['live_plate'] = "No text detected"
                st.image(cimg, channels="BGR")

    with c_right:
        st.markdown("### 🔍 Results")

        # Enable manual editing of the detected plate
        curr_plate = st.text_input("Detected Plate (Edit if wrong)", value=st.session_state['live_plate'])

        if curr_plate == "Waiting...":
            st.write("Awaiting camera input...")
        else:
            st.success(f"**AI Result:** {curr_plate}")

            sec_msg = ai_logic.is_suspicious(curr_plate)
            if sec_msg: st.error(f"🚨 **ALERT:** {sec_msg}")
            elif curr_plate != "No text detected": st.info("✅ Security: CLEAR")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Move to Gate"):
                    st.session_state['entry_plate'] = curr_plate
                    st.success("Transferred")
            with col_b2:
                if st.button("Clear / Retry"):
                    st.session_state['live_plate'] = "Waiting..."
                    # Remove the transfer session state too if user wants full retry
                    if 'entry_plate' in st.session_state: del st.session_state['entry_plate']
                    st.rerun()

            if curr_plate != "No text detected" and st.button("🚨 Blacklist Vehicle"):
                ai_logic.add_to_blacklist(curr_plate, "Intelligence Alert")
                st.warning(f"Blacklisted!")
                st.rerun()

elif page == "Parking Operations":
    t_in, t_out = st.tabs(["🚀 Vehicle Entry", "🚀 Vehicle Exit"])
    with t_in:
        col1, col2 = st.columns(2)
        with col1:
            plat = st.text_input("License Plate", value=st.session_state.get('entry_plate', ""))
            vtype = st.selectbox("Vehicle Class", ["Normal", "Disabled", "VIP", "Bike"])
        with col2:
            if st.button("AI Recommendation"):
                rec = ai_logic.recommend_parking_slot(vtype)
                st.session_state['rec_slot'] = rec
            slat = st.text_input("Assigned Slot", value=str(st.session_state.get('rec_slot', "")))
        if st.button("Process Entry"):
            if plat and slat:
                if ai_logic.is_suspicious(plat):
                    st.error(f"🛑 ENTRY DENIED: Vehicle {plat} is blacklisted!")
                else:
                    if parking_lot.park_vehicle(plat, vtype, slat):
                        st.success(f"Parking complete for {plat}")
                        st.balloons()
            else: st.error("Fill all details")

    with t_out:
        out_plat = st.text_input("Exit License Plate")
        if st.button("Check-out & Billing"):
            if ai_logic.is_suspicious(out_plat):
                st.error(f"🛑 EXIT LOCKED: Security issues pending.")
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, entry_time FROM vehicles WHERE plate_number=?", (out_plat,))
                res = cursor.fetchone()
                if res:
                    v_id, e_time = res
                    hrs = max(1, (datetime.datetime.now() - datetime.datetime.strptime(e_time, '%Y-%m-%d %H:%M:%S')).total_seconds()/3600)
                    fee = parking_lot.calculate_fee(hrs)
                    parking_lot.remove_parked_vehicle(v_id, hrs)
                    st.metric("Total Fee", f"{round(fee, 2)} PKR")
                    st.success(f"Exit cleared.")
                else: st.error("No active record")
                conn.close()

elif page == "AI Analytics":
    st.markdown("### 📊 Smart Insights")
    l, r = st.columns(2)
    with l:
        st.info("Peak Demand Forecasting")
        if st.button("Run Model"):
            st.metric("Predicted Peak", ai_logic.predict_peak_hours())
    with r:
        st.info("Violation Detection")
        if st.button("Scan Cameras"):
            v = ai_logic.detect_wrong_parking()
            if v: st.warning(f"⚠️ AI Alert: {v}")
            else: st.success("Operations Normal")
    st.markdown("---")
    if st.button("Refresh Overstays"):
        st.table(ai_logic.detect_overstays(0.01))

elif page == "Security":
    st.markdown("### 🔒 Security Watchlist")
    bp = st.text_input("Plate Number")
    br = st.text_input("Violation Reason")
    if st.button("Add to Blacklist"):
        ai_logic.add_to_blacklist(bp, br)
        st.success("Updated")
    st.markdown("---")
    conn = get_db_connection()
    st.table(conn.execute("SELECT * FROM blacklist").fetchall())
    conn.close()

elif page == "Logs":
    st.markdown("### 📜 System Event Records")
    conn = get_db_connection()
    t_a, t_h = st.tabs(["Active Units", "Archive History"])
    with t_a: st.table(conn.execute("SELECT plate_number, vehicle_type, slot_id, entry_time FROM vehicles").fetchall())
    with t_h: st.table(conn.execute("SELECT * FROM parking_history ORDER BY id DESC LIMIT 20").fetchall())
    conn.close()
