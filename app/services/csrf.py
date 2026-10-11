import secrets
from flask import session, request, abort, current_app

def generate_csrf_token() -> str:
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

def validate_csrf_token():
    if current_app.config.get("TESTING") and not current_app.config.get("WTF_CSRF_ENABLED", False):
        return
    token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
    expected = session.get("_csrf_token")
    if not expected or not token or not secrets.compare_digest(token, expected):
        abort(400, description="CSRF token validation failed. Submission rejected.")
