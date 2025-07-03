from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId 
from uuid import uuid4

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["px4_data"]
telemetry_collection = db["telemetry"]


@app.route('/api/telemetry', methods=['POST'])
def save_telemetry():
    try:
        data = request.get_json()

        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        data['timestamp'] = datetime.utcnow()
        telemetry_collection.insert_one(data)
        return jsonify({"status": "saved"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    try:
        records = telemetry_collection.find().sort("timestamp", -1).limit(10)
        result = []
        for r in records:
            r['_id'] = str(r['_id'])  # convert ObjectId -> string
            r['timestamp'] = r['timestamp'].isoformat()  # convert datetime -> string
            result.append(r)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/missions', methods=['POST'])
def create_mission():
    try:
        data = request.get_json()

        required = ['start_point', 'end_point', 'sequence_waypoint']
        if not all(k in data for k in required):
            return jsonify({"error": "Thiếu thông tin mission"}), 400

        mission = {
            "id": str(uuid4()),
            "status": "planned",
            "error": None,
            "created_at": datetime.utcnow(),
            "finished_at": None,
            "start_point": data["start_point"],
            "end_point": data["end_point"],
            "sequence_waypoint": data["sequence_waypoint"],
            "altitude": data.get("altitude", 10.0)
        }

        db["missions"].insert_one(mission)
        return jsonify({"status": "created", "mission_id": mission["id"]}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/missions/<mission_id>', methods=['GET'])
def get_mission(mission_id):
    try:
        mission = db["missions"].find_one({"id": mission_id})
        if not mission:
            return jsonify({"error": "Mission not found"}), 404

        mission['_id'] = str(mission['_id'])
        mission['created_at'] = mission['created_at'].isoformat()
        if mission['finished_at']:
            mission['finished_at'] = mission['finished_at'].isoformat()

        return jsonify(mission)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/missions', methods=['GET'])
def list_missions():
    try:
        status = request.args.get('status')
        query = {"status": status} if status else {}

        missions = db["missions"].find(query).sort("created_at", -1)
        result = []
        for m in missions:
            m['_id'] = str(m['_id'])
            m['created_at'] = m['created_at'].isoformat()
            if m['finished_at']:
                m['finished_at'] = m['finished_at'].isoformat()
            result.append(m)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/missions/<mission_id>/status', methods=['PUT'])
def update_mission_status(mission_id):
    try:
        data = request.get_json()
        new_status = data.get("status")
        if not new_status:
            return jsonify({"error": "Missing new status"}), 400

        update = { "status": new_status }
        if new_status in ["completed", "failed"]:
            update["finished_at"] = datetime.utcnow()
        if "error" in data:
            update["error"] = data["error"]

        result = db["missions"].update_one({"id": mission_id}, {"$set": update})
        if result.matched_count == 0:
            return jsonify({"error": "Mission not found"}), 404

        return jsonify({"status": "updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/missions/<mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    try:
        result = db["missions"].delete_one({"id": mission_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Mission not found"}), 404
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 5. Giao diện nhập mission và xem log (optional)
@app.route('/missions')
def mission_page():
    return render_template("missions.html") 


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
