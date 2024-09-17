from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Course, Enrollment, Teacher, Student
from .. import db

course_views = Blueprint('course_views', __name__)

@course_views.route('/courses')
@login_required
def courses():
    """Display the user's courses."""
    if current_user.role == 'teacher':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        courses = Course.query.filter_by(teacher_id=teacher.id).all()
    else:
        student = Student.query.filter_by(user_id=current_user.id).first()
        courses = db.session.query(Course).join(Enrollment).filter(Enrollment.student_id == student.id).all()

    return render_template('courses.html', courses=courses)

@course_views.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    """Create a new course."""
    if current_user.role != 'teacher':
        flash('Only teachers can create courses.', 'danger')
        return redirect(url_for('course_views.courses'))

    if request.method == 'POST':
        # Use helper function from utils.py
        from ..utils import create_new_course
        success, message = create_new_course(request, current_user.id)
        if success:
            flash(message, 'success')
            return redirect(url_for('course_views.courses'))
        else:
            flash(message, 'danger')

    return render_template('create_course.html')

@course_views.route('/courses/browse')
@login_required
def browse_courses():
    """Display all available courses for students to browse."""
    if current_user.role != 'student':
        flash('Only students can browse courses.', 'danger')
        return redirect(url_for('courses'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    enrolled_courses = [enrollment.course_id for enrollment in Enrollment.query.filter_by(student_id=student.id).all()]
    available_courses = Course.query.filter(~Course.id.in_(enrolled_courses)).all()

    return render_template('browse_courses.html', courses=available_courses, user=current_user)

@course_views.route('/courses/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course."""
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

@course_views.route('/courses/unenroll/<int:course_id>', methods=['POST'])
@login_required
def unenroll_course(course_id):
    """Unenroll from a course."""
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

@course_views.route('/courses/description/<int:course_id>')
@login_required
def course_description(course_id):
    """Display the description of a course."""
    course = Course.query.get(course_id)
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    return render_template('course_description.html', course=course)

@course_views.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete a course."""
    if current_user.role != 'teacher':
        flash('Only teachers can delete courses.', 'danger')
        return redirect(url_for('courses'))

    course = Course.query.get(course_id)
    
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if course.teacher_id != teacher.id:
        flash('You are not authorized to delete this course.', 'danger')
        return redirect(url_for('courses'))

    try:
        db.session.delete(course)
        db.session.commit()
        flash(f'Course "{course.name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the course.', 'danger')
        print(e)

    return redirect(url_for('courses'))

@course_views.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit a course."""
    if current_user.role != 'teacher':
        flash('Only teachers can edit courses.', 'danger')
        return redirect(url_for('courses'))

    course = Course.query.get(course_id)
    
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if course.teacher_id != teacher.id:
        flash('You are not authorized to edit this course.', 'danger')
        return redirect(url_for('courses'))

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
            return redirect(url_for('courses'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the course.', 'danger')
            print(e)

    return render_template('edit_course.html', course=course)

@course_views.route('/courses/view/<int:course_id>')
@login_required
def view_course(course_id):
    """"View a course"""
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        flash('Course not found.', 'danger')
        return redirect(url_for('courses'))

    return render_template('view_course.html', course=course)
