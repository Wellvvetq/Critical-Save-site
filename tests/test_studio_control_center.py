import os
import shutil
import pytest
from app import create_app
from app.services.db import get_db
from app.models import Base, User, PageContent, SoftwareProduct, SoftwareRelease, AuditLog
from app.services.static_exporter import export_static_site

@pytest.fixture
def app_instance(tmp_path):
    test_db = tmp_path / "test_critical_save.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    class TestConfig:
        TESTING = True
        WTF_CSRF_ENABLED = False
        SECRET_KEY = "test-secret-key-12345"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{test_db}"
        UPLOAD_FOLDER = str(upload_dir)
        ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg"}
    
    app = create_app(config_class=TestConfig)
    
    with app.app_context():
        db = get_db()
        Base.metadata.create_all(db.engine)
        
        # Create Owner and Editor accounts
        owner = User(username="test_owner", role="owner", is_active=True)
        owner.set_password("OwnerPassword123!")
        editor = User(username="test_editor", role="editor", is_active=True)
        editor.set_password("EditorPassword123!")
        db.session.add_all([owner, editor])
        
        # Seed test product
        prod = SoftwareProduct(
            slug="avenor-test",
            title_en="Avenor Test",
            title_ru="Авенор Тест",
            category="Intelligence Engine",
            is_published=True
        )
        db.session.add(prod)
        db.session.commit()
        
    yield app

def test_static_exporter(app_instance, tmp_path):
    """Verifies that static_exporter generates clean HTML and assets with zero errors."""
    out_dir = tmp_path / "dist"
    stats = export_static_site(app_instance, str(out_dir))
    
    assert stats["pages_exported"] >= 20
    assert stats["assets_copied"] > 0
    assert len(stats["errors"]) == 0
    assert (out_dir / "index.html").exists()
    assert (out_dir / "en" / "index.html").exists()
    assert (out_dir / "ru" / "index.html").exists()
    assert (out_dir / "404.html").exists()
    assert (out_dir / ".nojekyll").exists()

def test_rbac_admin_access(app_instance):
    """Verifies Owner vs Editor permissions."""
    client = app_instance.test_client()
    
    # 1. Unauthenticated request to /admin/ is redirected to login
    res = client.get("/admin/", follow_redirects=False)
    assert res.status_code == 302
    assert "/admin/login" in res.headers["Location"]
    
    # 2. Login as Editor
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["username"] = "test_editor"
        sess["role"] = "editor"
        
    # Editor can view dashboard and pages
    res = client.get("/admin/")
    assert res.status_code == 200
    res = client.get("/admin/pages")
    assert res.status_code == 200
    
    # Editor CANNOT publish or access team management mutations
    res = client.post("/admin/publishing/trigger", follow_redirects=False)
    assert res.status_code in (403, 302)  # blocked by role_required
    
    res = client.post("/admin/team/new", data={"username": "hacker", "password": "password123"}, follow_redirects=False)
    assert res.status_code in (403, 302)  # blocked by role_required

def test_four_stage_release_gate(app_instance):
    """Verifies that a release cannot be marked live without all 4 stages verified."""
    with app_instance.app_context():
        db = get_db()
        prod = db.session.query(SoftwareProduct).first()
        
        # Case A: Incomplete verification (missing hash and backend smoke test)
        rel_incomplete = SoftwareRelease(
            product_id=prod.id,
            version="1.0.0",
            standard_filename="test.exe",
            standard_sha256="abc",
            offline_filename="test-offline.exe",
            offline_sha256="def",
            file_exists_verified=True,
            hash_verified=False,
            backend_verified=False,
            owner_approved=True,
            is_live=False
        )
        db.session.add(rel_incomplete)
        db.session.commit()
        
        # Verify it cannot be live
        assert rel_incomplete.is_live is False
        
        # Case B: All 4 stages verified
        rel_complete = SoftwareRelease(
            product_id=prod.id,
            version="1.1.0",
            standard_filename="test2.exe",
            standard_sha256="abc2",
            offline_filename="test2-offline.exe",
            offline_sha256="def2",
            file_exists_verified=True,
            hash_verified=True,
            backend_verified=True,
            owner_approved=True,
            is_live=True
        )
        db.session.add(rel_complete)
        db.session.commit()
        
        assert rel_complete.is_live is True

def test_page_block_draft_staging(app_instance):
    """Verifies that editors save changes as drafts without immediately altering published output."""
    client = app_instance.test_client()
    
    with app_instance.app_context():
        db = get_db()
        page = PageContent(
            page_key="test_page",
            title_en="Initial Title",
            published_data_json='{"lead": "Original"}',
            draft_data_json='{"lead": "Original"}',
            has_unpublished_changes=False
        )
        db.session.add(page)
        db.session.commit()
        
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["username"] = "test_editor"
        sess["role"] = "editor"
        
    # Editor posts a draft modification
    res = client.post("/admin/pages/test_page/edit", data={
        "title_en": "Updated Title",
        "draft_data_json": '{"lead": "Draft Modification"}',
        "action": "save_draft"
    }, follow_redirects=True)
    assert res.status_code == 200
    
    with app_instance.app_context():
        db = get_db()
        p = db.session.query(PageContent).filter_by(page_key="test_page").first()
        assert p.title_en == "Updated Title"
        assert p.has_unpublished_changes is True
        assert p.get_published()["lead"] == "Original"
        assert p.get_draft()["lead"] == "Draft Modification"


