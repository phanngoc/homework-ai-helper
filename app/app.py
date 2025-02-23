from flask import Flask, request, jsonify, send_from_directory, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
from config import Config
from extensions import oauth, cors, google, db
from models import Answer, Question, User, Comment
from openai_resolve import resolve_solution
from auth import token_required
from flask_migrate import Migrate
import jwt
import datetime
import cv2
import numpy as np
import uuid
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
print('SECRET_KEY', os.getenv('SECRET_KEY'))

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize extensions
db.init_app(app)
oauth.init_app(app)
cors.init_app(app)
migrate = Migrate(app, db)

# Ensure database tables are created
with app.app_context():
    db.create_all()

# Auth routes
@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

def generate_token(user_info):
    payload = {
        'email': user_info['email'],
        'id': user_info['id'],
        'name': user_info['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    if token is None:
        return 'Access denied: reason={} error={}'.format(
            request.args.get('error_reason'),
            request.args.get('error_description')
        )

    session['google_token'] = token
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    
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
    
    jwt_token = generate_token(user_info)
    frontend_url = f"http://localhost:3000?token={jwt_token}"
    return redirect(frontend_url)

# Main routes
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/answer', methods=['POST'])
@token_required
def answer(current_user):
    data = request.get_json()
    action = data['action']
    imageSrc = data['imageSrc']

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
    
    return jsonify({'answer': response, 'question': question.to_dict()})

# Comment routes
@app.route('/api/questions/<int:question_id>/comments', methods=['GET'])
def get_comments(question_id):
    comments = Comment.query.filter_by(question_id=question_id).all()
    response_arr = [{
        'id': comment.id,
        'text': comment.text,
        'user': comment.user.to_dict(),
    } for comment in comments]
    return jsonify(response_arr)

@app.route('/api/questions/<int:question_id>/comments', methods=['POST'])
@token_required
def post_comment(current_user, question_id):
    data = request.json
    comment = Comment(
        question_id=question_id,
        user_id=current_user.id,
        text=data['text']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'id': comment.id,
        'user': current_user,
        'text': comment.text
    })

# File handling routes
@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    file = request.files['file']
    npimg = np.fromfile(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    temp_filepath = os.path.join('uploads', temp_filename)
    cv2.imwrite(temp_filepath, img)
    return jsonify({'temporary_url': temp_filepath})

@app.route('/uploads/<string:filename>', methods=['GET'])
def serve_imagefile(filename):
    try:
        return send_from_directory('../uploads', filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question_and_answer(question_id):
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.filter_by(question_id=question_id).first()
    
    if not answer:
        return jsonify({'error': 'Answer not found'}), 404

    question_dict = question.to_dict()
    question_dict['question_text'] = Config.BASE_URL + '/' + question_dict['question_text']
    answer_dict = {
        'id': answer.id,
        'content': answer.content,
        'role': answer.role,
        'created_at': answer.created_at,
        'updated_at': answer.updated_at
    }

    return jsonify({'question': question_dict, 'answer': answer_dict})

if __name__ == '__main__':
    app.run(debug=True)