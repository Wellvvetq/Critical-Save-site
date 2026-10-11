import os
import shutil
import re
from pathlib import Path
from flask import current_app
from app.services.db import get_db
from app.models import Game, Article, Career, SoftwareProduct, SoftwareRelease

def export_static_site(app, output_dir, base_path=""):
    """
    Exports the entire Critical Save Studio website to static HTML and assets
    for deployment to GitHub Pages or static CDN.
    
    :param app: Flask application instance
    :param output_dir: Directory where static site files will be written
    :param base_path: Optional repository base path (e.g. '/Critical-Save-site' or '')
    :return: dict with export statistics
    """
    if not base_path:
        base_path = os.environ.get("BASE_PATH", "")
        if not base_path and os.environ.get("GITHUB_REPOSITORY"):
            repo_part = os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1]
            if not repo_part.lower().endswith(".github.io"):
                base_path = repo_part

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    client = app.test_client()
    stats = {
        "pages_exported": 0,
        "assets_copied": 0,
        "errors": []
    }
    
    # 1. Collect all static routes to render
    routes_to_export = [
        # Root index redirect page
        ("/", "index.html"),
        ("/404.html", "404.html"),
        
        # Localized Core Pages
        ("/en", "en/index.html"),
        ("/ru", "ru/index.html"),
        ("/en/games", "en/games/index.html"),
        ("/ru/games", "ru/games/index.html"),
        ("/en/software", "en/software/index.html"),
        ("/ru/software", "ru/software/index.html"),
        ("/en/products/financial-war-room", "en/products/financial-war-room/index.html"),
        ("/ru/products/financial-war-room", "ru/products/financial-war-room/index.html"),
        ("/en/about", "en/about/index.html"),
        ("/ru/about", "ru/about/index.html"),
        ("/en/news", "en/news/index.html"),
        ("/ru/news", "ru/news/index.html"),
        ("/en/careers", "en/careers/index.html"),
        ("/ru/careers", "ru/careers/index.html"),
        ("/en/contact", "en/contact/index.html"),
        ("/ru/contact", "ru/contact/index.html"),
        
        # System & SEO feeds
        ("/sitemap.xml", "sitemap.xml"),
        ("/robots.txt", "robots.txt"),
    ]
    
    with app.app_context():
        db = get_db()
        
        # Dynamic Game Detail Pages
        games = db.session.query(Game).filter_by(is_published=True).all()
        for g in games:
            routes_to_export.append((f"/en/games/{g.slug}", f"en/games/{g.slug}/index.html"))
            routes_to_export.append((f"/ru/games/{g.slug}", f"ru/games/{g.slug}/index.html"))
            
        # Dynamic Article Detail Pages
        articles = db.session.query(Article).filter_by(is_published=True).all()
        for a in articles:
            routes_to_export.append((f"/en/news/{a.slug}", f"en/news/{a.slug}/index.html"))
            routes_to_export.append((f"/ru/news/{a.slug}", f"ru/news/{a.slug}/index.html"))

    # 2. Render each route and save to output directory
    for route, target_rel_path in routes_to_export:
        try:
            resp = client.get(route, follow_redirects=(route == "/"))
            if resp.status_code != 200:
                stats["errors"].append(f"Route {route} returned status {resp.status_code}")
                continue
                
            content = resp.data.decode("utf-8")
            
            # If base_path is provided (for GitHub Pages subpaths like /repo-name), adjust root-relative URLs
            if base_path:
                clean_base = "/" + base_path.strip("/")
                # Replace root-relative static and page links safely
                content = re.sub(r'href="/(en|ru|static|sitemap\.xml|robots\.txt)', rf'href="{clean_base}/\1', content)
                content = re.sub(r'src="/(static)', rf'src="{clean_base}/\1', content)
                content = re.sub(r'content="http://localhost/static', rf'content="{clean_base}/static', content)
                content = re.sub(r'content="/(static)', rf'content="{clean_base}/\1', content)
                content = re.sub(r'url\((["\']?)/(static)', rf'url(\1{clean_base}/\2', content)
                
            target_file = out_path / target_rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content, encoding="utf-8")
            stats["pages_exported"] += 1
        except Exception as e:
            stats["errors"].append(f"Error exporting {route}: {str(e)}")

    # 3. Copy static asset folder directly
    static_src = Path(app.root_path) / "static"
    static_dst = out_path / "static"
    if static_dst.exists():
        shutil.rmtree(static_dst)
    shutil.copytree(static_src, static_dst)
    
    # Count copied assets
    for _ in static_dst.rglob("*"):
        stats["assets_copied"] += 1

    # 4. Create .nojekyll file for GitHub Pages (ensures folders with underscores or raw assets are preserved)
    (out_path / ".nojekyll").write_text("", encoding="utf-8")
    
    return stats
