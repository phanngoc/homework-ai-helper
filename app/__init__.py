from flask import Flask
from .config import Config
from .extensions import db, oauth, cors
from .routes import main_bp
from .comments import comments_bp
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    oauth.init_app(app)
    cors.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(comments_bp, url_prefix='/api')

    # Ensure database tables are created within the application context
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)

    return app