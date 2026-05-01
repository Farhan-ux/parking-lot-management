# Wisteria Parking: AI-Powered Smart Parking System (Web Edition)

A beautiful, high-performance web-based parking management solution featuring real-time IPCam license plate recognition, predictive analytics, and a vibrant "Wisteria Bloom" theme.

## Requirements

The system requires Python 3.x and the following libraries:

- `streamlit`
- `opencv-python-headless`
- `easyocr`
- `numpy`
- `scikit-learn`
- `pillow`
- `sqlite3`

You can install the dependencies using pip:

```bash
pip install streamlit opencv-python-headless easyocr numpy scikit-learn pillow
```

## How to Run

### 1. Initialize the Database
```bash
python3 init_db.py
```

### 2. (Optional) Generate Dummy Data
```bash
python3 generate_dummy_data.py
```

### 3. Launch the Application
```bash
streamlit run app.py
```

## Key Features
- **Wisteria Bloom Theme:** A modern, colorful interface with purple and pink gradients.
- **LAN IPCam Integration:** Paste your camera's IP or RTSP link in the sidebar to start live monitoring.
- **CPU-Optimized AI:** Uses lightweight settings for OCR and detection to ensure smooth performance on standard hardware.
- **Smart Operations:** AI-powered slot recommendations, automated billing, and real-time security alerts.
- **Data Analytics:** Peak hour prediction and violation detection models.

## Credits
**Made by Rafay**
