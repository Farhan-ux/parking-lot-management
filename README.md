# Smart Parking Management System with AI (Web Edition)

An intelligent, modern web-based parking management solution featuring real-time OCR license plate recognition, predictive analytics, and automated billing.

## Requirements

The system requires Python 3.x and the following libraries:

- `streamlit`
- `streamlit-webrtc`
- `opencv-python-headless`
- `easyocr`
- `numpy`
- `scikit-learn`
- `pillow`
- `aiortc`
- `av`
- `sqlite3` (built-in with Python)

You can install all dependencies using pip:

```bash
pip install streamlit streamlit-webrtc opencv-python-headless easyocr numpy scikit-learn pillow aiortc av
```

## How to Run

Follow these steps to set up and run the application:

### 1. Initialize the Database
Create the database and tables:

```bash
python3 init_db.py
```

### 2. (Optional) Generate Dummy Data
To populate the system with historical data for AI prediction:

```bash
python3 generate_dummy_data.py
```

### 3. Launch the Web Application
Start the Streamlit app:

```bash
streamlit run app.py
```

## Key Features
- **Live Monitoring:** Real-time IPCam feed using `streamlit-webrtc`. AI automatically detects license plates and checks against the blacklist.
- **Parking Operations:** Unified entry/exit management with AI-powered slot recommendations and automatic fee calculation.
- **AI Analytics:** Peak hour prediction using historical trends and simulated fraud/wrong-parking detection.
- **Security:** Manage blacklisted vehicles with real-time alerting.
- **Logs:** View active vehicles and historical parking records.

## AI Report
For a detailed explanation of the AI models used in this project, please refer to [AI_REPORT.md](AI_REPORT.md).
