# Smart Parking Management System with AI

An intelligent parking management solution featuring OCR license plate recognition, predictive analytics, and automated billing.

## Requirements

The system requires Python 3.x and the following libraries:

- `opencv-python-headless`
- `easyocr`
- `numpy`
- `scikit-learn`
- `sqlite3` (built-in with Python)
- `tkinter` (usually built-in with Python)

You can install the dependencies using pip:

```bash
pip install opencv-python-headless easyocr numpy scikit-learn
```

## How to Run

Follow these steps to set up and run the application:

### 1. Initialize the Database
Before running the app for the first time, you must create the database and tables:

```bash
python3 init_db.py
```

### 2. (Optional) Generate Dummy Data
To see the Peak Hour Prediction and other analytics in action immediately, you can generate historical dummy data:

```bash
python3 generate_dummy_data.py
```

### 3. Launch the Application
Start the main GUI:

```bash
python3 main_gui.py
```

## Key Features
- **Operations Tab:** Scan license plates (via image upload or simulation), get slot recommendations, and manage entries/exits.
- **AI Analytics Tab:** Predict peak hours based on history and detect overstaying vehicles.
- **Security Tab:** Manage the blacklist for suspicious vehicle detection.
- **System Logs Tab:** Real-time logging of all system activities.

## AI Report
For a detailed explanation of the AI models used in this project, please refer to [AI_REPORT.md](AI_REPORT.md).
