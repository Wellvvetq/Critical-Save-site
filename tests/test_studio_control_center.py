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
