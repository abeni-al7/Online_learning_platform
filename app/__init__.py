import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, ALL

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
uploaded_files = UploadSet('files', ALL)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOADS_DEFAULT_DEST'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOADS_DEFAULT_DEST'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    configure_uploads(app, uploaded_files)

    login_manager.login_view = 'login'

    with app.app_context():
        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        db.create_all()

    return app