from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
from datetime import datetime, timedelta
from sqlalchemy import func, case, text, or_
from sqlalchemy.types import Float

# Create blueprints with proper URL prefixes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')
main_bp = Blueprint('main', __name__)

# Main routes
@main_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'user.user_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please provide both username and password')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        if user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!')
            return redirect(url_for('admin.dashboard' if user.is_admin else 'user.user_dashboard'))

        flash('Invalid username or password')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'user.user_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Please fill in all fields')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, is_admin=False)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

# Admin routes
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('user.user_dashboard'))
    
     # Get all subjects (will show only 3 in template)
    subjects = Subject.query.all()

    return render_template('admin/dashboard.html', subjects=subjects)

@admin_bp.route('/subjects')
@login_required
def subjects():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@admin_bp.route('/subject/add', methods=['GET', 'POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        subject = Subject(name=name, description=description)
        try:
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding subject', 'error')

    return render_template('admin/add_subject.html')

@admin_bp.route('/chapter/add/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def add_chapter(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        try:
            db.session.add(chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding chapter', 'error')

    return render_template('admin/add_chapter.html', subject=subject)


@admin_bp.route('/subject/<int:subject_id>')
@login_required
def view_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/view_subject.html', subject=subject)

@admin_bp.route('/subject/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')
        try:
            db.session.commit()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('admin.view_subject', subject_id=subject.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating subject', 'error')

    return render_template('admin/edit_subject.html', subject=subject)

@admin_bp.route('/chapter/<int:chapter_id>')
@login_required
def view_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('admin/view_chapter.html', chapter=chapter)

@admin_bp.route('/chapter/edit/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        try:
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('admin.view_chapter', chapter_id=chapter.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating chapter', 'error')

    return render_template('admin/edit_chapter.html', chapter=chapter)

@admin_bp.route('/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    try:
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully')
        return '', 200
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {str(e)}')
        return 'Error deleting subject', 500

@admin_bp.route('/chapter/delete/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully')
        return '', 200
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting chapter: {str(e)}')
        return 'Error deleting chapter', 500

@admin_bp.route('/quiz/manage/<int:chapter_id>')
@login_required
def manage_quiz(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    chapter = Chapter.query.get_or_404(chapter_id)
    current_time = datetime.utcnow()
    return render_template('admin/quiz_management.html', chapter=chapter, current_time=current_time)

@admin_bp.route('/quiz/add/<int:chapter_id>', methods=['POST'])
@login_required
def add_quiz(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    if request.method == 'POST':
        try:
            # Get quiz details from form
            title = request.form.get('title')
            start_datetime = datetime.strptime(request.form.get('start_datetime'), '%Y-%m-%dT%H:%M')
            end_datetime = datetime.strptime(request.form.get('end_datetime'), '%Y-%m-%dT%H:%M')
            duration = int(request.form.get('duration'))

            # Create quiz
            quiz = Quiz(
                title=title,
                chapter_id=chapter_id,
                duration=duration,
                start_date=start_datetime,
                end_date=end_datetime
            )
            db.session.add(quiz)
            db.session.flush()  # Get quiz.id before committing

            # Process questions
            questions_data = {}
            for key, value in request.form.items():
                if key.startswith('questions['):
                    parts = key.replace('questions[', '').replace(']', ' ').split()
                    idx, field = parts[0], parts[1].replace('[', '').replace(']', '')

                    if idx not in questions_data:
                        questions_data[idx] = {}
                    questions_data[idx][field] = value

            # Create Question objects
            for idx, q_data in questions_data.items():
                if 'text' in q_data:  # Ensure we have complete question data
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q_data['text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct']
                    )
                    db.session.add(question)

            db.session.commit()
            flash('Quiz created successfully!')

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}')

        return redirect(url_for('admin.manage_quiz', chapter_id=chapter_id))

@admin_bp.route('/quiz/edit/<int:quiz_id>')
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin_bp.route('/quiz/update/<int:quiz_id>', methods=['POST'])
@login_required
def update_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)

    try:
        # Update quiz details
        quiz.title = request.form.get('title')
        start_date = datetime.strptime(request.form.get('start_date'),
                                       '%Y-%m-%d')
        quiz.duration = int(request.form.get('duration'))

        # Set start time to beginning of day and end time to end of day
        quiz.start_date = start_date.replace(hour=0, minute=0, second=0)
        quiz.end_date = start_date.replace(hour=23, minute=59, second=59)

        # Process questions
        questions_data = {}
        existing_question_ids = set()

        # Collect form data
        for key, value in request.form.items():
            if key.startswith('questions['):
                parts = key.replace('questions[', '').replace(']', ' ').split()
                idx, field = parts[0], parts[1].replace('[',
                                                        '').replace(']', '')

                if idx not in questions_data:
                    questions_data[idx] = {}
                questions_data[idx][field] = value

        # Update or create questions
        for idx, q_data in questions_data.items():
            if 'text' in q_data:
                if 'id' in q_data:  # Existing question
                    question = Question.query.get(int(q_data['id']))
                    if question:
                        question.question_text = q_data['text']
                        question.option_a = q_data['option_a']
                        question.option_b = q_data['option_b']
                        question.option_c = q_data['option_c']
                        question.option_d = q_data['option_d']
                        question.correct_answer = q_data['correct']
                        existing_question_ids.add(question.id)
                else:  # New question
                    question = Question(quiz_id=quiz.id,
                                        question_text=q_data['text'],
                                        option_a=q_data['option_a'],
                                        option_b=q_data['option_b'],
                                        option_c=q_data['option_c'],
                                        option_d=q_data['option_d'],
                                        correct_answer=q_data['correct'])
                    db.session.add(question)

        db.session.commit()
        flash('Quiz updated successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating quiz: {str(e)}')

    return redirect(url_for('admin.manage_quiz', chapter_id=quiz.chapter_id))


@admin_bp.route('/quiz/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully')
        return '', 200
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}')
        return 'Error deleting quiz', 500
    
@admin_bp.route('/search')
@login_required
def admin_search():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('admin.dashboard'))

    # Search users
    users = User.query.filter(
        or_(User.username.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%'))).all()

    # Search subjects
    subjects = Subject.query.filter(
        or_(Subject.name.ilike(f'%{query}%'),
            Subject.description.ilike(f'%{query}%'))).all()

    # Search quizzes
    quizzes = Quiz.query.filter(Quiz.title.ilike(f'%{query}%')).all()

    # Search questions
    questions = Question.query.filter(
        Question.question_text.ilike(f'%{query}%')).all()

    return render_template('admin/search_results.html',
                           query=query,
                           users=users,
                           subjects=subjects,
                           quizzes=quizzes,
                           questions=questions)

# User routes
@user_bp.route('/')
@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    subjects = Subject.query.all()
    current_time = datetime.utcnow()


    # Get only 3 recent attempts
    recent_attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
        .order_by(QuizAttempt.date_attempted.desc())\
        .limit(3).all()

    return render_template('user/dashboard.html', 
                         subjects=subjects, 
                         attempts=recent_attempts,
                         current_time=current_time)

# Add new route for viewing all attempts
@user_bp.route('/attempts')
@login_required
def view_attempts():
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
        .order_by(QuizAttempt.date_attempted.desc())\
        .all()
    return render_template('user/attempts.html', attempts=attempts)

# Add new route for summary report
@user_bp.route('/summary')
@login_required
def view_summary():
    # Get total score and maximum possible score
    attempts_with_scores = db.session.query(
        QuizAttempt.score,
        func.count(Question.id).label('total_questions')
    ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
    .join(Question, Question.quiz_id == Quiz.id)\
    .filter(QuizAttempt.user_id == current_user.id)\
    .group_by(QuizAttempt.id, QuizAttempt.score)\
    .all()

    total_score = sum(attempt.score for attempt in attempts_with_scores)
    total_possible = sum(attempt.total_questions for attempt in attempts_with_scores)
    total_attempts = len(attempts_with_scores)

    # Calculate percentage score
    avg_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0

    quiz_stats = {
        'total_attempts': total_attempts,
        'total_score': total_score,
        'total_possible': total_possible,
        'avg_percentage': round(avg_percentage, 2)
    }

    # First get the total questions per quiz in a subquery
    questions_per_quiz = db.session.query(
        Quiz.id.label('quiz_id'),
        func.count(Question.id).label('question_count')
    ).join(Question)\
    .group_by(Quiz.id)\
    .subquery()

    # Then use this to calculate subject-wise statistics
    subject_stats = db.session.query(
        Subject.name,
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(
            (100.0 * QuizAttempt.score / questions_per_quiz.c.question_count)
        ).label('avg_score')
    ).select_from(Subject)\
    .join(Chapter)\
    .join(Quiz)\
    .join(questions_per_quiz, questions_per_quiz.c.quiz_id == Quiz.id)\
    .join(QuizAttempt)\
    .filter(QuizAttempt.user_id == current_user.id)\
    .group_by(Subject.name)\
    .all()

    return render_template('user/summary.html', 
                         quiz_stats=quiz_stats,
                         subject_stats=subject_stats)

@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()

    # Check if quiz is available
    if current_time < quiz.start_date or current_time > quiz.end_date:
        flash('This quiz is not available at this time.')
        return redirect(url_for('user.user_dashboard'))

    return render_template('user/quiz.html', quiz=quiz)


@user_bp.route('/quiz/<int:quiz_id>/view')
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()

    # Check if quiz has ended
    if current_time <= quiz.end_date:
        flash('This quiz is still active and cannot be viewed.')
        return redirect(url_for('user.user_dashboard'))

    return render_template('user/view_quiz.html', quiz=quiz)


@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()

    # Check if quiz is still available
    if current_time < quiz.start_date or current_time > quiz.end_date:
        flash('This quiz is not available at this time.')
        return redirect(url_for('user.user_dashboard'))

    score = 0
    for question in quiz.questions:
        answer = request.form.get(f'question_{question.id}')
        if answer == question.correct_answer:
            score += 1

    attempt = QuizAttempt(user_id=current_user.id,
                         quiz_id=quiz_id,
                         score=score)
    db.session.add(attempt)
    db.session.commit()
    flash(f'Quiz submitted! Your score: {score}/{len(quiz.questions)}')
    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/search')
@login_required
def user_search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('user.user_dashboard'))

    # Search subjects
    subjects = Subject.query.filter(
        or_(Subject.name.ilike(f'%{query}%'),
            Subject.description.ilike(f'%{query}%'))).all()

    # Search quizzes - include matches on subject name, chapter name, and quiz title
    quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        or_(Subject.name.ilike(f'%{query}%'), Chapter.name.ilike(f'%{query}%'),
            Quiz.title.ilike(f'%{query}%'))).all()

    return render_template('user/search_results.html',
                           query=query,
                           subjects=subjects,
                           quizzes=quizzes)