from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import User, Student, Teacher
from .. import db

profile_views = Blueprint('profile_views', __name__)

@profile_views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Display the user's profile."""
    from ..utils import update_profile
    
    if request.method == 'POST':
        success, message = update_profile(current_user)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('profile_views.profile'))
    
    user = current_user.to_json()
    return render_template('profile.html', user=user)

@profile_views.route('/profile/edit')
@login_required
def edit_profile():
    """Display the form to edit the user's profile."""
    user = current_user.to_json()
    return render_template('edit_profile.html', user=user)
