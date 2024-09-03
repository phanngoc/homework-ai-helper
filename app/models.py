from traitlets import default
from .extensions import db
import datetime

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
    answer_text = db.Column(db.JSON, nullable=True)
    type = db.Column(db.String(10), nullable=True)  # 'image' or 'text'
    category = db.Column(db.String, nullable=True)  # New column for category
    grade = db.Column(db.Integer, nullable=True)  # New column for grade
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'category': self.category,
            'grade': self.grade,
            'user_id': self.user_id,
            'answer_text': self.answer_text,
            'type': self.type
        }

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    content = db.Column(db.JSON, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'bot'
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, question_id, content, role):
        self.question_id = question_id
        self.content = content
        self.role = role

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    def __init__(self, question_id, user_id, text):
        self.question_id = question_id
        self.user_id = user_id
        self.text = text
    
class Performance(db.Model):
    __tablename__ = 'performances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    score = db.Column(db.Integer)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, student_id, question_id, score):
        self.student_id = student_id
        self.question_id = question_id
        self.score = score