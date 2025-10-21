from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client["animals_watchlist"]
pets_collection = db["pets"]

# ----------------- CREATE -----------------
@app.route('/pets', methods=['POST'])
def add_pet():
    data = request.json
    username = data.get("username")
    name = data.get("name")
    type_ = data.get("type")
    age = data.get("age")

    pet_doc = {"username": username, "name": name, "type": type_, "age": age}
    result = pets_collection.insert_one(pet_doc)
    return jsonify({"message": f"Pet '{name}' added!", "_id": str(result.inserted_id)}), 201

# ----------------- READ -----------------
@app.route('/pets/<username>', methods=['GET'])
def get_pets(username):
    pets = pets_collection.find({"username": username})
    pet_list = []
    for p in pets:
        pet_list.append({"_id": str(p["_id"]), "name": p["name"], "type": p["type"], "age": p["age"]})
    return jsonify({"pets": pet_list}), 200

# ----------------- DELETE -----------------
@app.route('/pets/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    try:
        result = pets_collection.delete_one({"_id": ObjectId(pet_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Pet not found"}), 404
        return jsonify({"message": "Pet deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
