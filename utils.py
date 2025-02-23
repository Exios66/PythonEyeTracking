import json

def save_gaze_data(file_path, gaze_data):
    with open(file_path, "w") as file:
        json.dump(gaze_data, file)
