#verification.py
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
from pymongo import MongoClient
from deepface import DeepFace
from scipy.spatial.distance import cosine  # Cosine similarity function

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voting_system"]
collection = db["voters"]

def decode_base64_image(base64_string):
    """Decode base64 image and convert it to OpenCV format without saving."""
    try:
        image_data = base64.b64decode(base64_string.split(",")[1])  # Remove Base64 prefix
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # Convert to OpenCV format
        return frame  # Return the image as a NumPy array
    except Exception as e:
        print("Error decoding image:", str(e))
        return None

def get_stored_embedding(aadhaar_id):
    """Fetch stored face embedding from MongoDB using Aadhaar ID."""
    user = collection.find_one({"aadhaar_id": aadhaar_id})
    if user and "face_encoding" in user:
        return np.array(user["face_encoding"])  # Convert to numpy array
    return None

def verify_face(stored_embedding, new_image_path):
    """Compare stored face encoding with new image embedding."""
    try:
        # Generate embedding for the new image
        new_embedding = DeepFace.represent(new_image_path, model_name="Facenet", enforce_detection=False)[0]["embedding"]
        new_embedding = np.array(new_embedding)

        # Normalize embeddings
        stored_embedding = stored_embedding / np.linalg.norm(stored_embedding)
        new_embedding = new_embedding / np.linalg.norm(new_embedding)

        # Calculate similarity
        similarity = 1 - cosine(stored_embedding, new_embedding)
        
        return similarity
    except Exception as e:
        print("Error in face verification:", str(e))
        return None

@app.route('/')
def index():
    return render_template('verification.html')

@app.route('/verify', methods=['POST'])
def verify_voter():
    data = request.json
    aadhaar_id = data.get("aadhaarID")
    image_base64 = data.get("image")

    if not aadhaar_id or not image_base64:
        return jsonify({"status": "error", "message": "Aadhaar ID and image are required"}), 400

    stored_embedding = get_stored_embedding(aadhaar_id)
    if stored_embedding is None:
        return jsonify({"status": "error", "message": "No data found for Aadhaar ID"}), 404

    image = decode_base64_image(image_base64)
    if image is None:
        return jsonify({"status": "error", "message": "Invalid image data"}), 400

    similarity_score = verify_face(stored_embedding, image)

    if similarity_score is not None:
        if similarity_score > 0.6:  # Threshold for authentication
            return jsonify({"status": "success", "message": "✅ Face Matched! Authentication Successful."})
        else:
            return jsonify({"status": "error", "message": "❌ Face Mismatch! Authentication Failed."})

    return jsonify({"status": "error", "message": "Error in verification"}), 500

if __name__ == '__main__':
    app.run(debug=True)
