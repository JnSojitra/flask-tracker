from flask import Flask, request, jsonify
from datetime import datetime
import os
import json

app = Flask(__name__)
DATA_FILE = "data/location_data.json"
os.makedirs("data", exist_ok=True)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

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

    all_data = load_data()
    all_data.setdefault(trip_id, []).append(loc_entry)
    save_data(all_data)

    return jsonify({"status": "Location saved"}), 200

@app.route("/api/trip/<trip_id>", methods=["GET"])
def get_trip_location(trip_id):
    all_data = load_data()
    return jsonify(all_data.get(trip_id, []))

@app.route("/api/all", methods=["GET"])
def get_all():
    return jsonify(load_data())

if __name__ == "__main__":
    app.run(debug=True)
