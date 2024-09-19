from flask import Blueprint, render_template, request, url_for, redirect, flash, send_from_directory
from flask import current_app as app
from flask_login import login_user, login_required, current_user, logout_user
from . import db, login_manager, bcrypt, uploaded_files
from .models import User, Student, Teacher, Course, Enrollment

# Define the blueprint
main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('main.login'))
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
                return redirect(url_for('main.login'))
            except Exception as e:
                flash('Something went wrong. Please try again.')
                print(e)
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.courses'))
        else:
            flash('Login unsuccessful. Please check your email and password.')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    current_user_id = current_user.id
    user = User.query.filter_by(id=current_user_id).first()
    if request.method == 'POST':
        if request.form.get('_method') == 'DELETE':
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                db.session.delete(student)
            else:
                teacher = Teacher.query.filter_by(user_id=user.id).first()
                db.session.delete(teacher)
            db.session.delete(user)
            db.session.commit()
            flash('Profile deleted successfully', 'success')
            return redirect(url_for('main.index'))
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
        return redirect(url_for('main.profile'))
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

@main.route('/profile/edit')
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

@main.route('/courses')
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
        return redirect(url_for('main.index'))

@main.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'teacher':
        flash('Only teachers can create courses.', 'danger')
        return redirect(url_for('main.courses'))
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        pdf_files = request.files.getlist('syllabus_pdf[]')
        uploaded_pdfs = []
        for pdf in pdf_files:
            if pdf:
                pdf_filename = uploaded_files.save(pdf)
                uploaded_pdfs.append(pdf_filename)

        video_files = request.files.getlist('video[]')
        uploaded_videos = []
        for video in video_files:
            if video:
                video_filename = uploaded_files.save(video)
                uploaded_videos.append(video_filename)

        syllabus_pdf = ','.join(uploaded_pdfs) 
        video_link = ','.join(uploaded_videos)

        new_course = Course(name=name, code=code, description=description, teacher_id=teacher.id, syllabus_pdf=syllabus_pdf, video_link=video_link)
        db.session.add(new_course)
        db.session.commit()

        flash('Course created successfully!', 'success')
        return redirect(url_for('main.courses'))

    return render_template('create_course.html')

@main.route('/courses/browse')
@login_required
def browse_courses():
    if current_user.role != 'student':
        flash('Only students can browse courses.', 'danger')
        return redirect(url_for('main.courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    enrolled_courses = [enrollment.course_id for enrollment in Enrollment.query.filter_by(student_id=student.id).all()]
    available_courses = Course.query.filter(~Course.id.in_(enrolled_courses)).all()

    return render_template('browse_courses.html', courses=available_courses, user=current_user)

@main.route('/courses/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll in courses.', 'danger')
        return redirect(url_for('main.courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    course = Course.query.get(course_id)

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('main.browse_courses'))

    enrollment = Enrollment(student_id=student.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    flash(f'You have enrolled in {course.name}!', 'success')
    return redirect(url_for('main.courses'))

@main.route('/courses/unenroll/<int:course_id>', methods=['POST'])
@login_required
def unenroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can unenroll from courses.', 'danger')
        return redirect(url_for('main.courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    course = Course.query.get(course_id)

    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('main.courses'))

    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()

    if not enrollment:
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('main.courses'))

    db.session.delete(enrollment)
    db.session.commit()

    flash(f'You have successfully unenrolled from {course.name}.', 'success')
    return redirect(url_for('main.courses'))

@main.route('/courses/description/<int:course_id>')
@login_required
def course_description(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('main.courses'))

    return render_template('course_description.html', course=course)

@main.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'teacher':
        flash('Only teachers can delete courses.', 'danger')
        return redirect(url_for('main.courses'))

    course = Course.query.get(course_id)
    
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('main.courses'))

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if course.teacher_id != teacher.id:
        flash('You are not authorized to delete this course.', 'danger')
        return redirect(url_for('main.courses'))

    try:
        db.session.delete(course)
        db.session.commit()
        flash(f'Course "{course.name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the course.', 'danger')
        print(e)

    return redirect(url_for('main.courses'))

@main.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'teacher':
        flash('Only teachers can edit courses.', 'danger')
        return redirect(url_for('main.courses'))

    course = Course.query.get(course_id)
    
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('main.courses'))

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if course.teacher_id != teacher.id:
        flash('You are not authorized to edit this course.', 'danger')
        return redirect(url_for('main.courses'))

    if request.method == 'POST':
        course.name = request.form.get('name')
        course.code = request.form.get('code')
        course.description = request.form.get('description')

        pdf_files = request.files.getlist('syllabus_pdf[]')
        uploaded_pdfs = []
        for pdf in pdf_files:
            if pdf:
                pdf_filename = uploaded_files.save(pdf)
                uploaded_pdfs.append(pdf_filename)

        video_files = request.files.getlist('video[]')
        uploaded_videos = []
        for video in video_files:
            if video:
                video_filename = uploaded_files.save(video)
                uploaded_videos.append(video_filename)
        if course.syllabus_pdf:
            course.syllabus_pdf += ',' + ','.join(uploaded_pdfs) 
            course.video_link += ',' + ','.join(uploaded_videos)
        else:
            course.syllabus_pdf = ','.join(uploaded_pdfs)
            course.video_link = ','.join(uploaded_videos)

        try:
            db.session.commit()
            flash(f'Course "{course.name}" updated successfully.', 'success')
            return redirect(url_for('main.courses'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the course.', 'danger')
            print(e)

    return render_template('edit_course.html', course=course)

@main.route('/courses/view/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('main.courses'))

    return render_template('view_course.html', course=course)

@main.route('/download/<path:filename>')
@login_required
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOADS_DEFAULT_DEST'], f'files/{filename}', as_attachment=True)
    except Exception as e:
        flash('File not found.', 'danger')
        return redirect(url_for('main.courses'))
