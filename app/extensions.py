from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS

db = SQLAlchemy()
oauth = OAuth()
cors = CORS()