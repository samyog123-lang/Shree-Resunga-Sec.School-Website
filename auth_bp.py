# auth_bp.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

# ---------------- SIGNUP ----------------
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', '').strip()  # 'admin', 'teacher', 'student'

        # Validation
        if not all([username, email, password, confirm_password, role]):
            flash('Please fill in all fields!', 'danger')
            return redirect(url_for('auth.signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('auth.signup'))

        # Create user
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=password_hash, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Fetch user from DB
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))

        # Log in user
        login_user(user)
        flash(f'Welcome, {user.username}!', 'success')

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))  # change route as needed
        elif user.role == 'teacher':
            return redirect(url_for('views.teacher_dashboard'))
        else:
            return redirect(url_for('views.student_dashboard'))

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('views.homepage'))
