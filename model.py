from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from sqlalchemy import create_engine
# Define the PostgreSQL connection URL
DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"
# Create an engine
engine = create_engine(DATABASE_URL)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=True)  # 'teacher' or 'student'
    subscription = db.Column(db.String(10), nullable=True)  # 'free' or 'premium'

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

print('db:start init')
db.create_all()
