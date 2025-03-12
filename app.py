import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Initialize SQLAlchemy with the Base class
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Database Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///quizmaster.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    with app.app_context():
        # Import models and create tables
        from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
        db.create_all()

    return app