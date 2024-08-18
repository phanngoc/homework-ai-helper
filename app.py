# app.py
from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
import openai
import cv2
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
oauth = OAuth(app)

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

# Routes
@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

from flask import session

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

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    npimg = np.fromfile(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    # Process image with OpenCV and extract question text
    question_text = "Extracted question text"
    # Use OpenAI API to get answer
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Image.create(
        file=open(file, "rb"),
        prompt=question_text,
        n=1,
        size="1024x1024"
    )
    answer_text = response['data'][0]['url']
    return jsonify({'question': question_text, 'answer': answer_text})

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
    db.create_all()
    app.run(debug=True)
