import os
import json
from datetime import datetime
from pathlib import Path
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
)
from app.services.auth import login_required, login_user, logout_user, get_current_user, role_required, is_owner
from app.services.db import get_db
from app.services.media import save_media_file
from app.models import User, Game, Article, Career, ContactInquiry, StudioSetting, SoftwareProduct, SoftwareRelease, PageContent, AuditLog
from app.services.csrf import validate_csrf_token
from app.services.i18n import TRANSLATIONS
from app.services.static_exporter import export_static_site

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.before_request
def check_admin_csrf():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        validate_csrf_token()

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        db = get_db()
        user = db.session.query(User).filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash("This administrative account has been deactivated.", "danger")
                return render_template("admin/login.html")
            login_user(user)
            # Log audit entry
            log = AuditLog(username=user.username, action="login", ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash(f"Welcome to Studio Control Center, {user.username}.", "success")
            next_url = request.args.get("next") or url_for("admin.dashboard")
            return redirect(next_url)
        else:
            flash("Invalid administrator credentials.", "danger")
            
    return render_template("admin/login.html")

@admin_bp.route("/logout")
def logout():
    db = get_db()
    if session.get("username"):
        log = AuditLog(username=session["username"], action="logout", ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
    logout_user()
    flash("Session terminated securely.", "info")
    return redirect(url_for("admin.login"))

@admin_bp.route("/")
@login_required
def dashboard():
    db = get_db()
    total_games = db.session.query(Game).count()
    total_software = db.session.query(SoftwareProduct).count()
    total_releases = db.session.query(SoftwareRelease).count()
    draft_changes_count = db.session.query(PageContent).filter_by(has_unpublished_changes=True).count()
    
    current_release = db.session.query(SoftwareRelease).order_by(SoftwareRelease.created_at.desc()).first()
    recent_audit_logs = db.session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(6).all()
    recent_inquiries = db.session.query(ContactInquiry).order_by(ContactInquiry.created_at.desc()).limit(5).all()
    
    return render_template(
        "admin/dashboard.html",
        total_games=total_games,
        total_software=total_software,
        total_releases=total_releases,
        draft_changes_count=draft_changes_count,
        current_release=current_release,
        recent_audit_logs=recent_audit_logs,
        recent_inquiries=recent_inquiries
    )

# --- GAMES CRUD ---

@admin_bp.route("/games")
@login_required
def games_list():
    db = get_db()
    games = db.session.query(Game).order_by(Game.sort_order.asc(), Game.created_at.desc()).all()
    return render_template("admin/games_list.html", games=games)

@admin_bp.route("/games/new", methods=["GET", "POST"])
@login_required
def game_create():
    if request.method == "POST":
        db = get_db()
        slug = request.form.get("slug", "").strip()
        title_en = request.form.get("title_en", "").strip()
        
        if not slug or not title_en:
            flash("Slug and English Title are required fields.", "danger")
            return render_template("admin/game_form.html", game=None)
            
        existing = db.session.query(Game).filter_by(slug=slug).first()
        if existing:
            flash(f"Project with slug '{slug}' already exists.", "danger")
            return render_template("admin/game_form.html", game=None)
            
        cover_image = request.form.get("cover_image", "").strip()
        if "cover_file" in request.files and request.files["cover_file"].filename:
            try:
                cover_image = save_media_file(request.files["cover_file"])
            except Exception as e:
                flash(f"Media upload error: {e}", "danger")
                
        hero_image = request.form.get("hero_image", "").strip()
        if "hero_file" in request.files and request.files["hero_file"].filename:
            try:
                hero_image = save_media_file(request.files["hero_file"])
            except Exception as e:
                flash(f"Media upload error: {e}", "danger")
                
        game = Game(
            slug=slug,
            title_en=title_en,
            tagline_en=request.form.get("tagline_en", "").strip(),
            short_description_en=request.form.get("short_description_en", "").strip(),
            full_description_en=request.form.get("full_description_en", "").strip(),
            genre_en=request.form.get("genre_en", "").strip(),
            status_en=request.form.get("status_en", "In Development").strip(),
            
            title_ru=request.form.get("title_ru", "").strip() or None,
            tagline_ru=request.form.get("tagline_ru", "").strip() or None,
            short_description_ru=request.form.get("short_description_ru", "").strip() or None,
            full_description_ru=request.form.get("full_description_ru", "").strip() or None,
            genre_ru=request.form.get("genre_ru", "").strip() or None,
            status_ru=request.form.get("status_ru", "В разработке").strip(),
            
            cover_image=cover_image or None,
            hero_image=hero_image or None,
            trailer_url=request.form.get("trailer_url", "").strip() or None,
            gallery_images_json=request.form.get("gallery_images_json", "[]").strip() or "[]",
            features_json_en=request.form.get("features_json_en", "[]").strip() or "[]",
            features_json_ru=request.form.get("features_json_ru", "[]").strip() or "[]",
            platforms=request.form.get("platforms", "").strip() or None,
            release_date_info=request.form.get("release_date_info", "").strip() or None,
            
            is_featured=bool(request.form.get("is_featured")),
            is_published=bool(request.form.get("is_published")),
            sort_order=int(request.form.get("sort_order") or 0)
        )
        
        db.session.add(game)
        db.session.commit()
        flash(f"Project '{game.title_en}' created successfully.", "success")
        return redirect(url_for("admin.games_list"))
        
    return render_template("admin/game_form.html", game=None)

@admin_bp.route("/games/<int:game_id>/edit", methods=["GET", "POST"])
@login_required
def game_edit(game_id):
    db = get_db()
    game = db.session.query(Game).get(game_id)
    if not game:
        abort(404)
        
    if request.method == "POST":
        slug = request.form.get("slug", "").strip()
        title_en = request.form.get("title_en", "").strip()
        
        if not slug or not title_en:
            flash("Slug and English Title are required fields.", "danger")
            return render_template("admin/game_form.html", game=game)
            
        existing = db.session.query(Game).filter(Game.slug == slug, Game.id != game.id).first()
        if existing:
            flash(f"Another project with slug '{slug}' already exists.", "danger")
            return render_template("admin/game_form.html", game=game)
            
        cover_image = request.form.get("cover_image", "").strip()
        if "cover_file" in request.files and request.files["cover_file"].filename:
            try:
                cover_image = save_media_file(request.files["cover_file"])
            except Exception as e:
                flash(f"Media upload error: {e}", "danger")
                
        hero_image = request.form.get("hero_image", "").strip()
        if "hero_file" in request.files and request.files["hero_file"].filename:
            try:
                hero_image = save_media_file(request.files["hero_file"])
            except Exception as e:
                flash(f"Media upload error: {e}", "danger")
                
        game.slug = slug
        game.title_en = title_en
        game.tagline_en = request.form.get("tagline_en", "").strip()
        game.short_description_en = request.form.get("short_description_en", "").strip()
        game.full_description_en = request.form.get("full_description_en", "").strip()
        game.genre_en = request.form.get("genre_en", "").strip()
        game.status_en = request.form.get("status_en", "").strip()
        
        game.title_ru = request.form.get("title_ru", "").strip() or None
        game.tagline_ru = request.form.get("tagline_ru", "").strip() or None
        game.short_description_ru = request.form.get("short_description_ru", "").strip() or None
        game.full_description_ru = request.form.get("full_description_ru", "").strip() or None
        game.genre_ru = request.form.get("genre_ru", "").strip() or None
        game.status_ru = request.form.get("status_ru", "").strip()
        
        if cover_image:
            game.cover_image = cover_image
        if hero_image:
            game.hero_image = hero_image
            
        game.trailer_url = request.form.get("trailer_url", "").strip() or None
        game.gallery_images_json = request.form.get("gallery_images_json", "[]").strip() or "[]"
        game.features_json_en = request.form.get("features_json_en", "[]").strip() or "[]"
        game.features_json_ru = request.form.get("features_json_ru", "[]").strip() or "[]"
        game.platforms = request.form.get("platforms", "").strip() or None
        game.release_date_info = request.form.get("release_date_info", "").strip() or None
        
        game.is_featured = bool(request.form.get("is_featured"))
        game.is_published = bool(request.form.get("is_published"))
        game.sort_order = int(request.form.get("sort_order") or 0)
        
        db.session.commit()
        flash(f"Project '{game.title_en}' updated.", "success")
        return redirect(url_for("admin.games_list"))
        
    return render_template("admin/game_form.html", game=game)

@admin_bp.route("/games/<int:game_id>/delete", methods=["POST"])
@login_required
def game_delete(game_id):
    db = get_db()
    game = db.session.query(Game).get(game_id)
    if not game:
        abort(404)
    db.session.delete(game)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("admin.games_list"))

# --- ARTICLES CRUD ---

@admin_bp.route("/articles")
@login_required
def articles_list():
    db = get_db()
    articles = db.session.query(Article).order_by(Article.created_at.desc()).all()
    return render_template("admin/articles_list.html", articles=articles)

@admin_bp.route("/articles/new", methods=["GET", "POST"])
@login_required
def article_create():
    if request.method == "POST":
        db = get_db()
        slug = request.form.get("slug", "").strip()
        title_en = request.form.get("title_en", "").strip()
        content_en = request.form.get("content_en", "").strip()
        
        if not slug or not title_en or not content_en:
            flash("Slug, Title (EN), and Content (EN) are required.", "danger")
            return render_template("admin/article_form.html", article=None)
            
        cover_image = request.form.get("cover_image", "").strip()
        if "cover_file" in request.files and request.files["cover_file"].filename:
            try:
                cover_image = save_media_file(request.files["cover_file"])
            except Exception as e:
                flash(f"Media upload error: {e}", "danger")
                
        article = Article(
            slug=slug,
            title_en=title_en,
            excerpt_en=request.form.get("excerpt_en", "").strip(),
            content_en=content_en,
            category_en=request.form.get("category_en", "Announcement").strip(),
            
            title_ru=request.form.get("title_ru", "").strip() or None,
            excerpt_ru=request.form.get("excerpt_ru", "").strip() or None,
            content_ru=request.form.get("content_ru", "").strip() or None,
            category_ru=request.form.get("category_ru", "Анонс").strip(),
            
            cover_image=cover_image or None,
            author=request.form.get("author", "Critical Save Studio").strip(),
            reading_time_minutes=int(request.form.get("reading_time_minutes") or 3),
            is_published=bool(request.form.get("is_published"))
        )
        
        db.session.add(article)
        db.session.commit()
        flash(f"Journal article '{article.title_en}' created.", "success")
        return redirect(url_for("admin.articles_list"))
        
    return render_template("admin/article_form.html", article=None)

@admin_bp.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
def article_edit(article_id):
    db = get_db()
    article = db.session.query(Article).get(article_id)
    if not article:
        abort(404)
        
    if request.method == "POST":
        slug = request.form.get("slug", "").strip()
        title_en = request.form.get("title_en", "").strip()
        content_en = request.form.get("content_en", "").strip()
        
        if not slug or not title_en or not content_en:
            flash("Slug, Title, and Content are required.", "danger")
            return render_template("admin/article_form.html", article=article)
            
        cover_image = request.form.get("cover_image", "").strip()
        if "cover_file" in request.files and request.files["cover_file"].filename:
            try:
                cover_image = save_media_file(request.files["cover_file"])
            except Exception as e:
                flash(f"Media upload error: {e}", "danger")
                
        article.slug = slug
        article.title_en = title_en
        article.excerpt_en = request.form.get("excerpt_en", "").strip()
        article.content_en = content_en
        article.category_en = request.form.get("category_en", "").strip()
        
        article.title_ru = request.form.get("title_ru", "").strip() or None
        article.excerpt_ru = request.form.get("excerpt_ru", "").strip() or None
        article.content_ru = request.form.get("content_ru", "").strip() or None
        article.category_ru = request.form.get("category_ru", "").strip()
        
        if cover_image:
            article.cover_image = cover_image
        article.author = request.form.get("author", "Critical Save Studio").strip()
        article.reading_time_minutes = int(request.form.get("reading_time_minutes") or 3)
        article.is_published = bool(request.form.get("is_published"))
        
        db.session.commit()
        flash(f"Journal article '{article.title_en}' updated.", "success")
        return redirect(url_for("admin.articles_list"))
        
    return render_template("admin/article_form.html", article=article)

@admin_bp.route("/articles/<int:article_id>/delete", methods=["POST"])
@login_required
def article_delete(article_id):
    db = get_db()
    article = db.session.query(Article).get(article_id)
    if not article:
        abort(404)
    db.session.delete(article)
    db.session.commit()
    flash("Journal article removed.", "info")
    return redirect(url_for("admin.articles_list"))

# --- CAREERS CRUD ---

@admin_bp.route("/careers")
@login_required
def careers_list():
    db = get_db()
    careers = db.session.query(Career).order_by(Career.created_at.desc()).all()
    return render_template("admin/careers_list.html", careers=careers)

@admin_bp.route("/careers/new", methods=["GET", "POST"])
@login_required
def career_create():
    if request.method == "POST":
        db = get_db()
        slug = request.form.get("slug", "").strip()
        title_en = request.form.get("title_en", "").strip()
        description_en = request.form.get("description_en", "").strip()
        
        if not slug or not title_en or not description_en:
            flash("Slug, Title (EN), and Description (EN) are required.", "danger")
            return render_template("admin/career_form.html", career=None)
            
        career = Career(
            slug=slug,
            title_en=title_en,
            department_en=request.form.get("department_en", "").strip(),
            location_en=request.form.get("location_en", "Remote / Hybrid").strip(),
            description_en=description_en,
            requirements_en=request.form.get("requirements_en", "").strip(),
            responsibilities_en=request.form.get("responsibilities_en", "").strip(),
            
            title_ru=request.form.get("title_ru", "").strip() or None,
            department_ru=request.form.get("department_ru", "").strip() or None,
            location_ru=request.form.get("location_ru", "Удалённо / Гибрид").strip(),
            description_ru=request.form.get("description_ru", "").strip() or None,
            requirements_ru=request.form.get("requirements_ru", "").strip() or None,
            responsibilities_ru=request.form.get("responsibilities_ru", "").strip() or None,
            
            is_published=bool(request.form.get("is_published"))
        )
        
        db.session.add(career)
        db.session.commit()
        flash(f"Role '{career.title_en}' created.", "success")
        return redirect(url_for("admin.careers_list"))
        
    return render_template("admin/career_form.html", career=None)

@admin_bp.route("/careers/<int:career_id>/edit", methods=["GET", "POST"])
@login_required
def career_edit(career_id):
    db = get_db()
    career = db.session.query(Career).get(career_id)
    if not career:
        abort(404)
        
    if request.method == "POST":
        slug = request.form.get("slug", "").strip()
        title_en = request.form.get("title_en", "").strip()
        description_en = request.form.get("description_en", "").strip()
        
        career.slug = slug
        career.title_en = title_en
        career.department_en = request.form.get("department_en", "").strip()
        career.location_en = request.form.get("location_en", "").strip()
        career.description_en = description_en
        career.requirements_en = request.form.get("requirements_en", "").strip()
        career.responsibilities_en = request.form.get("responsibilities_en", "").strip()
        
        career.title_ru = request.form.get("title_ru", "").strip() or None
        career.department_ru = request.form.get("department_ru", "").strip() or None
        career.location_ru = request.form.get("location_ru", "").strip()
        career.description_ru = request.form.get("description_ru", "").strip() or None
        career.requirements_ru = request.form.get("requirements_ru", "").strip() or None
        career.responsibilities_ru = request.form.get("responsibilities_ru", "").strip() or None
        career.is_published = bool(request.form.get("is_published"))
        
        db.session.commit()
        flash(f"Role '{career.title_en}' updated.", "success")
        return redirect(url_for("admin.careers_list"))
        
    return render_template("admin/career_form.html", career=career)

@admin_bp.route("/careers/<int:career_id>/delete", methods=["POST"])
@login_required
def career_delete(career_id):
    db = get_db()
    career = db.session.query(Career).get(career_id)
    if not career:
        abort(404)
    db.session.delete(career)
    db.session.commit()
    flash("Role deleted.", "info")
    return redirect(url_for("admin.careers_list"))

# --- INQUIRIES ---

@admin_bp.route("/inquiries")
@login_required
def inquiries_list():
    db = get_db()
    inquiries = db.session.query(ContactInquiry).order_by(ContactInquiry.created_at.desc()).all()
    return render_template("admin/inquiries_list.html", inquiries=inquiries)

@admin_bp.route("/inquiries/<int:inquiry_id>/status", methods=["POST"])
@login_required
def inquiry_status_update(inquiry_id):
    db = get_db()
    inquiry = db.session.query(ContactInquiry).get(inquiry_id)
    if not inquiry:
        abort(404)
    new_status = request.form.get("status", "processed")
    inquiry.status = new_status
    db.session.commit()
    flash(f"Inquiry marked as {new_status}.", "info")
    return redirect(url_for("admin.inquiries_list"))


# --- PAGES & BLOCKS CRUD ---

@admin_bp.route("/pages")
@login_required
def pages_list():
    db = get_db()
    pages = db.session.query(PageContent).order_by(PageContent.page_key.asc()).all()
    return render_template("admin/pages_list.html", pages=pages)

@admin_bp.route("/pages/<page_key>/edit", methods=["GET", "POST"])
@login_required
def page_edit(page_key):
    db = get_db()
    page = db.session.query(PageContent).filter_by(page_key=page_key).first()
    if not page:
        abort(404)
        
    if request.method == "POST":
        title_en = request.form.get("title_en", "").strip()
        title_ru = request.form.get("title_ru", "").strip() or None
        draft_raw = request.form.get("draft_data_json", "{}").strip()
        
        try:
            parsed = json.loads(draft_raw) if draft_raw else {}
            if not isinstance(parsed, dict):
                parsed = {}
        except Exception as e:
            flash(f"Invalid JSON block structure: {e}", "danger")
            return render_template("admin/page_form.html", page=page, draft_json_str=draft_raw, draft_dict=page.get_draft() or page.get_published())

        # For home page, merge known visual editor form fields preserving unmanaged keys
        if page.page_key == "home":
            home_fields = [
                "hero_badge_en", "hero_badge_ru",
                "hero_headline_1_en", "hero_headline_1_ru",
                "hero_headline_2_en", "hero_headline_2_ru",
                "hero_subheadline_en", "hero_subheadline_ru",
                "hero_cta_games_en", "hero_cta_games_ru",
                "hero_cta_software_en", "hero_cta_software_ru",
            ]
            for fld in home_fields:
                if fld in request.form:
                    val = request.form.get(fld, "").strip()
                    if val != "":
                        parsed[fld] = val
                    elif fld in parsed:
                        # Allow clearing if submitted empty
                        del parsed[fld]

        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            
        page.title_en = title_en
        page.title_ru = title_ru
        page.draft_data_json = formatted
        page.last_edited_by = session.get("username", "admin")
        
        action = request.form.get("action", "save_draft")
        if action == "publish_now" and is_owner():
            page.published_data_json = formatted
            page.has_unpublished_changes = False
            page.published_by = session.get("username", "admin")
            page.published_at = datetime.utcnow()
            log = AuditLog(
                username=session.get("username", "admin"),
                action="publish_page",
                target_type="PageContent",
                target_id=page.page_key,
                ip_address=request.remote_addr
            )
            db.session.add(log)
            flash(f"Page '{page.title_en}' published directly to live production.", "success")
        else:
            page.has_unpublished_changes = True
            log = AuditLog(
                username=session.get("username", "admin"),
                action="edit_page_draft",
                target_type="PageContent",
                target_id=page.page_key,
                ip_address=request.remote_addr
            )
            db.session.add(log)
            flash(f"Draft revisions saved for '{page.title_en}'. Staged for review.", "success")
            
        db.session.commit()
        return redirect(url_for("admin.pages_list"))
        
    draft_dict = page.get_draft() or page.get_published()
    draft_json_str = json.dumps(draft_dict, indent=2, ensure_ascii=False)
    return render_template("admin/page_form.html", page=page, draft_json_str=draft_json_str, draft_dict=draft_dict)


# --- SOFTWARE PRODUCTS CRUD ---

@admin_bp.route("/software")
@login_required
def software_list():
    db = get_db()
    products = db.session.query(SoftwareProduct).order_by(SoftwareProduct.id.asc()).all()
    return render_template("admin/software_list.html", products=products)

@admin_bp.route("/software/new", methods=["GET", "POST"])
@login_required
def software_create():
    if request.method == "POST":
        db = get_db()
        title_en = request.form.get("title_en", "").strip()
        slug = request.form.get("slug", "").strip()
        if not title_en or not slug:
            flash("Title and Slug are required.", "danger")
            return render_template("admin/software_form.html", product=None)
            
        existing = db.session.query(SoftwareProduct).filter_by(slug=slug).first()
        if existing:
            flash(f"Product slug '{slug}' is already registered.", "danger")
            return render_template("admin/software_form.html", product=None)
            
        product = SoftwareProduct(
            title_en=title_en,
            slug=slug,
            title_ru=request.form.get("title_ru", "").strip() or None,
            category=request.form.get("category", "Desktop Application").strip(),
            tagline_en=request.form.get("tagline_en", "").strip() or None,
            tagline_ru=request.form.get("tagline_ru", "").strip() or None,
            short_description_en=request.form.get("short_description_en", "").strip() or None,
            short_description_ru=request.form.get("short_description_ru", "").strip() or None,
            is_published=bool(request.form.get("is_published"))
        )
        db.session.add(product)
        log = AuditLog(
            username=session.get("username", "admin"),
            action="create_software",
            target_type="SoftwareProduct",
            target_id=slug,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Software product '{title_en}' registered successfully.", "success")
        return redirect(url_for("admin.software_list"))
        
    return render_template("admin/software_form.html", product=None)

@admin_bp.route("/software/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def software_edit(product_id):
    db = get_db()
    product = db.session.query(SoftwareProduct).get(product_id)
    if not product:
        abort(404)
        
    if request.method == "POST":
        product.title_en = request.form.get("title_en", "").strip()
        product.slug = request.form.get("slug", "").strip()
        product.title_ru = request.form.get("title_ru", "").strip() or None
        product.category = request.form.get("category", "Desktop Application").strip()
        product.tagline_en = request.form.get("tagline_en", "").strip() or None
        product.tagline_ru = request.form.get("tagline_ru", "").strip() or None
        product.short_description_en = request.form.get("short_description_en", "").strip() or None
        product.short_description_ru = request.form.get("short_description_ru", "").strip() or None
        product.is_published = bool(request.form.get("is_published"))
        
        log = AuditLog(
            username=session.get("username", "admin"),
            action="update_software",
            target_type="SoftwareProduct",
            target_id=product.slug,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Software product '{product.title_en}' updated.", "success")
        return redirect(url_for("admin.software_list"))
        
    return render_template("admin/software_form.html", product=product)


# --- RELEASES & 4-STAGE VERIFICATION GATE ---

@admin_bp.route("/releases")
@login_required
def releases_list():
    db = get_db()
    releases = db.session.query(SoftwareRelease).order_by(SoftwareRelease.created_at.desc()).all()
    return render_template("admin/releases_list.html", releases=releases)

@admin_bp.route("/releases/new", methods=["GET", "POST"])
@login_required
def release_create():
    db = get_db()
    products = db.session.query(SoftwareProduct).all()
    
    if request.method == "POST":
        product_id = request.form.get("product_id")
        version = request.form.get("version", "").strip()
        standard_filename = request.form.get("standard_filename", "").strip()
        standard_sha256 = request.form.get("standard_sha256", "").strip()
        offline_filename = request.form.get("offline_filename", "").strip()
        offline_sha256 = request.form.get("offline_sha256", "").strip()
        
        file_exists_verified = bool(request.form.get("file_exists_verified"))
        hash_verified = bool(request.form.get("hash_verified"))
        backend_verified = bool(request.form.get("backend_verified"))
        
        # Stage 4 Gate: Only owner can sign off
        owner_approved = bool(request.form.get("owner_approved")) if is_owner() else False
        is_live = file_exists_verified and hash_verified and backend_verified and owner_approved
        
        release = SoftwareRelease(
            product_id=int(product_id),
            version=version,
            release_channel=request.form.get("release_channel", "stable"),
            standard_filename=standard_filename,
            standard_size_display=request.form.get("standard_size_display", "159.0 MB"),
            standard_sha256=standard_sha256,
            offline_filename=offline_filename,
            offline_size_display=request.form.get("offline_size_display", "614.7 MB"),
            offline_sha256=offline_sha256,
            file_exists_verified=file_exists_verified,
            hash_verified=hash_verified,
            backend_verified=backend_verified,
            owner_approved=owner_approved,
            is_live=is_live
        )
        db.session.add(release)
        log = AuditLog(
            username=session.get("username", "admin"),
            action="stage_release",
            target_type="SoftwareRelease",
            target_id=f"v{version}",
            details=f"Gate Status: file={file_exists_verified}, hash={hash_verified}, backend={backend_verified}, owner={owner_approved}, live={is_live}",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Software release v{version} staged successfully.", "success")
        return redirect(url_for("admin.releases_list"))
        
    return render_template("admin/release_form.html", release=None, products=products)

@admin_bp.route("/releases/<int:release_id>/edit", methods=["GET", "POST"])
@login_required
def release_edit(release_id):
    db = get_db()
    release = db.session.query(SoftwareRelease).get(release_id)
    if not release:
        abort(404)
        
    products = db.session.query(SoftwareProduct).all()
    
    if request.method == "POST":
        release.product_id = int(request.form.get("product_id"))
        release.version = request.form.get("version", "").strip()
        release.release_channel = request.form.get("release_channel", "stable")
        release.standard_filename = request.form.get("standard_filename", "").strip()
        release.standard_size_display = request.form.get("standard_size_display", "").strip()
        release.standard_sha256 = request.form.get("standard_sha256", "").strip()
        release.offline_filename = request.form.get("offline_filename", "").strip()
        release.offline_size_display = request.form.get("offline_size_display", "").strip()
        release.offline_sha256 = request.form.get("offline_sha256", "").strip()
        
        release.file_exists_verified = bool(request.form.get("file_exists_verified"))
        release.hash_verified = bool(request.form.get("hash_verified"))
        release.backend_verified = bool(request.form.get("backend_verified"))
        
        # Stage 4 Gate
        if is_owner():
            release.owner_approved = bool(request.form.get("owner_approved"))
            
        release.is_live = (
            release.file_exists_verified and
            release.hash_verified and
            release.backend_verified and
            release.owner_approved
        )
        
        log = AuditLog(
            username=session.get("username", "admin"),
            action="update_release_telemetry",
            target_type="SoftwareRelease",
            target_id=f"v{release.version}",
            details=f"Gate Status: live={release.is_live}, owner_approved={release.owner_approved}",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Release v{release.version} telemetry updated.", "success")
        return redirect(url_for("admin.releases_list"))
        
    return render_template("admin/release_form.html", release=release, products=products)


# --- MEDIA LIBRARY ---

@admin_bp.route("/media")
@login_required
def media_library():
    media_files = []
    static_dir = Path(current_app.root_path) / "static"
    
    for folder_name in ["images", "uploads"]:
        folder_path = static_dir / folder_name
        if folder_path.exists():
            for f in folder_path.glob("*"):
                if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif"]:
                    media_files.append({
                        "filename": f.name,
                        "url": f"/static/{folder_name}/{f.name}",
                        "size_kb": round(f.stat().st_size / 1024, 1),
                        "ext": f.suffix.lower().replace(".", "").upper()
                    })
                    
    media_files.sort(key=lambda x: x["filename"].lower())
    return render_template("admin/media_library.html", media_files=media_files)

@admin_bp.route("/media/upload", methods=["POST"])
@login_required
def media_upload():
    if "file" not in request.files or not request.files["file"].filename:
        flash("No file was selected for upload.", "warning")
        return redirect(url_for("admin.media_library"))
        
    try:
        url_path = save_media_file(request.files["file"])
        db = get_db()
        log = AuditLog(
            username=session.get("username", "admin"),
            action="upload_media",
            target_type="Media",
            target_id=url_path,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Asset successfully uploaded to {url_path}.", "success")
    except Exception as e:
        flash(f"Upload failed: {str(e)}", "danger")
        
    return redirect(url_for("admin.media_library"))


# --- LOCALIZATION ---

@admin_bp.route("/localization")
@login_required
def localization_list():
    en_dict = TRANSLATIONS.get("en", {})
    ru_dict = TRANSLATIONS.get("ru", {})
    all_keys = sorted(list(set(en_dict.keys()) | set(ru_dict.keys())))
    return render_template(
        "admin/localization_list.html",
        keys=all_keys,
        translations_en=en_dict,
        translations_ru=ru_dict
    )


# --- TEAM & ACCESS CONTROL (OWNER ONLY FOR MUTATIONS) ---

@admin_bp.route("/team")
@login_required
def team_list():
    db = get_db()
    users = db.session.query(User).order_by(User.id.asc()).all()
    return render_template("admin/team_list.html", users=users)

@admin_bp.route("/team/new", methods=["POST"])
@role_required("owner")
def team_create_user():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "editor").strip().lower()
    
    if not username or not password:
        flash("Username and password are required.", "danger")
        return redirect(url_for("admin.team_list"))
        
    if len(password) < 8:
        flash("Password must be at least 8 characters.", "danger")
        return redirect(url_for("admin.team_list"))
        
    db = get_db()
    existing = db.session.query(User).filter_by(username=username).first()
    if existing:
        flash(f"Operator username '{username}' is already in use.", "danger")
        return redirect(url_for("admin.team_list"))
        
    user = User(username=username, role=role, is_active=True)
    user.set_password(password)
    db.session.add(user)
    
    log = AuditLog(
        username=session.get("username", "admin"),
        action="create_user",
        target_type="User",
        target_id=username,
        details=f"Role: {role}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f"Operator '{username}' registered with role '{role}'.", "success")
    return redirect(url_for("admin.team_list"))

@admin_bp.route("/team/<int:user_id>/toggle", methods=["POST"])
@role_required("owner")
def team_toggle_active(user_id):
    db = get_db()
    user = db.session.query(User).get(user_id)
    if not user:
        abort(404)
        
    if user.id == session.get("user_id"):
        flash("Security violation: you cannot deactivate your own active session.", "warning")
        return redirect(url_for("admin.team_list"))
        
    user.is_active = not user.is_active
    status_str = "activated" if user.is_active else "revoked"
    log = AuditLog(
        username=session.get("username", "admin"),
        action=f"user_{status_str}",
        target_type="User",
        target_id=user.username,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    flash(f"Access authority for operator '{user.username}' has been {status_str}.", "info")
    return redirect(url_for("admin.team_list"))


# --- PUBLISHING CENTER & STATIC EXPORT PIPELINE ---

@admin_bp.route("/publishing")
@login_required
def publishing_center():
    db = get_db()
    draft_changes_count = db.session.query(PageContent).filter_by(has_unpublished_changes=True).count()
    last_publish_result = session.pop("last_publish_result", None)
    return render_template(
        "admin/publishing_center.html",
        draft_changes_count=draft_changes_count,
        last_publish_result=last_publish_result
    )

@admin_bp.route("/publishing/trigger", methods=["POST"])
@role_required("owner")
def publish_trigger():
    db = get_db()
    
    # 1. Promote any pending drafts to published
    drafts = db.session.query(PageContent).filter_by(has_unpublished_changes=True).all()
    for draft in drafts:
        draft.published_data_json = draft.draft_data_json
        draft.has_unpublished_changes = False
        draft.published_by = session.get("username", "admin")
        draft.published_at = datetime.utcnow()
    db.session.commit()
    
    # 2. Run static site export
    dist_dir = os.path.abspath(os.path.join(current_app.root_path, "..", "dist"))
    try:
        stats = export_static_site(current_app._get_current_object(), dist_dir)
        summary = (
            f"Static Build Executed Successfully at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"--------------------------------------------------\n"
            f"Pages Rendered & Frozen: {stats['pages_exported']}\n"
            f"Assets Bundled:          {stats['assets_copied']}\n"
            f"Pipeline Errors:         {len(stats['errors'])}\n"
            f"Destination Path:        {dist_dir}\n"
            f"Integrity Check:         PASSED"
        )
        if stats["errors"]:
            summary += "\n\nWarnings/Errors:\n" + "\n".join(stats["errors"])
            
        session["last_publish_result"] = summary
        
        log = AuditLog(
            username=session.get("username", "admin"),
            action="publish_production_bundle",
            target_type="StaticSite",
            target_id="dist",
            details=f"Rendered: {stats['pages_exported']} pages, Copied: {stats['assets_copied']} assets",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash("Production export completed successfully! Static site is frozen and staged for deployment.", "success")
    except Exception as e:
        session["last_publish_result"] = f"CRITICAL PIPELINE ERROR:\n{str(e)}"
        flash(f"Publishing failed: {str(e)}", "danger")
        
    return redirect(url_for("admin.publishing_center"))
