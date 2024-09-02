from flask import Blueprint, request, jsonify, url_for, session, redirect
from .models import User
from .extensions import db, google
from flask import current_app
import jwt
import datetime
from functools import wraps
from .openai_resolve import resolve_solution
import cv2
import numpy as np
import uuid
import os

main_bp = Blueprint('main', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(identity=data['id']).first()
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired!', 'code': 401, 'extra_code': 2}
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid!', 'code': 401, 'extra_code': 1}
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

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
    data = request.get_json()
    action = data['action']
    imageSrc = data['imageSrc']
    print('method:answer', action, imageSrc)
    response = resolve_solution(imageSrc, action)
    print('method:ai-answer', response)
    return jsonify({'response': response})

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

# @main_bp.route('/questions/<int:question_id>/comments', methods=['GET'])
# def get_comments(question_id):
#     comments = Comment.query.filter_by(question_id=question_id).all()
#     return jsonify([{
#         'id': comment.id,
#         'user': {'id': comment.user.id, 'email': comment.user.email},
#         'text': comment.text
#     } for comment in comments])

# @main_bp.route('/questions/<int:question_id>/comments', methods=['POST'])
# def post_comment(question_id):
#     data = request.json
#     comment = Comment(
#         question_id=question_id,
#         user_id=data['userId'],
#         text=data['text']
#     )
#     db.session.add(comment)
#     db.session.commit()
#     return jsonify({
#         'id': comment.id,
#         'user': {'id': comment.user.id, 'email': comment.user.email},
#         'text': comment.text
#     })
