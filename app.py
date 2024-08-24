# app.py
import re
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
import openai
import cv2
import numpy as np
import base64
from dotenv import load_dotenv
import os
from flask import session
import requests
import uuid
from flask_cors import CORS 

# Load environment variables from .env file
load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print('env:SQLALCHEMY_DATABASE_URI', app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)
oauth = OAuth(app)
CORS(app)

# Google OAuth setup
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'teacher' or 'student'
    subscription = db.Column(db.String(10), nullable=False)  # 'free' or 'premium'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

# Ensure database tables are created within the application context
with app.app_context():
    print('app_context')
    db.create_all()

# Routes
@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    # Handle user info and create user in DB if not exists
    return jsonify(user_info.data)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# write function load index page and App.js file
@app.route('/')
def index():
    print('index')
    return app.send_static_file('index.html')

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def resolve_solution(url, action):
    if action == 'suggestion':
        question_text = "Đề xuất các gợi ý để giải quyết vấn đề"
    else:
        question_text = "Chọn đáp án đúng và đưa ra lời giải thích"

    image_base64 = encode_image(url)
    system_message = "Bạn là một giáo viên toán cấp 3, đang hướng dẫn học sinh thi tốt nghiệp đại học."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": question_text,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ]
            },
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content

@app.route('/upload', methods=['POST'])
def upload():
    action = request.form.get('action', type=str)
    temp_url = request.form.get('temp_url', type=str)
    response = resolve_solution(temp_url, action)

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
