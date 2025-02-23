import json
import threading
import time
import logging
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_sock import Sock
import pyeyetrack  # Ensure this library is installed
import os

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
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

@app.route('/start-tracking', methods=['POST'])
def start_tracking():
    """
    Start eye tracking and initiate background tracking thread.
    """
    global tracking
    if tracking:
        return jsonify({"status": "Already tracking"}), 200

    tracking = True
    thread = threading.Thread(target=track_gaze, daemon=True)
    thread.start()
    
    return jsonify({"status": "Tracking started"}), 200

@app.route('/stop-tracking', methods=['POST'])
def stop_tracking():
    """
    Stop eye tracking.
    """
    global tracking
    tracking = False
    return jsonify({"status": "Tracking stopped"}), 200

@app.route('/gaze-data', methods=['GET'])
def get_gaze_data():
    """
    Retrieve all gaze tracking data collected so far.
    """
    with lock:
        return jsonify(gaze_data), 200

@app.route('/update-settings', methods=['POST'])
def update_settings():
    """
    Update tracking settings like sensitivity and smoothing.
    """
    global settings
    try:
        new_settings = request.json
        settings.update(new_settings)
        logging.info(f"Updated settings: {settings}")
        return jsonify({"status": "Settings updated", "settings": settings}), 200
    except Exception as e:
        logging.error(f"Error updating settings: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 400

@sock.route('/ws')
def gaze_ws(ws):
    """
    WebSocket route for real-time gaze data streaming.
    """
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

@app.route('/download-data', methods=['GET'])
def download_data():
    """
    Allow users to download gaze data as JSON.
    """
    with lock:
        file_path = "gaze_data.json"
        with open(file_path, "w") as file:
            json.dump(gaze_data, file)
        return send_file(file_path, as_attachment=True)

@app.route('/start-calibration', methods=['POST'])
def start_calibration():
    """
    Simulate calibration sequence.
    """
    logging.info("Calibration started.")
    time.sleep(5)
    logging.info("Calibration completed.")
    return jsonify({"status": "Calibration completed"}), 200

@app.before_first_request
def before_first_request():
    """
    Function to run before the first request.
    """
    logging.info("Server started. Ready to accept connections.")

@app.teardown_appcontext
def cleanup(exception=None):
    """
    Graceful shutdown and cleanup.
    """
    global tracking
    tracking = False
    logging.info("Cleaning up resources before shutdown.")

if __name__ == '__main__':
    logging.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, debug=False)
