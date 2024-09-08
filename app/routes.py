from flask import Blueprint, request, jsonify, send_from_directory, url_for, session, redirect

from app.config import Config
from .models import Answer, Question, User
from .extensions import db, google
from flask import current_app
import jwt
import datetime
from functools import wraps
from .openai_resolve import resolve_solution
from .auth import token_required  # Updated import
import cv2
import numpy as np
import uuid
import os

main_bp = Blueprint('main', __name__)

# Routes
@main_bp.route('/login')
def login():
    redirect_uri = url_for('main.authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

def generate_token(user_info):
    payload = {
        'email': user_info['email'],
        'id': user_info['id'],
        'name': user_info['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*7)  # Token expiration time
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

@main_bp.route('/login/authorized')
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
    print('authorized:user', user)
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
@main_bp.route('/')
def index():
    print('index')
    return current_app.send_static_file('index.html')

@main_bp.route('/api/answer', methods=['POST'])
@token_required
def answer(current_user):
    print('answer:current_user', current_user)
    data = request.get_json()
    action = data['action']
    imageSrc = data['imageSrc']
    print('method:answer', action, imageSrc)

    response = resolve_solution(imageSrc, action)
    question = Question(
        question_text=imageSrc,
        category='math',
        grade=10,
        user_id=current_user.id,
        answer_text=response['response']['parsed']['final_answer'],
        type='link'
    )

    db.session.add(question)
    db.session.commit()

    answer = Answer(
        question_id=question.id,
        content=response['response']['content'],
        role='bot'
    )

    db.session.add(answer)
    db.session.commit()
    
    question_dict = question.to_dict()
    return jsonify({'answer': response, 'question': question_dict})

@main_bp.route('/upload_screenshot', methods=['POST'])
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

@main_bp.route('/uploads/<string:filename>', methods=['GET'])
def server_imagefile(filename):
    try:
        print('server_imagefile', filename)
        data = send_from_directory('../uploads', filename)
        print('server_imagefile: data', data)
        return data
    except Exception as e:
        print('server_imagefile:exception', e)
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question_and_answer(question_id):
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.filter_by(question_id=question_id).first()
    
    if not answer:
        return jsonify({'error': 'Answer not found'}), 404

    question_dict = question.to_dict()
    print('question_dict', question_dict)
    question_dict['question_text'] = Config.BASE_URL + '/' + question_dict['question_text']
    answer_dict = {
        'id': answer.id,
        'content': answer.content,
        'role': answer.role,
        'created_at': answer.created_at,
        'updated_at': answer.updated_at
    }

    return jsonify({'question': question_dict, 'answer': answer_dict})
