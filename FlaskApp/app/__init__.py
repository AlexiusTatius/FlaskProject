from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application"""
    # Create the Flask app
    app = Flask(__name__)

    # Load configurations from Config class
    from app.config import Config
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    
    # Import and initialize models
    from app.models import User
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Initialize database migrations
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Debug: Print all URL mappings
    if app.debug:
        print("Registered Routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.endpoint:30} {rule.methods} {rule}")

    return app