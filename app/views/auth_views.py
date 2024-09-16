"""A blueprint for authentication views (register, login, logout)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from ..models import User
from .. import db, bcrypt

auth_views = Blueprint('auth_views', __name__)

@auth_views.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        # Extract form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm-password')
        
        # Use helper function for registration logic (in utils.py)
        from ..utils import register_user
        success, message = register_user(username, email, password, confirm)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth_views.login'))
        else:
            flash(message, 'danger')
    
    return render_template('register.html')

@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('course_views.courses'))
        else:
            flash('Login unsuccessful. Please check your email and password.')
    return render_template('login.html')

@auth_views.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth_views.login'))
