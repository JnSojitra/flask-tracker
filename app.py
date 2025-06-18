from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# Paths
TRIP_FILE = "data/trips.json"
DATA_FILE = "data/location_data.json"
STATIC_FOLDER = "."

# Ensure data folder & files exist
os.makedirs("data", exist_ok=True)
for file in [TRIP_FILE, DATA_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

# Utils
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Routes
@app.route("/")
def home():
    return "✅ Flask Tracking Server is Running!"

@app.route("/admin")
def admin_ui():
    return send_file("admin.html")

@app.route("/track.html")
def track_page():
    return send_file("track.html")

@app.route("/manifest.json")
def manifest():
    return send_from_directory(STATIC_FOLDER, "manifest.json")

@app.route("/sw.js")
def service_worker():
    return send_from_directory(STATIC_FOLDER, "sw.js")

@app.route("/api/create_trip", methods=["POST"])
def create_trip():
    data = request.json
    trip_id = data.get("tripId")
    vehicle = data.get("vehicle")
    driver = data.get("driver")
    if not trip_id:
        return jsonify({"error": "Trip ID is required"}), 400
    trips = load_json(TRIP_FILE)
    trips[trip_id] = {
        "vehicle": vehicle,
        "driver": driver,
        "start_time": datetime.utcnow().isoformat(),
        "active": True
    }
    save_json(TRIP_FILE, trips)
    return jsonify({"status": "Trip created"}), 200

@app.route("/api/stop_trip/<trip_id>", methods=["POST"])
def stop_trip(trip_id):
    trips = load_json(TRIP_FILE)
    if trip_id in trips:
        trips[trip_id]["active"] = False
        trips[trip_id]["end_time"] = datetime.utcnow().isoformat()
        save_json(TRIP_FILE, trips)
        return jsonify({"status": "Trip ended"}), 200
    return jsonify({"error": "Trip not found"}), 404

@app.route("/api/trips", methods=["GET"])
def get_trips():
    return jsonify(load_json(TRIP_FILE))

@app.route("/api/location", methods=["POST"])
def receive_location():
    data = request.json
    trip_id = data.get("tripId")
    if not trip_id:
        return jsonify({"error": "Trip ID missing"}), 400

    loc_entry = {
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
    }
    all_data = load_json(DATA_FILE)
    all_data.setdefault(trip_id, []).append(loc_entry)
    save_json(DATA_FILE, all_data)

    return jsonify({"status": "Location saved"}), 200

@app.route("/api/trip/<trip_id>", methods=["GET"])
def get_trip_location(trip_id):
    all_data = load_json(DATA_FILE)
    return jsonify(all_data.get(trip_id, []))

@app.route("/api/all", methods=["GET"])
def get_all():
    return jsonify(load_json(DATA_FILE))

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
