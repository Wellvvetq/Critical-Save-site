import functools
from flask import session, redirect, url_for, flash, request, abort, current_app
from app.models import User
from app.services.db import get_db

def login_user(user: User):
    session.clear()
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

def logout_user():
    session.clear()

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    db = get_db()
    return db.session.query(User).filter_by(id=user_id, is_active=True).first()

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Authentication required to access studio control center.", "warning")
            return redirect(url_for("admin.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                flash("Authentication required to access studio control center.", "warning")
                return redirect(url_for("admin.login", next=request.path))
            user_role = session.get("role", "editor")
            # Map legacy 'admin' to 'owner' for backward compatibility
            effective_role = "owner" if user_role in ("owner", "admin") else user_role
            normalized_allowed = [r.lower() for r in allowed_roles]
            if effective_role not in normalized_allowed and "admin" not in normalized_allowed:
                flash("Permission denied. Action requires elevated authority (Owner).", "danger")
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def is_owner():
    role = session.get("role")
    return role in ("owner", "admin")

