from flask import Flask, request, jsonify
from flask_cors import CORS
import os

import requests
from resume_parser import parse_resume
from werkzeug.utils import secure_filename
# from models import db, Resume
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
CORS(app)


# Create a new client and connect to the server
client = MongoClient("mongodb://localhost:27017")
db = client['internshipmap']
collection = db['resumes']

# db.init_app(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def verify_token(token):
    res = requests.post("http://localhost:5001/verify", json={'token': token})
    return res.json()

@app.route('/')
def home():
    return "Backend running"

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token[7:]
    print(token)
    if not token:
        return jsonify({'error': 'Missing token'}), 403

    auth = verify_token(token)
    print(auth)
    if not auth.get('valid'):
        return jsonify({'error': auth.get('error', 'Invalid')}), 403

    user_email = auth['email']
    
    resume = request.files.get('resume')
    if not resume:
        return jsonify({"error": "No file uploaded"}), 401
    
    filename = secure_filename(resume.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(filepath)
    
    try:
        parsed = parse_resume(filepath)
        os.remove(filepath)

        # Debug print what we got back from Gemini
        # print("Parsed resume data:", parsed)

        if not isinstance(parsed, dict):
            raise ValueError("Gemini response was not a dictionary")

        user = collection.find_one({'email' : user_email})
        parsed['email'] = user_email
        if(user):
            
            collection.update_one({'email' : user_email}, {'$set' : parsed})
        else:  
            # parsed['email'] = user_email
            collection.insert_one(parsed)
        return jsonify({"email" : parsed['email'],
                        "skills" : parsed['skills'],
                        "experience" : parsed['experience'],
                        "projects" : parsed['projects']})

    except Exception as e:
        print("Error during resume parsing:", e)
        return jsonify({
            "error": str(e)
        }), 500
    

# with app.app_context():
#     db.create_all()
    

if __name__ == "__main__":
    app.run(debug=True)
    
    
    