
from flask import Flask, request, session, jsonify
from flask_cors import CORS
import requests
from job_filter import job_match
from pymongo.mongo_client import MongoClient
from datetime import datetime, timedelta

collection = MongoClient("mongodb://localhost:27017")
db = collection['internshipmap']
resumes = db['resumes']
jobs = db['jobs']

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret-key'

def verify_token(token):
    res = requests.post("http://localhost:5001/verify", json={'token': token})
    return res.json()

@app.route('/api/match_jobs')
def match_jobs():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token[7:]
    print(token)
    if not token:
        return jsonify({'error': 'Missing token'}), 403

    auth = verify_token(token)
    if not auth.get('valid'):
        return jsonify({'error': auth.get('error', 'Invalid')}), 403

    email = auth['email']
    
    print(f"Looking up resume for email: {email}")
    data = job_match(email)
    return jsonify(data)

@app.route('/api/get_jobs')
def get_jobs():
    # email = session.get('user_email')
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token[7:]
    print(token)
    if not token:
        return jsonify({'error': 'Missing token'}), 403

    auth = verify_token(token)
    if not auth.get('valid'):
        return jsonify({'error': auth.get('error', 'Invalid')}), 403

    email = auth['email']
    job_list = jobs.find_one({'email' : email})
    if job_list:
        if job_list['date_accessed'] < datetime.now() - timedelta(days=3):
            return jsonify({'message' : "no jobs generated"})
        else:  
            return jsonify(job_list['jobs'])
    else:
        return jsonify({'message' : "no jobs generated"})
    

if __name__ == "__main__":
    app.run(debug=True, port=5002)




