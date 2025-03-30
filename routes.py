from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
from datetime import datetime, timedelta
from sqlalchemy import func, case, text, or_
from sqlalchemy.types import Float

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')


# Root route
@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.user_dashboard'))
    return redirect(url_for('auth.login'))


# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            # Clear any existing flash messages
            session.pop('_flashes', None)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.user_dashboard'))

        flash('Invalid username or password')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Prevent registration with username 'admin'
        if username.lower() == 'admin':
            flash('This username is reserved')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Admin routes
@admin_bp.route('/subjects')
@login_required
def subjects():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    # Get all subjects (will show only 3 in template)
    subjects = Subject.query.all()
    
    # Get only non-admin users
    users = User.query.filter_by(is_admin=False).all()

    # Get statistics for admin dashboard
    stats = {
        'total_users':
            User.query.filter_by(is_admin=False).count(),
        'active_quizzes':
            Quiz.query.filter(Quiz.start_date <= datetime.utcnow(), Quiz.end_date
                              >= datetime.utcnow()).count(),
        'completed_attempts':
            QuizAttempt.query.count(),
        'avg_score':
            db.session.query(func.avg(QuizAttempt.score)).scalar() or 0
    }

    return render_template('admin/dashboard.html',
                           subjects=subjects,
                           stats=stats,
                           users=users)


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

        chapter = Chapter(name=name,
                          description=description,
                          subject_id=subject_id)
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
            return redirect(
                url_for('admin.view_subject', subject_id=subject.id))
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
            return redirect(
                url_for('admin.view_chapter', chapter_id=chapter.id))
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
    return render_template('admin/quiz_management.html',
                         chapter=chapter,
                         current_time=current_time,
                         timedelta=timedelta)


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

            # Debug output
            print(f"DEBUG: Adding quiz with times - Start: {start_datetime}, End: {end_datetime}")

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
        quiz.start_date = datetime.strptime(request.form.get('start_datetime'), '%Y-%m-%dT%H:%M')
        quiz.end_date = datetime.strptime(request.form.get('end_datetime'), '%Y-%m-%dT%H:%M')
        quiz.duration = int(request.form.get('duration'))

        # Process questions
        questions_data = {}
        existing_question_ids = set()

        # Collect form data
        for key, value in request.form.items():
            if key.startswith('questions['):
                parts = key.replace('questions[', '').replace(']', ' ').split()
                idx, field = parts[0], parts[1].replace('[', '').replace(']', '')

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


# Admin Search Route
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
@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    subjects = Subject.query.all()
    current_time = datetime.utcnow()
    current_ts = current_time.timestamp()

    print(f"DEBUG: Current time (UTC): {current_time}")
    print(f"DEBUG: Current timestamp: {current_ts}")

    # Pre-process quiz status
    active_quizzes = []
    past_quizzes = []

    for subject in subjects:
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                quiz_start_ts = quiz.start_date.timestamp()
                quiz_end_ts = quiz.end_date.timestamp()

                print(f"\nDEBUG: Checking quiz: {quiz.title}")
                print(f"DEBUG: Quiz start time: {quiz.start_date} (TS: {quiz_start_ts})")
                print(f"DEBUG: Quiz end time: {quiz.end_date} (TS: {quiz_end_ts})")
                print(f"DEBUG: Current time: {current_time} (TS: {current_ts})")

                # Check if quiz is active (started but not ended) - strictly using timestamp comparison
                is_active = quiz_start_ts <= current_ts and quiz_end_ts > current_ts
                print(f"DEBUG: Is active? {is_active}")
                print(f"DEBUG: Start check: {quiz_start_ts <= current_ts}")
                print(f"DEBUG: End check: {quiz_end_ts > current_ts}")

                if is_active:
                    active_quizzes.append(quiz)
                    print(f"DEBUG: Quiz {quiz.title} is ACTIVE")
                elif quiz_end_ts <= current_ts:
                    past_quizzes.append(quiz)
                    print(f"DEBUG: Quiz {quiz.title} is PAST")
                else:
                    print(f"DEBUG: Quiz {quiz.title} is NOT active")

    # Get only 3 recent attempts
    recent_attempts = QuizAttempt.query.filter_by(user_id=current_user.id) \
        .order_by(QuizAttempt.date_attempted.desc()) \
        .limit(3).all()

    return render_template('user/dashboard.html',
                        subjects=subjects,
                        active_quizzes=active_quizzes,
                        past_quizzes=past_quizzes,
                        attempts=recent_attempts,
                        current_time=current_time)


# Add new route for viewing all attempts
@user_bp.route('/attempts')
@login_required
def view_attempts():
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id) \
        .order_by(QuizAttempt.date_attempted.desc()) \
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
    ).join(Quiz, QuizAttempt.quiz_id == Quiz.id) \
        .join(Question, Question.quiz_id == Quiz.id) \
        .filter(QuizAttempt.user_id == current_user.id) \
        .group_by(QuizAttempt.id, QuizAttempt.score) \
        .all()

    total_score = sum(attempt.score for attempt in attempts_with_scores)
    total_possible = sum(attempt.total_questions
                         for attempt in attempts_with_scores)
    total_attempts = len(attempts_with_scores)

    # Calculate percentage score
    avg_percentage = (total_score / total_possible *
                      100) if total_possible > 0 else 0

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
    ).join(Question) \
        .group_by(Quiz.id) \
        .subquery()

    # Then use this to calculate subject-wise statistics
    subject_stats = db.session.query(
        Subject.name,
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(
            (100.0 * QuizAttempt.score / questions_per_quiz.c.question_count)
        ).label('avg_score')
    ).select_from(Subject) \
        .join(Chapter) \
        .join(Quiz) \
        .join(questions_per_quiz, questions_per_quiz.c.quiz_id == Quiz.id) \
        .join(QuizAttempt) \
        .filter(QuizAttempt.user_id == current_user.id) \
        .group_by(Subject.name) \
        .all()

    return render_template('user/summary.html',
                           quiz_stats=quiz_stats,
                           subject_stats=subject_stats)


@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()
    current_ts = current_time.timestamp()
    quiz_start_ts = quiz.start_date.timestamp()
    quiz_end_ts = quiz.end_date.timestamp()

    # Check if quiz is available using timestamp comparison
    if current_ts < quiz_start_ts or current_ts > quiz_end_ts:
        flash('This quiz is not available at this time.')
        return redirect(url_for('user.user_dashboard'))

    return render_template('user/quiz.html', quiz=quiz)


@user_bp.route('/quiz/<int:quiz_id>/view')
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()
    current_ts = current_time.timestamp()
    quiz_end_ts = quiz.end_date.timestamp()

    # Check if quiz has ended using timestamp comparison
    if current_ts <= quiz_end_ts:
        flash('This quiz is still active and cannot be viewed.')
        return redirect(url_for('user.user_dashboard'))

    return render_template('user/view_quiz.html', quiz=quiz)


@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()
    current_ts = current_time.timestamp()
    quiz_start_ts = quiz.start_date.timestamp()
    quiz_end_ts = quiz.end_date.timestamp()

    # Check if quiz is still available using timestamp comparison
    if current_ts < quiz_start_ts or current_ts > quiz_end_ts:
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


# User Search Route
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