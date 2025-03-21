from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
from pymongo import MongoClient
from deepface import DeepFace
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voting_system"]
collection = db["voters"]

def calculate_age(dob):
    """Calculate age from Date of Birth (DOB)."""
    dob_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    return age

def decode_base64_image(image_data):
    """Convert Base64 image to OpenCV format (without saving)."""
    try:
        image_data = image_data.split(",")[1]  # Remove Base64 prefix
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print("Error decoding image:", str(e))
        return None

@app.route('/')
def index():
    return render_template("registration.html")

@app.route('/register_voter', methods=["POST"])
def register_voter():
    data = request.json
    aadhaar_id = data.get("aid")
    dob = data.get("dob")
    image_data = data.get("image")

    if not aadhaar_id or not dob or not image_data:
        return jsonify({"status": "error", "message": "Missing Aadhaar ID, DOB, or Image"}), 400

    # Check age eligibility
    age = calculate_age(dob)
    if age < 18:
        return jsonify({"status": "error", "message": "❌ You must be 18 or older to register."})

    try:
        # Convert Base64 to OpenCV Image
        frame = decode_base64_image(image_data)
        if frame is None:
            return jsonify({"status": "error", "message": "❌ Error decoding image."})

        # Generate face encoding directly from image (no saving)
        embedding = DeepFace.represent(frame, model_name="Facenet", enforce_detection=False)
        face_encoding = embedding[0]['embedding']  # Extract 128-D face vector

        # Store voter data in MongoDB
        voter_data = {
            "aadhaar_id": aadhaar_id,
            "dob": dob,
            "age": age,
            "face_encoding": face_encoding
        }
        collection.insert_one(voter_data)

        return jsonify({"status": "success", "message": "✅ Voter Registered Successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Face encoding failed: {str(e)}"})

# Run Flask Server
if __name__ == "__main__":
    app.run(debug=True)
