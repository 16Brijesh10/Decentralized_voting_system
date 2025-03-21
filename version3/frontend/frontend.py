#frontend.py
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
import json
import logging
import cv2
import numpy as np
import base64
from pymongo import MongoClient
from deepface import DeepFace
from scipy.spatial.distance import cosine

backend_addr = "http://127.0.0.1:80/"

app = Flask(__name__)
app.secret_key = 'i love white chocolate'

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voting_system"]
collection = db["voters"]

logging.basicConfig(level=logging.DEBUG)

# Face verification helper functions
def decode_base64_image(base64_string):
    try:
        image_data = base64.b64decode(base64_string.split(",")[1])
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        logging.error("Error decoding image: %s", e)
        return None

def get_stored_embedding(aadhaar_id):
    user = collection.find_one({"aadhaar_id": aadhaar_id})
    if user and "face_encoding" in user:
        return np.array(user["face_encoding"])
    return None

def verify_face(stored_embedding, new_image):
    try:
        new_embedding = DeepFace.represent(new_image, model_name="Facenet", enforce_detection=False)[0]["embedding"]
        new_embedding = np.array(new_embedding)
        stored_embedding = stored_embedding / np.linalg.norm(stored_embedding)
        new_embedding = new_embedding / np.linalg.norm(new_embedding)
        similarity = 1 - cosine(stored_embedding, new_embedding)
        return similarity
    except Exception as e:
        logging.error("Error in face verification: %s", e)
        return None

@app.route("/", methods=['GET', 'POST'])
def home():
    return redirect(url_for('verify'))

@app.route("/results", methods=['GET'])
def results():
    try:
        resp = requests.get(f"{backend_addr}results")
        resp.raise_for_status()
        result = json.loads(resp.text)
        result.sort(reverse=True, key=lambda x: x["voteCount"])
        return render_template('results.html', result=result)
    except Exception as e:
        logging.error("Error fetching results: %s", e)
        return render_template('confirmation.html', message="Error processing results."), 500

@app.route("/verify", methods=['GET', 'POST'])
def verify():
    try:
        resp = requests.get(f"{backend_addr}isended")
        if not json.loads(resp.text):
            if request.method == 'POST':
                data = request.json  # Expect JSON from verification.html
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
                if similarity_score is not None and similarity_score > 0.6:
                    session['verified'] = True
                    session['aid'] = int(aadhaar_id)
                    return jsonify({"status": "success", "message": "✅ Face Matched! Redirecting to vote...", "redirect": url_for('vote')})
                else:
                    return jsonify({"status": "error", "message": "❌ Face Mismatch! Authentication Failed."}), 403

            return render_template('verification.html')
        else:
            return render_template('confirmation.html', message="Election ended", code=400), 400
    except Exception as e:
        logging.error("Error in /verify: %s", e)
        return render_template('confirmation.html', message="Error processing"), 500

@app.route("/vote", methods=['GET', 'POST'])
def vote():
    try:
        logging.debug(f"Session Data: {session}")  # Add this line for debugging
        resp = requests.get(f"{backend_addr}isended")
        if not json.loads(resp.text):
            if 'verified' in session and session['verified']:
                resp = requests.get(f"{backend_addr}candidates_list")
                candidates = json.loads(resp.text)
                candidates1, candidates2 = candidates[:len(candidates)//2], candidates[len(candidates)//2:]
                if request.method == 'POST':
                    aid = session.pop('aid')
                    session.pop('verified')
                    candidate = request.form['candidate']
                    cid = candidates.index(candidate) + 1
                    resp = requests.post(f"{backend_addr}/", json={"aadhaarID": aid, "candidateID": cid})
                    return render_template('confirmation.html', message=resp.text, code=resp.status_code), resp.status_code
                return render_template('vote.html', candidates1=candidates1, candidates2=candidates2)
            else:
                return redirect(url_for('verify'))
        else:
            return render_template('confirmation.html', message="Election ended", code=400), 400
    except Exception as e:
        logging.error("Error in /vote: %s", e)
        return render_template('confirmation.html', message="Error processing"), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=90, debug=True)