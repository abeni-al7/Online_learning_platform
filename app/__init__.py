#!/usr/bin/env python3
"""A module for creating the Flask app and setting up the database, login manager, and file uploads."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, ALL

# Initialize the database, login manager, and file uploads
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
uploaded_files = UploadSet('files', ALL)

def create_app():
    """Create the Flask app and set up the database, login manager, and file uploads."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOADS_DEFAULT_DEST'], exist_ok=True)

    # Initialize the database, login manager, and file uploads
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    bcrypt.init_app(app)
    configure_uploads(app, uploaded_files)

    # Register blueprints
    from views.auth import auth as auth_blueprint
    from views.profile import profile as profile_blueprint
    from views.courses import courses as courses_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(courses_blueprint)

    # Create the database tables
    with app.app_context():
        db.create_all()
    
    return app
