from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from pymongo import MongoClient
import requests
import os

app = Flask(__name__)
CORS(app)

# -------------------- MONGODB --------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client["animals_watchlist"]
users_collection = db["users"]

# -------------------- PET SERVICE --------------------
PET_SERVICE_URL = os.environ.get("PET_SERVICE_URL", "http://pet_service:5006")

# -------------------- FRONTEND --------------------
@app.route('/')
def serve_index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    file_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.exists(file_path):
        return send_from_directory(os.path.dirname(__file__), path)
    return send_from_directory(os.path.dirname(__file__), 'index.html')


# -------------------- AUTH --------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400

    result = users_collection.insert_one({"username": username, "password": password})
    return jsonify({"status": "success", "user_id": str(result.inserted_id), "username": username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return jsonify({"status": "success", "user_id": str(user["_id"]), "username": username}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# -------------------- PET PROXY --------------------
@app.route('/pets', methods=['POST'])
def add_pet_proxy():
    data = request.json
    try:
        resp = requests.post(f"{PET_SERVICE_URL}/pets", json=data, timeout=5)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error connecting to Pet Service: {str(e)}"}), 500

@app.route('/pets/<username>', methods=['GET'])
def get_pets_proxy(username):
    try:
        resp = requests.get(f"{PET_SERVICE_URL}/pets/{username}", timeout=5)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching pets: {str(e)}"}), 500

@app.route('/pets/<pet_id>', methods=['DELETE'])
def delete_pet_proxy(pet_id):
    try:
        resp = requests.delete(f"{PET_SERVICE_URL}/pets/{pet_id}", timeout=5)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error deleting pet: {str(e)}"}), 500

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
