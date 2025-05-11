
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # For API use JSON; for HTML forms use request.form.
        data = request.form if request.form else request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not username or not email or not password:
            flash('Please fill out all fields')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Create JWT token
            access_token = create_access_token(identity=user.id)
            # Log in via Flask-Login for HTML sessions
            login_user(user)
            flash('Logged in successfully')
            # For API: return token; for HTML, redirect.
            if request.is_json:
                return jsonify({'access_token': access_token, 'msg': 'Logged in successfully'}), 200
            return redirect(url_for('posts.list_posts'))
        else:
            flash('Invalid credentials')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('auth.login'))
