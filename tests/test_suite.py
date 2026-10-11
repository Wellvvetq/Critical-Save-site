import unittest
import json
from app import create_app
from config import TestConfig
from app.services.db import get_db
from app.models import User, Game, Article, Career, ContactInquiry

class CriticalSaveTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db = get_db()
        # Seed test administrator
        admin = User(username="testadmin", role="admin")
        admin.set_password("AdminSecret2026!")
        db.session.add(admin)
        
        # Seed test game
        game = Game(
            slug="test-aegis",
            title_en="Aegis Decay Test",
            short_description_en="Test description in english",
            title_ru="Aegis Decay Тест",
            short_description_ru="Тестовое описание на русском",
            is_published=True,
            is_featured=True
        )
        db.session.add(game)
        
        # Seed draft game
        draft_game = Game(
            slug="secret-prototype",
            title_en="Confidential Prototype",
            short_description_en="Not for public eyes",
            is_published=False
        )
        db.session.add(draft_game)

        # Seed article
        article = Article(
            slug="consequential-design-test",
            title_en="Agency In Systems",
            content_en="Article content",
            title_ru="Агентность в системах",
            content_ru="Содержимое статьи",
            is_published=True
        )
        db.session.add(article)

        db.session.commit()

    def tearDown(self):
        db = get_db()
        db.session.rollback()
        self.app_context.pop()

    def test_root_redirects_to_en(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers["Location"].endswith("/en"))

    def test_homepage_en_and_ru(self):
        res_en = self.client.get("/en")
        self.assertEqual(res_en.status_code, 200)
        self.assertIn(b"Critical Save Studio", res_en.data)
        self.assertIn(b"Aegis Decay Test", res_en.data)
        # Verify draft does not leak
        self.assertNotIn(b"Confidential Prototype", res_en.data)

        res_ru = self.client.get("/ru")
        self.assertEqual(res_ru.status_code, 200)
        self.assertIn(b"Aegis Decay \xd0\xa2\xd0\xb5\xd1\x81\xd1\x82", res_ru.data) # utf-8 encoded Russian

    def test_games_catalog_and_detail(self):
        res = self.client.get("/en/games")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Aegis Decay Test", res.data)
        self.assertNotIn(b"Confidential Prototype", res.data)

        res_detail = self.client.get("/en/games/test-aegis")
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn(b"Aegis Decay Test", res_detail.data)

        # 404 for unreleased/nonexistent
        res_404 = self.client.get("/en/games/secret-prototype")
        self.assertEqual(res_404.status_code, 404)

    def test_news_listing_and_detail(self):
        res = self.client.get("/en/news")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Agency In Systems", res.data)

        res_detail = self.client.get("/en/news/consequential-design-test")
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn(b"Agency In Systems", res_detail.data)

    def test_careers_page(self):
        res = self.client.get("/en/careers")
        self.assertEqual(res.status_code, 200)

    def test_contact_form_validation_and_submission(self):
        # Invalid payload (missing consent and invalid email)
        res_bad = self.client.post("/en/contact", data={
            "name": "A",
            "email": "invalid-email",
            "subject": "Press",
            "message": "Hi"
        })
        self.assertEqual(res_bad.status_code, 200)
        self.assertIn(b"Please provide your full name", res_bad.data)

        # Valid payload
        res_good = self.client.post("/en/contact", data={
            "name": "Alex Mercer",
            "email": "alex@studio-partner.com",
            "subject": "Publishing",
            "message": "We are interested in discussing co-publishing partnerships.",
            "consent": "on"
        })
        self.assertEqual(res_good.status_code, 200)
        self.assertIn(b"Message Received", res_good.data)

        # Verify DB queue
        db = get_db()
        inq = db.session.query(ContactInquiry).filter_by(email="alex@studio-partner.com").first()
        self.assertIsNotNone(inq)
        self.assertEqual(inq.name, "Alex Mercer")

    def test_admin_access_control(self):
        # Unauthenticated access to admin dashboard redirects to login
        res = self.client.get("/admin/")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers["Location"])

        # Authenticate
        login_res = self.client.post("/admin/login", data={
            "username": "testadmin",
            "password": "AdminSecret2026!"
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Operational Telemetry", login_res.data)

        # Create new project via admin
        create_res = self.client.post("/admin/games/new", data={
            "slug": "admin-created-project",
            "title_en": "Deep Space Void",
            "genre_en": "Atmospheric Space",
            "status_en": "Prototyping",
            "is_published": "on"
        }, follow_redirects=True)
        self.assertEqual(create_res.status_code, 200)

        # Confirm visible on public site
        pub_res = self.client.get("/en/games/admin-created-project")
        self.assertEqual(pub_res.status_code, 200)
        self.assertIn(b"Deep Space Void", pub_res.data)

    def test_sitemap_and_robots(self):
        sitemap_res = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap_res.status_code, 200)
        self.assertIn(b"<loc>", sitemap_res.data)
        self.assertIn(b"/en/games/test-aegis", sitemap_res.data)
        self.assertNotIn(b"/admin", sitemap_res.data)

        robots_res = self.client.get("/robots.txt")
        self.assertEqual(robots_res.status_code, 200)
        self.assertIn(b"Disallow: /admin/", robots_res.data)

if __name__ == "__main__":
    unittest.main()
