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
        font-family: 'Segoe UI', Arial, sans-serif;
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

    /* SCROLLING FOOTER IN SIDEBAR */
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

def get_db_connection():
    return sqlite3.connect('parking_system.db')

# Sidebar Content
st.sidebar.image("https://img.icons8.com/color/96/000000/lotus.png")
st.sidebar.markdown(f"### **{theme_mode.split(' ')[0]} Parking**")
page = st.sidebar.radio("Menu", ["Live Monitoring", "Parking Operations", "AI Analytics", "Security", "Logs"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎥 IPCam Setup")
ip_link = st.sidebar.text_input("Stream Link (IP/RTSP)", placeholder="e.g. 192.168.1.50")

# Made by Rafay Branding (Moved to end of sidebar flow)
st.sidebar.markdown("---")
st.sidebar.markdown(f'<div class="made-by">Made by Rafay</div>', unsafe_allow_html=True)

st.title(f"🌸 {page}")

if page == "Live Monitoring":
    st.subheader("High-Accuracy Two-Stage CNN Scanner")
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
                if not ret: break
                if int(time.time() * 10) % 10 == 0:
                    cv2.imwrite("dl_frame.jpg", frame)
                    plate = ai_logic.perform_ocr("dl_frame.jpg")
                    if plate: st.session_state['live_plate'] = plate

                h, w, _ = frame.shape
                cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (255, 0, 255), 3)
                if st.session_state.get('live_plate'):
                    cv2.putText(frame, st.session_state['live_plate'], (w//4, h//4-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
                FRAME_WIN.image(frame, channels="BGR")
            cap.release()
        else:
            st.warning("Connect IPCam in sidebar or use local camera:")
            img = st.camera_input("Take Photo of Plate")
            if img:
                b = img.getvalue()
                cimg = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)
                cv2.imwrite("dl_snap.jpg", cimg)
                plate = ai_logic.perform_ocr("dl_snap.jpg")
                st.session_state['live_plate'] = plate
                st.image(cimg, channels="BGR")

    with c_right:
        st.markdown("### 🔍 Two-Stage Detection")
        curr_plate = st.session_state.get('live_plate', "Waiting...")

        if curr_plate == "Waiting...":
            st.write("Awaiting visual input from camera...")
        else:
            st.success(f"**Plate Found:** {curr_plate}")
            sec_msg = ai_logic.is_suspicious(curr_plate)
            if sec_msg: st.error(f"🚨 **ALERT:** {sec_msg}")
            else: st.info("✅ Security Status: CLEAR")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Move to Entry Gate"):
                    st.session_state['entry_plate'] = curr_plate
                    st.success("Plate Registered")
            with col_b2:
                if st.button("Clear / Retry"):
                    st.session_state['live_plate'] = "Waiting..."
                    st.rerun()

            if st.button("🚨 Blacklist This Vehicle"):
                ai_logic.add_to_blacklist(curr_plate, "Manual Intelligence Alert")
                st.warning(f"Vehicle {curr_plate} blacklisted!")
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
                    st.error(f"🛑 ENTRY DENIED: Vehicle {plat} is on the security watchlist!")
                else:
                    if parking_lot.park_vehicle(plat, vtype, slat):
                        st.success(f"Parking sequence complete for {plat}")
                        st.balloons()
            else: st.error("Please provide plate and slot details")

    with t_out:
        out_plat = st.text_input("Exit License Plate")
        if st.button("Check-out & Billing"):
            if ai_logic.is_suspicious(out_plat):
                st.error(f"🛑 EXIT LOCKED: Vehicle {out_plat} has pending security issues.")
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
                    st.metric("Total Fee", f"{round(fee, 2)} PKR", delta=f"{round(hrs, 2)} hrs")
                    st.success(f"Vehicle {out_plat} successfully exited")
                else: st.error("No active parking record found for this plate")
                conn.close()

elif page == "AI Analytics":
    st.markdown("### 📊 Smart Facility Insights")
    l, r = st.columns(2)
    with l:
        st.info("Peak Demand Forecasting")
        if st.button("Run Prediction Model"):
            st.metric("Predicted Peak Hour", ai_logic.predict_peak_hours())
    with r:
        st.info("Dynamic Violation Check")
        if st.button("Simulate AI Scan"):
            v = ai_logic.detect_wrong_parking()
            if v: st.warning(f"⚠️ AI Alert: {v}")
            else: st.success("No violations detected currently")
    st.markdown("---")
    if st.button("Refresh Overstay Alerts"):
        st.table(ai_logic.detect_overstays(0.01))

elif page == "Security":
    st.markdown("### 🔒 Security & Watchlist Management")
    bp = st.text_input("Plate to Flag")
    br = st.text_input("Reason for Watchlist")
    if st.button("Add to Security Blacklist"):
        ai_logic.add_to_blacklist(bp, br)
        st.success("Vehicle blacklisted and security protocols updated")
    st.markdown("---")
    st.write("#### Active Security Watchlist")
    conn = get_db_connection()
    st.table(conn.execute("SELECT * FROM blacklist").fetchall())
    conn.close()

elif page == "Logs":
    st.markdown("### 📜 System Event Records")
    conn = get_db_connection()
    t_a, t_h = st.tabs(["Currently Parked Units", "Archive History (AI Learning Data)"])
    with t_a:
        st.table(conn.execute("SELECT plate_number, vehicle_type, slot_id, entry_time FROM vehicles").fetchall())
    with t_h:
        st.table(conn.execute("SELECT * FROM parking_history ORDER BY id DESC LIMIT 20").fetchall())
    conn.close()
