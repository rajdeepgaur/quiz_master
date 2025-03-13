from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User

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
    return render_template('admin/dashboard.html')

# User routes
@user_bp.route('/')
@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    return render_template('user/dashboard.html')