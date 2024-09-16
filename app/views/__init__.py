"""A module for registering the blueprints."""
from .auth_views import auth_views
from .profile_views import profile_views
from .course_views import course_views
from .utility_views import utility_views

def register_blueprints(app):
    """Register the blueprints with the Flask app."""
    app.register_blueprint(auth_views)
    app.register_blueprint(profile_views)
    app.register_blueprint(course_views)
    app.register_blueprint(utility_views)
