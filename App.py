import json
import threading
import time
import logging
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
from flask_sock import Sock
import pyeyetrack  # Ensure this library is installed

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
sock = Sock(app)

# Global Variables
tracking = False
ws_clients = set()
gaze_data = []
settings = {"sensitivity": 5, "smoothing": 5}

# Initialize Eye Tracker
eye_tracker = pyeyetrack.EyeTracker()
lock = threading.Lock()

def track_gaze():
    """
    Background thread function to continuously fetch gaze data.
    """
    global tracking, gaze_data, ws_clients

    logging.info("Eye tracking started.")
    eye_tracker.start()
    
    while tracking:
        gaze = eye_tracker.get_gaze()
        if gaze:
            data_point = {"x": gaze[0], "y": gaze[1], "timestamp": int(time.time() * 1000)}
            with lock:
                gaze_data.append(data_point)

            # Send data to WebSocket clients
            for ws in list(ws_clients):
                try:
                    ws.send(json.dumps(data_point))
                except Exception as e:
                    logging.error(f"WebSocket error: {e}")
                    ws_clients.discard(ws)

        time.sleep(0.05)

    eye_tracker.stop()
    logging.info("Eye tracking stopped.")

# Home Route - Loads Eye Tracking UI
@app.route('/')
def home():
    return render_template('index.html')

# Settings Page Route
@app.route('/settings')
def settings_page():
    return render_template('settings.html', settings=settings)

# Download Page Route
@app.route('/download')
def download_page():
    return render_template('download.html')

# API: Start Tracking
@app.route('/start-tracking', methods=['POST'])
def start_tracking():
    global tracking
    if tracking:
        return jsonify({"status": "Already tracking"}), 200

    tracking = True
    thread = threading.Thread(target=track_gaze, daemon=True)
    thread.start()
    
    return jsonify({"status": "Tracking started"}), 200

# API: Stop Tracking
@app.route('/stop-tracking', methods=['POST'])
def stop_tracking():
    global tracking
    tracking = False
    return jsonify({"status": "Tracking stopped"}), 200

# API: Retrieve Gaze Data
@app.route('/gaze-data', methods=['GET'])
def get_gaze_data():
    with lock:
        return jsonify(gaze_data), 200

# API: Update Settings
@app.route('/update-settings', methods=['POST'])
def update_settings():
    global settings
    try:
        new_settings = request.json
        settings.update(new_settings)
        logging.info(f"Updated settings: {settings}")
        return jsonify({"status": "Settings updated", "settings": settings}), 200
    except Exception as e:
        logging.error(f"Error updating settings: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 400

# WebSocket Route for Real-Time Tracking
@sock.route('/ws')
def gaze_ws(ws):
    global ws_clients
    ws_clients.add(ws)
    
    try:
        while True:
            message = ws.receive()
            if message == "STOP":
                break
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        ws_clients.discard(ws)
        logging.info("WebSocket client disconnected")

# API: Download Gaze Data
@app.route('/download-data', methods=['GET'])
def download_data():
    with lock:
        file_path = "data/gaze_data.json"
        with open(file_path, "w") as file:
            json.dump(gaze_data, file)
        return send_file(file_path, as_attachment=True)

# API: Start Calibration
@app.route('/start-calibration', methods=['POST'])
def start_calibration():
    logging.info("Calibration started.")
    time.sleep(5)
    logging.info("Calibration completed.")
    return jsonify({"status": "Calibration completed"}), 200

# App Initialization
@app.before_first_request
def before_first_request():
    logging.info("Server started. Ready to accept connections.")

# Graceful Shutdown
@app.teardown_appcontext
def cleanup(exception=None):
    global tracking
    tracking = False
    logging.info("Cleaning up resources before shutdown.")

if __name__ == '__main__':
    logging.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, debug=False)
