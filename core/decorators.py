from functools import wraps
from flask import redirect, url_for, flash, abort, session, request
from flask_login import current_user

def admin_only(f):
    """
    Ensures that the accessing user is logged in and possesses administrator privileges.
    Checks flask-login current_user attributes as well as session role markers.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Flask-Login session check
        if getattr(current_user, 'is_authenticated', False):
            if getattr(current_user, 'is_admin', False) or getattr(current_user, 'role', '').lower() in ['admin', 'superadmin', 'warden']:
                return f(*args, **kwargs)
        
        # 2. Raw session check fallback
        if session.get('is_admin') or session.get('role') in ['admin', 'superadmin', 'warden'] or session.get('management_logged_in'):
            return f(*args, **kwargs)

        flash("Administrative clearance required to access this hangar sector.", "danger")
        return redirect(url_for('auth.login', next=request.url))
    return decorated_function

def role_required(*roles):
    """
    Generalized decorator to require specific roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(current_user, 'role', None) or session.get('role')
            if user_role in roles:
                return f(*args, **kwargs)
            abort(403)
        return decorated_function
    return decorator
