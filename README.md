# Eye Tracking Web App

A real-time **eye tracking web application** built with **Flask, WebSockets, and Heatmaps**.

## 🎯 Features
✅ **Real-time Gaze Tracking** using WebSockets  
✅ **Gaze Heatmaps** to visualize focus points  
✅ **Advanced Calibration** for higher accuracy  
✅ **Download Gaze Data** for analysis  
✅ **Optimized WebSocket Communication** for low latency  

## 🛠️ Installation

## 1️⃣ Clone the repository

```sh
git clone https://github.com/your-repo/eye-tracking-app.git
cd eye-tracking-app
```

## 2️⃣ Create a Virtual Environment (Recommended)

```python
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate  # For Windows
```

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

# 🚀 Running the Application

## 1️⃣ Start the Backend (Flask)

```python
python app.py
```

## 2️⃣ Open the Web App
•	Open index.html in a web browser.

# 🔌 API Endpoints

```markdown
Endpoint	Method	Description
/start-tracking	POST	Starts gaze tracking
/stop-tracking	POST	Stops tracking
/gaze-data	GET	Retrieves gaze data
/update-settings	POST	Updates sensitivity and smoothing
/download-data	GET	Downloads gaze data as JSON
/start-calibration	POST	Starts calibration process
/ws	WebSocket	Streams real-time gaze data
```

# 📜 License

This project is open-source. Modify and use it as needed.
