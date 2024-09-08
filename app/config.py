import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    BASE_URL = os.getenv('BASE_URL')