# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)  


# 1. Database Connection 

client = MongoClient("mongodb+srv://admin:Aman%402005@cluster0.zixkaen.mongodb.net/?appName=Cluster0")
db = client["roboconDB"]
robots_collection = db["robots"]

print("Connected to MongoDB successfully!")

def serialize_doc(doc):
    doc['_id'] = str(doc['_id'])
    return doc

#  2. API Endpoints (CRUD)

# CREATE (POST) 
@app.route('/api/robots', methods=['POST'])
def create_robot():
    data = request.json

    if not data or 'name' not in data or 'type' not in data:
        return jsonify({"error": "Missing required fields: name, type"}), 400
    
    try:
        new_robot = {
            "name": data['name'],
            "type": data['type'],
            "status": data.get('status', 'Active')
        }
        result = robots_collection.insert_one(new_robot)
        new_robot['_id'] = str(result.inserted_id)
        return jsonify(new_robot), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# READ ALL (GET)
@app.route('/api/robots', methods=['GET'])
def get_robots():
    try:
        robots = list(robots_collection.find())
        return jsonify([serialize_doc(robot) for robot in robots]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UPDATE (PUT)
@app.route('/api/robots/<id>', methods=['PUT'])
def update_robot(id):
    data = request.json
    try:
        
        updated_robot = robots_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True
        )
        if updated_robot:
            return jsonify(serialize_doc(updated_robot)), 200
        else:
            return jsonify({"error": "Robot not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format or server error"}), 500

# DELETE (DELETE) 
@app.route('/api/robots/<id>', methods=['DELETE'])
def delete_robot(id):
    try:
        result = robots_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Robot deleted successfully"}), 200
        else:
            return jsonify({"error": "Robot not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format or server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
