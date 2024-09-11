import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, current_user, logout_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=True)
    role = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=True)

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'name': self.name,
        }

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grade = db.Column(db.Text)
    bio = db.Column(db.Text)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

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
        user = User.query.filter_by(email=email).first()
        if user:
            flash('You are already registered. Please Login', 'fail')
            return redirect(url_for('login'))
        if password != confirm:
            flash('Passwords don\'t match')
            print('Passwords don\'t match')
        else:
            try:
                new_user = User(email=email, password=hashed_password, username=username, role=role, name=name)
                db.session.add(new_user)
                db.session.commit()
                if role == 'teacher':
                    new_teacher = Teacher(user_id=new_user.id)
                    db.session.add(new_teacher)
                    db.session.commit()
                elif role == 'student':
                    new_student = Student(user_id=new_user.id)
                    db.session.add(new_student)
                    db.session.commit()
                flash('You have been registered successfully. Please Login', 'success')
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
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('courses'))
        else:
            flash('Login unsuccessful. Please check your username and password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    current_user_id = current_user.id
    user = User.query.filter_by(id=current_user_id).first()
    user = user.to_json()
    print(user)
    if user['role'] == 'teacher':
        teacher = Teacher.query.filter_by(user_id=current_user_id).first()
        role = 'teacher'
        user['bio'] = teacher.bio
        user['education'] = teacher.education
        user['experience'] = teacher.experience
    elif user['role'] == 'student':
        student = Student.query.filter_by(user_id=current_user_id).first()
        role = 'student'
        user['grade'] = student.grade
        user['bio'] = student.bio
    return render_template('profile.html', user=user, role=role)

@app.route('/profile/edit')
@login_required
def edit_profile():
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
    return render_template('edit_profile.html', user=user, role=role)

@app.route('/courses')
@login_required
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
@login_required
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
@login_required
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
@login_required
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)