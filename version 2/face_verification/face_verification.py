#face_verification.py

import pymongo
import base64
import numpy as np
import face_recognition
from PIL import Image
from io import BytesIO
import logging

# MongoDB Setup
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["voting_system"]
collection = db["voter_images"]

# Configure Logging
logging.basicConfig(level=logging.DEBUG)

def encode_image(image_data):
    """Convert Base64 to NumPy array"""
    image_bytes = base64.b64decode(image_data.split(",")[1])  # Remove prefix
    image = Image.open(BytesIO(image_bytes))
    return np.array(image)

def verify_voter_face(aadhaar_id, captured_image_data):
    """Checks if the stored face matches the captured face"""
    try:
        # Retrieve stored image from MongoDB
        stored_data = collection.find_one({"aadhaarID": aadhaar_id})
        if not stored_data:
            logging.warning("No registered image found for Aadhaar: %s", aadhaar_id)
            return False

        stored_image_data = stored_data["image"]

        # Convert images to NumPy arrays for face recognition
        captured_image = encode_image(captured_image_data)
        stored_image = encode_image(stored_image_data)

        # Detect face encodings
        captured_encodings = face_recognition.face_encodings(captured_image)
        stored_encodings = face_recognition.face_encodings(stored_image)

        if not captured_encodings or not stored_encodings:
            logging.warning("Face not detected in one or both images")
            return False

        # Compare faces
        match = face_recognition.compare_faces([stored_encodings[0]], captured_encodings[0])[0]
        return match

    except Exception as e:
        logging.error("Error in verify_voter_face: %s", str(e))
        return False
