from . import db
from flask_login import UserMixin

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
    enrollments = db.relationship('Enrollment', cascade='all, delete', backref='student')

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    courses = db.relationship('Course', backref='teacher', lazy=True, cascade="all, delete-orphan")

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    students = db.relationship('Student', secondary='enrollments', back_populates='courses')
    syllabus_pdf = db.Column(db.Text)
    video_link = db.Column(db.Text)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    db.UniqueConstraint('student_id', 'course_id')
