import os
from flask import Flask, render_template, request, g
from config import Config
from app.services.db import Database, get_db
import app.services.db as db_module
from app.services.i18n import t

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize persistence
    database = Database(app.config["SQLALCHEMY_DATABASE_URI"])
    database.init_db()
    db_module.db = database

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Context processors
    from app.services.csrf import generate_csrf_token
    @app.context_processor
    def inject_global_vars():
        lang = getattr(g, "lang", "en")
        return {
            "current_lang": lang,
            "t": lambda key: t(key, lang),
            "site_title": "Critical Save Studio",
            "csrf_token": generate_csrf_token
        }

    # Teardown database session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = get_db()
        if db:
            db.session.remove()

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy allows self styles, fonts, inline SVGs
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline'; "
            "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com; "
            "frame-ancestors 'self';"
        )
        return response

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        lang = getattr(g, "lang", "en")
        return render_template(
            "errors/404.html",
            lang=lang,
            t=lambda k: t(k, lang),
            page_title="404 — Not Found"
        ), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        lang = getattr(g, "lang", "en")
        return render_template(
            "errors/500.html",
            lang=lang,
            t=lambda k: t(k, lang),
            page_title="500 — Server Error"
        ), 500

    return app