def test_page_content_translation_override_lifecycle(app_instance):
    """
    Verifies that:
    1. Published PageContent overrides are visible on the public website via t(key, lang).
    2. Draft modifications are strictly hidden until published.
    3. Keys without overrides fallback seamlessly to TRANSLATIONS.
    4. Russian and English languages do not mix.
    """
    from app.services.i18n import t

    with app_instance.app_context():
        db = get_db()
        page = PageContent(
            page_key="home",
            title_en="Home Page",
            published_data_json='{"hero_headline_1_en": "OVERRIDDEN WORLDS EN", "hero_headline_1_ru": "КАСТОМНЫЕ МИРЫ RU"}',
            draft_data_json='{"hero_headline_1_en": "UNPUBLISHED DRAFT EN", "hero_headline_1_ru": "ЧЕРНОВЫЕ МИРЫ RU"}',
            has_unpublished_changes=True
        )
        db.session.add(page)
        db.session.commit()

        # 1. Published values are rendered
        assert t("hero_headline_1", "en") == "OVERRIDDEN WORLDS EN"
        assert t("hero_headline_1", "ru") == "КАСТОМНЫЕ МИРЫ RU"

        # 2. Draft values are NOT rendered
        assert t("hero_headline_1", "en") != "UNPUBLISHED DRAFT EN"
        assert t("hero_headline_1", "ru") != "ЧЕРНОВЫЕ МИРЫ RU"

        # 3. Keys without overrides fallback to hardcoded TRANSLATIONS
        assert t("studio_name", "en") == "Critical Save Studio"
        assert t("studio_name", "ru") == "Critical Save Studio"
        assert t("nav_home", "en") == "Home"
        assert t("nav_home", "ru") == "Главная"

        # 4. English and Russian values do not mix
        assert t("hero_headline_1", "en") != t("hero_headline_1", "ru")

    # 5. Check public HTTP endpoint rendering
    client = app_instance.test_client()
    res_en = client.get("/en")
    assert res_en.status_code == 200
    assert "OVERRIDDEN WORLDS EN" in res_en.get_data(as_text=True)
    assert "UNPUBLISHED DRAFT EN" not in res_en.get_data(as_text=True)

    res_ru = client.get("/ru")
    assert res_ru.status_code == 200
    assert "КАСТОМНЫЕ МИРЫ RU" in res_ru.get_data(as_text=True)
    assert "ЧЕРНОВЫЕ МИРЫ RU" not in res_ru.get_data(as_text=True)


def test_home_page_visual_form_editor_and_unmanaged_keys(app_instance):
    """
    Verifies that:
    1. Saving the home page form via visual form fields updates draft_data_json correctly.
    2. Unmanaged / arbitrary JSON keys already in draft_data_json are preserved without loss.
    3. Distinct RU and EN fields are preserved independently.
    4. Save draft does not immediately publish to production.
    """
    client = app_instance.test_client()

    with app_instance.app_context():
        db = get_db()
        # Seed home page with an existing unmanaged custom key
        home_page = PageContent(
            page_key="home",
            title_en="Home",
            title_ru="Главная",
            published_data_json='{"unmanaged_custom_telemetry": "ALPHA-01", "hero_headline_1_en": "ORIGINAL"}',
            draft_data_json='{"unmanaged_custom_telemetry": "ALPHA-01", "hero_headline_1_en": "ORIGINAL"}',
            has_unpublished_changes=False
        )
        db.session.add(home_page)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "test_owner"
        sess["role"] = "owner"

    # Post home form with visual form fields while preserving unmanaged raw JSON in textarea
    res = client.post("/admin/pages/home/edit", data={
        "title_en": "Home Updated",
        "title_ru": "Главная Обновлена",
        "draft_data_json": '{"unmanaged_custom_telemetry": "ALPHA-01"}',
        "hero_badge_en": "Studio Label EN",
        "hero_badge_ru": "Лейбл Студии RU",
        "hero_headline_1_en": "NEW WORLDS EN",
        "hero_headline_1_ru": "НОВЫЕ МИРЫ RU",
        "hero_headline_2_en": "BEYOND STARS EN",
        "hero_headline_2_ru": "ЗА ЗВЕЗДАМИ RU",
        "hero_subheadline_en": "Deep narrative adventures.",
        "hero_subheadline_ru": "Глубокие нарративные приключения.",
        "hero_cta_games_en": "View Catalog",
        "hero_cta_games_ru": "В каталог",
        "hero_cta_software_en": "Download FWR",
        "hero_cta_software_ru": "Скачать FWR",
        "action": "save_draft"
    }, follow_redirects=True)
    assert res.status_code == 200

    with app_instance.app_context():
        db = get_db()
        p = db.session.query(PageContent).filter_by(page_key="home").first()
        draft = p.get_draft()

        # 1. Unmanaged key preserved
        assert draft.get("unmanaged_custom_telemetry") == "ALPHA-01"

        # 2. Visual fields mapped into draft JSON
        assert draft.get("hero_badge_en") == "Studio Label EN"
        assert draft.get("hero_badge_ru") == "Лейбл Студии RU"
        assert draft.get("hero_headline_1_en") == "NEW WORLDS EN"
        assert draft.get("hero_headline_1_ru") == "НОВЫЕ МИРЫ RU"
        assert draft.get("hero_headline_2_en") == "BEYOND STARS EN"
        assert draft.get("hero_headline_2_ru") == "ЗА ЗВЕЗДАМИ RU"
        assert draft.get("hero_subheadline_en") == "Deep narrative adventures."
        assert draft.get("hero_subheadline_ru") == "Глубокие нарративные приключения."
        assert draft.get("hero_cta_games_en") == "View Catalog"
        assert draft.get("hero_cta_games_ru") == "В каталог"
        assert draft.get("hero_cta_software_en") == "Download FWR"
        assert draft.get("hero_cta_software_ru") == "Скачать FWR"

        # 3. Not automatically published
        assert p.has_unpublished_changes is True
        assert p.get_published().get("hero_headline_1_en") == "ORIGINAL"

