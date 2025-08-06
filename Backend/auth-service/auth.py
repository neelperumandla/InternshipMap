import base64
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta
import bcrypt
import jwt
import os

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret-key'
# app.secret_key = "secret-key"
SECRET_KEY = os.getenv("JWT_SECRET", "secret-key")

client = MongoClient("mongodb://localhost:27017")
db = client['internshipmap']
collection = db['users']

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    if(collection.find_one({'email' : email})):
        return jsonify({'error': "User is already registered"})
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    hashed_pw_b64 = base64.b64encode(hashed_pw).decode('utf-8')
    
    collection.insert_one({
        'email' : email,
        'password' : hashed_pw_b64,
        'created_at' : datetime.now()
    })
    
    return jsonify({"message" : "User created succesfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = collection.find_one({'email' : data['email']})
    stored_hashed_pw = base64.b64decode(user['password'].encode())

    if not user or not bcrypt.checkpw(data['password'].encode(), stored_hashed_pw):
        return jsonify({"error" : "Invalid credentials"}), 401
    
    session['email'] = user['email']
    print(session['email'] + " " + session.get('email'))
    token = jwt.encode({
        'email' : user['email'],
        'exp' : datetime.now() + timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({'token' : token})

@app.route('/verify', methods=['POST'])
def verify():
    token = request.get_json().get('token')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    print("Verifying token:", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({'valid': True, 'email': payload['email']})
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
    