from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    # One-to-Many relationship with QuizAttempt
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # One-to-Many relationship with Chapter, cascade deletes
    chapters = db.relationship('Chapter', backref='subject', lazy=True, 
                             cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Many-to-One relationship with Subject
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    # One-to-Many relationship with Quiz, cascade deletes
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, 
                            cascade='all, delete-orphan')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # Many-to-One relationship with Chapter
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    date = db.Column(db.DateTime, nullable=False)
    # One-to-Many relationships with cascade deletes
    questions = db.relationship('Question', backref='quiz', lazy=True, 
                              cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Many-to-One relationship with Quiz
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Many-to-One relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)