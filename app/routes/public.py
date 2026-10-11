import os
import re
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, g, make_response, send_file
)
from app.services.db import get_db
from app.services.i18n import t
from app.services.contact import handle_contact_submission
from app.models import Game, Article, Career, ContactInquiry

public_bp = Blueprint("public", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@public_bp.url_value_preprocessor
def pull_lang(endpoint, values):
    if values is not None and "lang" in values:
        g.lang = values.pop("lang")
    else:
        g.lang = "en"
    if g.lang not in ("en", "ru"):
        g.lang = "en"

@public_bp.url_defaults
def add_language_code(endpoint, values):
    if "lang" in values:
        return
    if hasattr(g, "lang"):
        values["lang"] = g.lang

# Root redirect to default locale (/en)
@public_bp.route("/")
def root():
    return redirect("/en")

# Direct alias for Financial War Room product showcase
@public_bp.route("/products/financial-war-room")
def fwr_direct():
    lang = getattr(g, "lang", "en")
    if lang not in ("en", "ru"):
        lang = "en"
    return redirect(f"/{lang}/products/financial-war-room")

@public_bp.route("/<lang>/products/financial-war-room")
def product_fwr():
    lang = g.lang
    fwr_metadata = {
        "version": "5.0.0",
        "release_date": "2026-10-11",
        "standard": {
            "edition": "Standard Edition",
            "filename": "Avenor-Setup-5.0.0.exe",
            "size_bytes": 166781273,
            "size_mb": "159.0 MB",
            "sha256": "A3CCC0F9D252EB132B5034141540337F6B76CCF085CC0657EEC889005295FC66",
            "download_url": url_for("public.download_fwr", edition="standard"),
            "requirements": "Windows 10 / 11 (64-bit), 4 GB RAM. Internet required on first run to download lightweight AI model."
        },
        "offline": {
            "edition": "Offline Edition",
            "filename": "Avenor-Offline-Setup-5.0.0.exe",
            "size_bytes": 644524466,
            "size_mb": "614.7 MB",
            "sha256": "FC8C6D14588DEC409ECE65A5927867A7698B67332D3470DAAFBCB9DDA113185A",
            "download_url": url_for("public.download_fwr", edition="offline"),
            "requirements": "Windows 10 / 11 (64-bit), 8 GB RAM. Fully standalone air-gapped bundle; pre-bundled local financial model."
        }
    }
    return render_template(
        "public/product_fwr.html",
        lang=lang,
        t=lambda k: t(k, lang),
        meta=fwr_metadata,
        page_title="Avenor — Personal Finance Intelligence | Critical Save Studio" if lang == "en" else "Avenor — Персональный финансовый интеллект | Critical Save Studio",
        meta_description="Avenor — Your finances, in perspective." if lang == "en" else "Avenor — персональный финансовый интеллект, прогноз ликвидности и локальный ИИ."
    )

@public_bp.route("/download/fwr/<edition>")
def download_fwr(edition):
    edition_map = {
        "standard": {
            "filename": "Avenor-Setup-5.0.0.exe",
            "local_path": r"C:\Users\PLATINUM\.gemini\antigravity\scratch\financial-war-room\apps\web\dist-release\Avenor-Setup-5.0.0.exe"
        },
        "offline": {
            "filename": "Avenor-Offline-Setup-5.0.0.exe",
            "local_path": r"C:\Users\PLATINUM\.gemini\antigravity\scratch\financial-war-room\apps\web\dist-release\Avenor-Offline-Setup-5.0.0.exe"
        }
    }
    if edition not in edition_map:
        abort(404)

    file_info = edition_map[edition]
    cdn_base = os.environ.get("FWR_RELEASE_BASE_URL")
    if cdn_base:
        return redirect(f"{cdn_base.rstrip('/')}/{file_info['filename']}")

    if os.path.exists(file_info["local_path"]):
        return send_file(
            file_info["local_path"],
            as_attachment=True,
            download_name=file_info["filename"],
            mimetype="application/vnd.microsoft.portable-executable"
        )
    return make_response(
        "Release installer is currently in local staging or awaiting publication.",
        404
    )

@public_bp.route("/<lang>")
def index():
    lang = g.lang
    db = get_db()
    featured_games = (
        db.session.query(Game)
        .filter_by(is_published=True, is_featured=True)
        .order_by(Game.sort_order.asc(), Game.created_at.desc())
        .limit(3)
        .all()
    )
    if not featured_games:
        # Fallback to any published games if none flagged as featured
        featured_games = (
            db.session.query(Game)
            .filter_by(is_published=True)
            .order_by(Game.sort_order.asc(), Game.created_at.desc())
            .limit(3)
            .all()
        )
    latest_articles = (
        db.session.query(Article)
        .filter_by(is_published=True)
        .order_by(Article.created_at.desc())
        .limit(3)
        .all()
    )
    return render_template(
        "public/index.html",
        lang=lang,
        t=lambda k: t(k, lang),
        featured_games=featured_games,
        latest_articles=latest_articles,
        page_title="Critical Save Studio — Cinematic Interactive Worlds" if lang == "en" else "Critical Save Studio — Кинематографичные интерактивные миры",
        meta_description=t("hero_subheadline", lang)
    )

@public_bp.route("/<lang>/games")
def games_catalog():
    lang = g.lang
    genre_filter = request.args.get("genre")
    db = get_db()
    
    query = db.session.query(Game).filter_by(is_published=True)
    if genre_filter:
        if lang == "ru":
            query = query.filter(Game.genre_ru.ilike(f"%{genre_filter}%"))
        else:
            query = query.filter(Game.genre_en.ilike(f"%{genre_filter}%"))
            
    games = query.order_by(Game.sort_order.asc(), Game.created_at.desc()).all()
    
    # Collect available genres for filter bar
    all_genres = set()
    for g_item in db.session.query(Game).filter_by(is_published=True).all():
        val = g_item.get_genre(lang)
        if val:
            all_genres.add(val)
            
    return render_template(
        "public/games.html",
        lang=lang,
        t=lambda k: t(k, lang),
        games=games,
        genres=sorted(list(all_genres)),
        active_genre=genre_filter,
        page_title=f"{t('catalog_title', lang)} — Critical Save Studio",
        meta_description=t("catalog_subtitle", lang)
    )

# Direct alias for Software catalog
@public_bp.route("/software")
def software_direct():
    lang = getattr(g, "lang", "en")
    if lang not in ("en", "ru"):
        lang = "en"
    return redirect(f"/{lang}/software")

@public_bp.route("/<lang>/software")
def software_catalog():
    lang = g.lang
    fwr_metadata = {
        "version": "4.1.0",
        "release_date": "2026-10-11",
        "standard": {
            "edition": "Standard Edition",
            "filename": "Financial-War-Room-Setup-4.1.0.exe",
            "size_bytes": 162232092,
            "size_mb": "154.7 MB",
            "sha256": "ffc7e7bc2e7338ea1cf1c5a8181ce31a6e8e2d0acdd1fac0cc2f3bde2ac6e206",
            "download_url": url_for("public.download_fwr", edition="standard"),
            "requirements": "Windows 10 / 11 (64-bit), 4 GB RAM"
        },
        "offline": {
            "edition": "Offline Edition",
            "filename": "Financial-War-Room-Offline-Setup-4.1.0.exe",
            "size_bytes": 639975053,
            "size_mb": "610.3 MB",
            "sha256": "e4052b04e1f65d119e9b7a4d36e7a21beed784aff338e527990535f013f9573c",
            "download_url": url_for("public.download_fwr", edition="offline"),
            "requirements": "Windows 10 / 11 (64-bit), 8 GB RAM"
        }
    }
    return render_template(
        "public/software.html",
        lang=lang,
        t=lambda k: t(k, lang),
        meta=fwr_metadata,
        page_title="Software & Digital Tools — Critical Save Studio" if lang == "en" else "Программное обеспечение и инструменты — Critical Save Studio",
        meta_description=t("division_software_desc", lang)
    )

@public_bp.route("/<lang>/games/<slug>")
def game_detail(slug):
    lang = g.lang
    db = get_db()
    game = db.session.query(Game).filter_by(slug=slug, is_published=True).first()
    if not game:
        abort(404)
        
    other_games = (
        db.session.query(Game)
        .filter(Game.is_published == True, Game.id != game.id)
        .order_by(Game.sort_order.asc())
        .limit(2)
        .all()
    )
    
    return render_template(
        "public/game_detail.html",
        lang=lang,
        t=lambda k: t(k, lang),
        game=game,
        other_games=other_games,
        page_title=f"{game.get_title(lang)} — Critical Save Studio",
        meta_description=game.get_short_description(lang) or game.get_tagline(lang) or ""
    )

@public_bp.route("/<lang>/about")
def about():
    lang = g.lang
    return render_template(
        "public/about.html",
        lang=lang,
        t=lambda k: t(k, lang),
        page_title=f"{t('nav_about', lang)} — Critical Save Studio",
        meta_description=t("about_subtitle", lang)
    )

@public_bp.route("/<lang>/news")
def news():
    lang = g.lang
    db = get_db()
    articles = (
        db.session.query(Article)
        .filter_by(is_published=True)
        .order_by(Article.created_at.desc())
        .all()
    )
    return render_template(
        "public/news.html",
        lang=lang,
        t=lambda k: t(k, lang),
        articles=articles,
        page_title=f"{t('news_title', lang)} — Critical Save Studio",
        meta_description=t("news_subtitle", lang)
    )

@public_bp.route("/<lang>/news/<slug>")
def article_detail(slug):
    lang = g.lang
    db = get_db()
    article = db.session.query(Article).filter_by(slug=slug, is_published=True).first()
    if not article:
        abort(404)
        
    recent_articles = (
        db.session.query(Article)
        .filter(Article.is_published == True, Article.id != article.id)
        .order_by(Article.created_at.desc())
        .limit(2)
        .all()
    )
    
    return render_template(
        "public/article_detail.html",
        lang=lang,
        t=lambda k: t(k, lang),
        article=article,
        recent_articles=recent_articles,
        page_title=f"{article.get_title(lang)} — Critical Save Studio",
        meta_description=article.get_excerpt(lang) or ""
    )

@public_bp.route("/<lang>/careers")
def careers():
    lang = g.lang
    db = get_db()
    careers_list = (
        db.session.query(Career)
        .filter_by(is_published=True)
        .order_by(Career.created_at.desc())
        .all()
    )
    return render_template(
        "public/careers.html",
        lang=lang,
        t=lambda k: t(k, lang),
        careers=careers_list,
        page_title=f"{t('careers_title', lang)} — Critical Save Studio",
        meta_description=t("careers_subtitle", lang)
    )

@public_bp.route("/<lang>/contact", methods=["GET", "POST"])
def contact():
    lang = g.lang
    error = None
    success = False
    delivery_note = None
    
    if request.method == "POST":
        from app.services.csrf import validate_csrf_token
        from app.services.limiter import is_rate_limited
        
        # 1. CSRF Verification
        validate_csrf_token()

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

        # 2. Rate Limiting Check (max 5 requests per 60 seconds)
        if is_rate_limited(ip, max_requests=5, window_seconds=60):
            error = (
                "Rate limit exceeded. Please wait a moment before transmitting another dispatch."
                if lang == "en" else
                "Превышен лимит отправки сообщений. Пожалуйста, подождите минуту перед повторной попыткой."
            )
        else:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()
            consent = request.form.get("consent")
            
            # Rigorous Server-side Validation
            if not name or len(name) < 2:
                error = "Please provide your full name (at least 2 characters)." if lang == "en" else "Пожалуйста, укажите ваше имя (не менее 2 символов)."
            elif not email or not EMAIL_REGEX.match(email):
                error = "Please provide a valid email address." if lang == "en" else "Пожалуйста, укажите корректный адрес электронной почты."
            elif not subject:
                error = "Please select or enter the nature of your inquiry." if lang == "en" else "Пожалуйста, укажите тему сообщения."
            elif not message or len(message) < 10:
                error = "Message content must be at least 10 characters." if lang == "en" else "Текст сообщения должен содержать не менее 10 символов."
            elif not consent:
                error = "You must agree to privacy processing to proceed." if lang == "en" else "Необходимо дать согласие на обработку данных."
            else:
                ok, delivered, note = handle_contact_submission(name, email, subject, message, ip)
                if ok:
                    success = True
                    delivery_note = note
                else:
                    error = note or ("An error occurred during submission." if lang == "en" else "Произошла ошибка при отправке.")
                
    return render_template(
        "public/contact.html",
        lang=lang,
        t=lambda k: t(k, lang),
        error=error,
        success=success,
        delivery_note=delivery_note,
        page_title=f"{t('contact_title', lang)} — Critical Save Studio",
        meta_description=t("contact_subtitle", lang)
    )

# SEO & Discovery Routes
@public_bp.route("/sitemap.xml")
def sitemap():
    db = get_db()
    games = db.session.query(Game).filter_by(is_published=True).all()
    articles = db.session.query(Article).filter_by(is_published=True).all()
    
    pages = [
        {"loc": "/en", "lastmod": "2026-10-09"},
        {"loc": "/ru", "lastmod": "2026-10-09"},
        {"loc": "/en/games", "lastmod": "2026-10-09"},
        {"loc": "/ru/games", "lastmod": "2026-10-09"},
        {"loc": "/en/about", "lastmod": "2026-10-09"},
        {"loc": "/ru/about", "lastmod": "2026-10-09"},
        {"loc": "/en/news", "lastmod": "2026-10-09"},
        {"loc": "/ru/news", "lastmod": "2026-10-09"},
        {"loc": "/en/careers", "lastmod": "2026-10-09"},
        {"loc": "/ru/careers", "lastmod": "2026-10-09"},
        {"loc": "/en/contact", "lastmod": "2026-10-09"},
        {"loc": "/ru/contact", "lastmod": "2026-10-09"},
        {"loc": "/en/products/financial-war-room", "lastmod": "2026-10-11"},
        {"loc": "/ru/products/financial-war-room", "lastmod": "2026-10-11"},
    ]
    
    for g_item in games:
        pages.append({"loc": f"/en/games/{g_item.slug}", "lastmod": g_item.updated_at.strftime("%Y-%m-%d")})
        pages.append({"loc": f"/ru/games/{g_item.slug}", "lastmod": g_item.updated_at.strftime("%Y-%m-%d")})
        
    for a in articles:
        pages.append({"loc": f"/en/news/{a.slug}", "lastmod": a.updated_at.strftime("%Y-%m-%d")})
        pages.append({"loc": f"/ru/news/{a.slug}", "lastmod": a.updated_at.strftime("%Y-%m-%d")})
        
    xml_content = render_template("public/sitemap.xml", pages=pages, host=request.host_url.rstrip("/"))
    response = make_response(xml_content)
    response.headers["Content-Type"] = "application/xml"
    return response

@public_bp.route("/robots.txt")
def robots():
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /static/uploads/

Sitemap: {request.host_url.rstrip('/')}/sitemap.xml
"""
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain"
    return response
