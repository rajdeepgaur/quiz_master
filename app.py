import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Initialize SQLAlchemy 
db = SQLAlchemy()
# Initialize Flask-Login
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get("SESSION_SECRET")

    # Database Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///quizmaster.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Set secret key for session management
    # Use environment variable in production, fallback to a development key
    app.secret_key = os.environ.get("SESSION_SECRET") or 'dev-secret-key-123' 

    # Initialize SQLAlchemy
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    with app.app_context():
        # Import models and create tables
        from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
        db.create_all()

        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin098765')
            db.session.add(admin)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        from routes import auth_bp, admin_bp, user_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(user_bp)
   

    return app