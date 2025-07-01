from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId  # dùng để convert ObjectId

app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["px4_data"]
telemetry_collection = db["telemetry"]

# API nhận dữ liệu từ drone (MAVSDK)
@app.route('/api/telemetry', methods=['POST'])
def save_telemetry():
    try:
        data = request.get_json()

        # Validate & bổ sung timestamp
        if not data:
            return jsonify({"error": "No data provided"}), 400

        data['timestamp'] = datetime.utcnow()
        telemetry_collection.insert_one(data)
        return jsonify({"status": "saved"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API trả dữ liệu mới nhất (JSON)
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

# Trả về frontend HTML
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
