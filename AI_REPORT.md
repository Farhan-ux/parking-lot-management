# AI-Powered Smart Parking Management System Report

## Overview
This project transforms a traditional parking lot into a high-intelligence facility using a suite of seven Deep Learning and Statistical AI models. The system is designed for high accuracy, real-time response, and operational efficiency.

## Implemented AI Models & Architectures

### 1. Advanced Deep Learning ANPR (Automatic Number Plate Recognition)
- **Architecture:** Uses a state-of-the-art pipeline consisting of **CRAFT** (Convolutional Character Region Awareness) for text detection and **CRNN** (Convolutional Recurrent Neural Network) for sequence recognition.
- **Deep Learning Detail:** The model uses ResNet-based feature extraction and an LSTM-based sequence decoder with CTC (Connectionist Temporal Classification) loss for superior accuracy on diverse fonts and lighting conditions.
- **Optimizations:** Implemented custom image pre-processing (Bilateral filtering, Adaptive Thresholding, and Sharpening) to maximize recognition confidence.

### 2. Intelligent Parking Space Recommendation AI
- **Description:** A logic-driven AI that assigns slots based on real-time availability and vehicle classification (Normal, Disabled, VIP, Bike).
- **Benefits:** Ensures optimal space allocation and prioritized access.

### 3. Automated Billing & AI Time Tracking
- **Description:** Automatically calculates parking duration and fees upon vehicle exit by cross-referencing Entry/Exit timestamps recorded by the ANPR system.
- **Benefits:** Removes human error and speeds up throughput.

### 4. Overstay Detection AI
- **Description:** Monitors active sessions and flags vehicles exceeding the allowed duration threshold.
- **Benefits:** Identifies abandoned vehicles and improves lot turnover.

### 5. Statistical Peak Hour Prediction AI
- **Description:** Uses historical data analysis and statistical modeling (frequency distribution) to forecast high-demand periods.
- **Benefits:** Enables predictive staffing and dynamic facility management.

### 6. Computer Vision Fraud Detection (Simulation)
- **Description:** Simulates the detection of parking violations (e.g., parking in no-parking zones or unauthorized VIP slot usage).
- **Benefits:** Provides a blueprint for integrating real-world sensor/camera data for compliance monitoring.

### 7. Integrated Smart Parking System
- **Description:** A unified, web-based control center (built with Streamlit) that centralizes all AI outputs, live IPCam monitoring, and security protocols.

## Technical Stack
- **Interface:** Streamlit (Dynamic Theme Engine: Wisteria/Midnight Bloom)
- **Computer Vision:** OpenCV & Deep Learning-based EasyOCR
- **Database:** SQLite3
- **Data Processing:** NumPy & Scikit-learn
- **Branding:** Made by Rafay

## Conclusion
By moving from traditional OCR to a Deep Learning-based recognition pipeline and implementing predictive analytics, this system offers a professional-grade solution for modern smart city infrastructure.
