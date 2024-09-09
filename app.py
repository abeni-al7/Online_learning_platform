import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        role = request.form.get('role')
        password = request.form.get('password')
        confirm = request.form.get('confirm-password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if password != confirm:
            flash('Passwords don\'t match')
            print('Passwords don\'t match')
        else:
            try:
                from models import User
                new_user = User(email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                print('Success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('Something went wrong. Please try again.')
                print(e)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        from models import User
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('courses'))
        else:
            flash('Login unsuccessful. Please check your username and password.')
    return render_template('login.html')

@app.route('/courses')
def courses():
    courses = [
        {
            'name': 'Python Programming',
            'code': 'PY101',
            'description': 'Learn Python Programming from scratch'
        },
        {
            'name': 'Web Development',
            'code': 'WD101',
            'description': 'Learn Web Development from scratch'
        },
        {
            'name': 'Data Science',
            'code': 'DS101',
            'description': 'Learn Data Science from scratch'
        },
    ]
    user = {
        'name': 'John Doe',
    }
    role = 'teacher'
    return render_template('courses.html', role=role, courses=courses, user=user)

@app.route('/courses/browse')
def browse_courses():
    courses = [
        {
            'name': 'Python Programming',
            'code': 'PY101',
            'description': 'Learn Python Programming from scratch'
        },
        {
            'name': 'Web Development',
            'code': 'WD101',
            'description': 'Learn Web Development from scratch'
        },
        {
            'name': 'Data Science',
            'code': 'DS101',
            'description': 'Learn Data Science from scratch'
        },
    ]
    user = {
        'name': 'John Doe',
    }
    role = 'student'
    return render_template('browse_courses.html', courses=courses, user=user)

@app.route('/courses/enrolled')
def enrolled_courses():
    courses = [
        {
            'name': 'Python Programming',
            'code': 'PY101',
            'description': 'Learn Python Programming from scratch'
        },
        {
            'name': 'Web Development',
            'code': 'WD101',
            'description': 'Learn Web Development from scratch'
        },
    ]
    user = {
        'name': 'John Doe',
    }
    role = 'student'
    return render_template('enrolled_courses.html', courses=courses, user=user)

@app.route('/courses/wishlist')
def wishlist():
    courses = [
        {
            'name': 'Data Science',
            'code': 'DS101',
            'description': 'Learn Data Science from scratch'
        },
    ]
    user = {
        'name': 'John Doe',
    }
    role = 'student'
    return render_template('wishlist.html', courses=courses, user=user)

@app.route('/profile')
def profile():
    role = 'teacher'
    user = {
        'username': 'johndoe',
        'name': 'John Doe',
        'email': 'john@doe.com',
        'role': role,
        'grade': '10th Grade',
        'bio': 'I am a student at XYZ High School',
        'certificates': [
            {
                'name': 'Python Programming',
                'year': '1998',
                'institution': 'ABC Institute',
                'description': 'Learned Python Programming from scratch',
            },
            {
                'name': 'Web Development',
                'year': '1999',
                'institution': 'DEF Institute',
                'description': 'Learned Web Development from scratch',
            },
        ],
        'education': 'Bachelors',
        'experience': '5 years',
        'specializations': ['Python Programming', 'Web Development'],
    }
    return render_template('profile.html', user=user, role=role)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)