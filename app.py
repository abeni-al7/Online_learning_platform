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
    courses = db.relationship('Course', secondary='enrollments', back_populates='students')

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    courses = db.relationship('Course', backref='teacher', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    students = db.relationship('Student', secondary='enrollments', back_populates='courses')

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    db.UniqueConstraint('student_id', 'course_id')

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
            flash('Login unsuccessful. Please check your email and password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    current_user_id = current_user.id
    user = User.query.filter_by(id=current_user_id).first()
    if request.method == 'POST':
        if request.form.get('_method') == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            flash('Profile deleted successfully', 'success')
            return redirect(url_for('index'))
        name = request.form.get('name')
        user.name = name
        db.session.commit()
        if user.role == 'teacher':
            bio = request.form.get('bio')
            education = request.form.get('education')
            experience = request.form.get('experience')
            teacher = Teacher.query.filter_by(user_id=current_user_id).first()
            teacher.bio = bio
            teacher.education = education
            teacher.experience = experience
            db.session.commit()
        elif user.role == 'student':
            grade = request.form.get('grade_level')
            bio = request.form.get('bio')
            student = Student.query.filter_by(user_id=current_user_id).first()
            student.grade = grade
            student.bio = bio
            db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    user = user.to_json()
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
    current_user_id = current_user.id
    user = User.query.filter_by(id=current_user_id).first()
    user = user.to_json()
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
    return render_template('edit_profile.html', user=user, role=role)

@app.route('/courses')
@login_required
def courses():
    if current_user.role == 'teacher':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        created_courses = Course.query.filter_by(teacher_id=teacher.id).all()
        return render_template('courses.html', role='teacher', courses=created_courses, user=current_user)
    
    elif current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        enrolled_courses = db.session.query(Course).join(Enrollment).filter(Enrollment.student_id == student.id).all()
        return render_template('courses.html', role='student', courses=enrolled_courses, user=current_user)

    else:
        flash('Invalid role.', 'danger')
        return redirect(url_for('index'))

@app.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'teacher':
        flash('Only teachers can create courses.', 'danger')
        return redirect(url_for('courses'))
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()

        new_course = Course(name=name, code=code, description=description, teacher_id=teacher.id)
        db.session.add(new_course)
        db.session.commit()

        flash('Course created successfully!', 'success')
        return redirect(url_for('courses'))

    return render_template('create_course.html')

@app.route('/courses/browse')
@login_required
def browse_courses():
    if current_user.role != 'student':
        flash('Only students can browse courses.', 'danger')
        return redirect(url_for('courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    enrolled_courses = [enrollment.course_id for enrollment in Enrollment.query.filter_by(student_id=student.id).all()]
    available_courses = Course.query.filter(~Course.id.in_(enrolled_courses)).all()

    return render_template('browse_courses.html', courses=available_courses, user=current_user)

@app.route('/courses/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll in courses.', 'danger')
        return redirect(url_for('courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    course = Course.query.get(course_id)

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('browse_courses'))

    enrollment = Enrollment(student_id=student.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    flash(f'You have enrolled in {course.name}!', 'success')
    return redirect(url_for('courses'))

@app.route('/courses/unenroll/<int:course_id>', methods=['POST'])
@login_required
def unenroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can unenroll from courses.', 'danger')
        return redirect(url_for('courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    course = Course.query.get(course_id)

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()

    if not enrollment:
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('courses'))

    db.session.delete(enrollment)
    db.session.commit()

    flash(f'You have successfully unenrolled from {course.name}.', 'success')
    return redirect(url_for('courses'))

@app.route('/courses/description/<int:course_id>')
@login_required
def course_description(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    return render_template('course_description.html', course=course)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)