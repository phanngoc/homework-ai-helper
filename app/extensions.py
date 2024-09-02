from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
import json
import os
from .utils import load_google_creds

db = SQLAlchemy()
oauth = OAuth()
cors = CORS()

# Load Google OAuth credentials
google_creds = load_google_creds()

# Google OAuth setup
google = oauth.register(
    name='google',
    client_id=google_creds['client_id'],
    client_secret=google_creds['client_secret'],
    authorize_url=google_creds['auth_uri'],
    access_token_url=google_creds['token_uri'],
    authorize_params=None,
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=os.getenv('GOOGLE_REDIRECT_URI'),
    client_kwargs={'scope': 'email profile'},
)