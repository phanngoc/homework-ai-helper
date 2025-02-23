import os
from dotenv import load_dotenv

load_dotenv('../.env')

print('SQLALCHEMY_DATABASE_URI', os.getenv('SQLALCHEMY_DATABASE_URI'))
class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost:5485/homeworkdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    BASE_URL = os.getenv('BASE_URL')