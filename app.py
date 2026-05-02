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
st.set_page_config(page_title="Wisteria Smart Parking", layout="wide", page_icon="🌸")

# --- Theme Configuration ---
st.sidebar.title("🎨 Appearance")
theme_mode = st.sidebar.radio("Switch Theme", ["Wisteria Bloom (Light)", "Midnight Bloom (Dark)"])

if theme_mode == "Wisteria Bloom (Light)":
    primary_color = "#6a1b9a"
    bg_gradient = "linear-gradient(135deg, #f3e5f5 0%, #fce4ec 100%)"
    sidebar_bg = "#f8bbd0"
    text_color = "#212121"
    card_bg = "#ffffff"
    btn_bg = "#9c27b0"
    footer_color = "#880e4f"
    input_bg = "#ffffff"
    input_text = "#000000"
else:
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

    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stText, .stMetric label {{
        color: {text_color} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {primary_color} !important;
        font-weight: bold;
    }}

    /* INPUT VISIBILITY */
    input, select, textarea {{
        color: {input_text} !important;
        background-color: {input_bg} !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {text_color} !important;
        background-color: transparent !important;
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
    }}

    div.stMetric, .stTable, div[data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border: 2px solid {primary_color} !important;
        border-radius: 12px;
    }}

    .made-by {{
        position: fixed;
        bottom: 25px;
        left: 20px;
        font-family: 'Comic Sans MS', cursive;
        color: {footer_color};
        font-size: 20px;
        font-weight: 900;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# Initialize DB
if not os.path.exists('parking_system.db'):
    import init_db
    init_db.init_db()

def get_db_connection():
    return sqlite3.connect('parking_system.db')

# Sidebar Content
st.sidebar.image("https://img.icons8.com/color/96/000000/lotus.png")
st.sidebar.markdown(f"### **{theme_mode.split(' ')[0]} Parking**")
page = st.sidebar.radio("Menu", ["Live Monitoring", "Parking Operations", "AI Analytics", "Security", "Logs"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎥 IPCam Setup")
ip_link = st.sidebar.text_input("Stream Link (IP/RTSP)", placeholder="e.g. 192.168.1.50")

# Made by Rafay
st.sidebar.markdown(f'<div class="made-by">Made by Rafay</div>', unsafe_allow_html=True)

st.title(f"🌸 {page}")

if page == "Live Monitoring":
    st.subheader("Automated License Plate Scanner")
    c_left, c_right = st.columns([2, 1])

    with c_left:
        if ip_link:
            st.info(f"Connecting to Stream: {ip_link}")
            run = st.checkbox("Enable Live Feed", value=True)
            FRAME_WIN = st.image([])
            # Use ip_link if provided, else fallback to webcam
            source = ip_link if ip_link else 0
            cap = cv2.VideoCapture(source)
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to fetch stream. Using webcam fallback...")
                    cap = cv2.VideoCapture(0)
                    ret, frame = cap.read()
                    if not ret: break

                if int(time.time() * 10) % 10 == 0:
                    cv2.imwrite("temp_frame.jpg", frame)
                    plate = ai_logic.perform_ocr("temp_frame.jpg")
                    if plate: st.session_state['live_plate'] = plate

                h, w, _ = frame.shape
                cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (255, 0, 255), 3)
                if st.session_state.get('live_plate'):
                    cv2.putText(frame, st.session_state['live_plate'], (w//4, h//4-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
                FRAME_WIN.image(frame, channels="BGR")
            cap.release()
        else:
            st.warning("Configure IPCam in sidebar or use local camera below:")
            img = st.camera_input("Scan Plate")
            if img:
                b = img.getvalue()
                cimg = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                cv2.imwrite("snap.jpg", cimg)
                plate = ai_logic.perform_ocr("snap.jpg")
                st.session_state['live_plate'] = plate
                st.image(cimg, channels="BGR")

    with c_right:
        st.markdown("### 📋 Results")
        curr_plate = st.session_state.get('live_plate', "Scanning...")
        st.success(f"**Detected Plate:** {curr_plate}")
        if curr_plate != "Scanning...":
            sec_msg = ai_logic.is_suspicious(curr_plate)
            if sec_msg: st.error(f"🚨 **ALERT:** {sec_msg}")
            else: st.info("✅ Security: CLEAR")
            if st.button("Move to Entry Gate"):
                st.session_state['entry_plate'] = curr_plate
                st.success("Plate Transferred")

elif page == "Parking Operations":
    t_in, t_out = st.tabs(["🚀 Vehicle Entry", "🚀 Vehicle Exit"])
    with t_in:
        col1, col2 = st.columns(2)
        with col1:
            plat = st.text_input("Vehicle Plate", value=st.session_state.get('entry_plate', ""))
            vtype = st.selectbox("Category", ["Normal", "Disabled", "VIP", "Bike"])
        with col2:
            if st.button("Get AI Recommendation"):
                rec = ai_logic.recommend_parking_slot(vtype)
                st.session_state['rec_slot'] = rec
            # Fixed session state key mismatch
            slat = st.text_input("Target Slot", value=str(st.session_state.get('rec_slot', "")))
        if st.button("Complete Parking"):
            if plat and slat:
                if ai_logic.is_suspicious(plat):
                    st.error(f"🛑 ENTRY DENIED: Vehicle {plat} is blacklisted!")
                else:
                    if parking_lot.park_vehicle(plat, vtype, slat):
                        st.success("Parking Confirmed!")
                        st.balloons()
            else: st.error("Fill required fields")

    with t_out:
        out_plat = st.text_input("Plate to Exit")
        if st.button("Verify & Exit"):
            if ai_logic.is_suspicious(out_plat):
                st.error(f"🛑 EXIT LOCKED: Vehicle {out_plat} has security violations. Contact Admin.")
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
                    st.metric("Amount Due", f"{round(fee, 2)} PKR")
                    st.success(f"Exit cleared for {out_plat}")
                else: st.error("No active session found")
                conn.close()

elif page == "AI Analytics":
    st.markdown("### 📈 Intelligent Insights")
    l, r = st.columns(2)
    with l:
        st.info("Peak Demand Prediction")
        if st.button("Run Forecast"):
            st.metric("Predicted Peak", ai_logic.predict_peak_hours())
    with r:
        st.info("Dynamic Violation Check")
        if st.button("Scan All Cameras"):
            v = ai_logic.detect_wrong_parking()
            if v: st.warning(f"⚠️ {v}")
            else: st.success("Operations Normal")
    st.markdown("---")
    if st.button("Fetch Overstay Reports"):
        st.table(ai_logic.detect_overstays(0.01))

elif page == "Security":
    st.markdown("### 🔒 Security Dashboard")
    bp = st.text_input("Plate Number")
    br = st.text_input("Violation Reason")
    if st.button("Add to Blacklist"):
        ai_logic.add_to_blacklist(bp, br)
        st.success("Database Updated")
    st.markdown("---")
    st.write("#### Active Watchlist")
    conn = get_db_connection()
    st.table(conn.execute("SELECT * FROM blacklist").fetchall())
    conn.close()

elif page == "Logs":
    st.markdown("### 📜 System Logs")
    conn = get_db_connection()
    t_a, t_h = st.tabs(["Active Units", "Archive History"])
    with t_a:
        active_v = conn.execute("SELECT plate_number, vehicle_type, slot_id, entry_time FROM vehicles").fetchall()
        st.table(active_v)
    with t_h:
        hist_v = conn.execute("SELECT * FROM parking_history ORDER BY id DESC LIMIT 20").fetchall()
        st.table(hist_v)
    conn.close()
