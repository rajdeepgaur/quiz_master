from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User model for both admin and regular users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

    def set_password(self, password):
        """Hash the password for security."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Subject(db.Model):
    """Subject model for different courses."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, 
                             cascade='all, delete-orphan')

class Chapter(db.Model):
    """Chapter model linked to subjects."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, 
                            cascade='all, delete-orphan')

class Quiz(db.Model):
    """Quiz model linked to chapters."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    date = db.Column(db.DateTime, nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True, 
                              cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class Question(db.Model):
    """Question model for quiz questions."""
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

class QuizAttempt(db.Model):
    """QuizAttempt model to track user attempts at quizzes."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)