# app.py
import json
from flask import Flask, request, jsonify, url_for, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import openai
import cv2
import numpy as np
import base64
from dotenv import load_dotenv
import os
from flask import session
import uuid
from flask_cors import CORS 
import secrets
from sqlalchemy import inspect
import jwt
import datetime
from openai_resolve import resolve_solution
from functools import wraps

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

print('env:SQLALCHEMY_DATABASE_URI', app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)
oauth = OAuth(app)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if the token is passed in the request headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        # If token is not provided, return an error
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print('token_required:data', data)
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
# Load Google OAuth credentials from JSON file
with open('secret/client_secret_729346947261-6btkvj36hci72mtc5mpkp1pfmqo1pnob.apps.googleusercontent.com.json') as f:
    google_creds = json.load(f)['web']

# Google OAuth setup
google = oauth.register(
    name='google',
    client_id=google_creds['client_id'],
    client_secret=google_creds['client_secret'],
    authorize_url=google_creds['auth_uri'],
    access_token_url=google_creds['token_uri'],
    authorize_params=None,
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=os.getenv('GOOGLE_REDIRECT_URI'),
    client_kwargs={'scope': 'email profile'},
)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=False, nullable=True)
    role = db.Column(db.String(10), nullable=True)  # 'teacher' or 'student'
    profile_pic = db.Column(db.String(200), nullable=True)
    subscription = db.Column(db.String(10), nullable=True)  # 'free' or 'premium'

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

def list_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)

# Ensure database tables are created within the application context
with app.app_context():
    print('app_context')
    db.create_all()
    list_tables()

# Routes
@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)


def generate_token(user_info):
    payload = {
        'email': user_info['email'],
        'id': user_info['id'],
        'name': user_info['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    if token is None:
        return 'Access denied: reason={} error={}'.format(
            request.args.get('error_reason'),
            request.args.get('error_description')
        )
    session['google_token'] = token
    print('token', token)
     # Fix the MissingSchema error by providing the full URL with scheme
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    print('user_info', user_info)
    # Save user info to the database
    user = User.query.filter_by(email=user_info['email']).first()
    if user is None:
        user = User(
            identity=user_info['id'],
            email=user_info['email'],
            name=user_info['name'],
            profile_pic=user_info['picture']
        )
        db.session.add(user)
        db.session.commit()
        # Generate JWT token
        jwt_token = generate_token(user_info)

    # Redirect to the frontend app with the token
    frontend_url = f"http://localhost:3000?token={jwt_token}"
    return redirect(frontend_url)

# write function load index page and App.js file
@app.route('/')
def index():
    print('index')
    return app.send_static_file('index.html')

@app.route('/api/answer', methods=['POST'])
@token_required
def answer():
    action = request.form.get('action', type=str)
    temp_url = request.form.get('temp_url', type=str)
    print('method:answer', action, temp_url)
    response = resolve_solution(temp_url, action)
    print('method:ai-answer', response)
    return jsonify({'response': response})

@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    file = request.files['file']
    npimg = np.fromfile(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    # Save the image to a temporary location
    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    temp_filepath = os.path.join('uploads', temp_filename)
    print('temp_filepath', temp_filepath)
    cv2.imwrite(temp_filepath, img)

    return jsonify({'temporary_url': temp_filepath})

@app.route('/questions/<int:question_id>/comments', methods=['GET'])
def get_comments(question_id):
    comments = Comment.query.filter_by(question_id=question_id).all()
    return jsonify([{
        'id': comment.id,
        'user': {'id': comment.user.id, 'email': comment.user.email},
        'text': comment.text
    } for comment in comments])

@app.route('/questions/<int:question_id>/comments', methods=['POST'])
def post_comment(question_id):
    data = request.json
    comment = Comment(
        question_id=question_id,
        user_id=data['userId'],
        text=data['text']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'id': comment.id,
        'user': {'id': comment.user.id, 'email': comment.user.email},
        'text': comment.text
    })

if __name__ == '__main__':
    app.run(debug=True)
