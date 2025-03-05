from flask import Flask, render_template, flash, request, session, redirect, url_for
from wtforms import Form, StringField, TextAreaField, validators, SubmitField
import requests
import json
import logging
import os
import base64

backend_addr ="http://127.0.0.1:80/"

app = Flask(__name__)
app.secret_key = 'i love white chocolate'

logging.basicConfig(level=logging.DEBUG)

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
                aid = request.form['aid']
                image_data = request.form['image']  # Captured image in base64
                
                if aid.isdigit() and image_data:
                    verification_payload = {"aadhaarID": aid, "image": image_data}
                    verification_resp = requests.post(f"{backend_addr}face_verify", json=verification_payload)
                    
                    if verification_resp.status_code == 200:
                        session['verified'] = True
                        session['aid'] = int(aid)
                        return redirect(url_for('vote'))
                    else:
                        return render_template('confirmation.html', message="Face verification failed.", code=400), 400
            return render_template('verification.html')
        else:
            return render_template('confirmation.html', message="Election ended", code=400), 400
    except Exception as e:
        logging.error("Error in /verify: %s", e)
        return render_template('confirmation.html', message="Error processing"), 500

@app.route("/vote", methods=['GET', 'POST'])
def vote():
    try:
        resp = requests.get(f"{backend_addr}isended")
        if not json.loads(resp.text):
            if 'verified' in session:
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
