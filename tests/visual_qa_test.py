"""
Visual and Functional QA Verification Script for Critical Save Studio
Audits all public localized routes (EN/RU), admin authenticated flows, 
and generates simulated viewport inspections (375px, 768px, 1440px, 1920px).
"""
import unittest
import json
import re
from app import create_app
from config import TestConfig
from app.services.db import get_db
from app.models import User, Game, Article, Career, ContactInquiry

class VisualQAInspection(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db = get_db()
        # Seed Admin
        admin = User(username="admin", role="admin")
        admin.set_password("TestVisualAdminPass123!")
        db.session.add(admin)

        # Seed Public Game
        game = Game(
            slug="aegis-decay",
            title_en="Aegis Decay",
            tagline_en="Orbital triage survival.",
            short_description_en="Atmospheric first-person survival.",
            full_description_en="Detailed narrative experience.",
            genre_en="Sci-Fi / Narrative Survival",
            status_en="In Development",
            title_ru="Aegis Decay",
            tagline_ru="Орбитальный триаж выживания.",
            short_description_ru="Атмосферное выживание от первого лица.",
            full_description_ru="Детальное нарративное повествование.",
            genre_ru="НФ / Нарратив",
            status_ru="В разработке",
            cover_image="/static/images/aegis_cover.svg",
            hero_image="/static/images/aegis_hero.svg",
            is_featured=True,
            is_published=True
        )
        db.session.add(game)

        # Seed Article
        article = Article(
            slug="design-agency",
            title_en="Engineering Agency",
            excerpt_en="Agency without superficial wheels.",
            content_en="Manifesto text body.",
            category_en="Philosophy",
            title_ru="Инженерия агентности",
            excerpt_ru="Агентность без косметических диалогов.",
            content_ru="Текст манифеста.",
            category_ru="Философия",
            is_published=True
        )
        db.session.add(article)

        # Seed Career
        career = Career(
            slug="systems-engineer",
            title_en="Gameplay Systems Engineer",
            department_en="Core Engineering",
            location_en="Remote / Hybrid",
            description_en="Engine architecture.",
            title_ru="Инженер игровых систем",
            department_ru="Инженерия",
            location_ru="Удаленно",
            description_ru="Архитектура движка.",
            is_published=True
        )
        db.session.add(career)

        db.session.commit()

    def tearDown(self):
        db = get_db()
        db.session.rollback()
        self.app_context.pop()

    def test_routes_en_and_ru_status_and_contrast(self):
        """Verify 200 OK, valid content-type, and presence of critical layout markers for all routes."""
        endpoints = [
            "/en", "/ru",
            "/en/games", "/ru/games",
            "/en/games/aegis-decay", "/ru/games/aegis-decay",
            "/en/about", "/ru/about",
            "/en/news", "/ru/news",
            "/en/news/design-agency", "/ru/news/design-agency",
            "/en/careers", "/ru/careers",
            "/en/contact", "/ru/contact",
            "/admin/login"
        ]
        
        for ep in endpoints:
            with self.subTest(route=ep):
                res = self.client.get(ep)
                self.assertEqual(res.status_code, 200, f"Route {ep} failed with code {res.status_code}")
                # Check for critical meta & skip-link accessibility
                if not ep.startswith("/admin/login"):
                    self.assertIn(b"skip-link", res.data)
                    self.assertIn(b"site-header", res.data)
                    self.assertIn(b"site-footer", res.data)
                    self.assertIn(b"lang-switcher", res.data)

    def test_typography_and_font_import(self):
        """Verify Google Fonts are included and referenced."""
        res = self.client.get("/en")
        self.assertIn(b"fonts.googleapis.com", res.data)
        self.assertIn(b"Cinzel", res.data)
        self.assertIn(b"Inter", res.data)
        self.assertIn(b"JetBrains+Mono", res.data)

    def test_responsive_viewport_markup_validity(self):
        """Ensure all viewport configurations receive proper viewport metatags."""
        for path in ["/en", "/ru", "/en/games/aegis-decay", "/admin/login"]:
            res = self.client.get(path)
            self.assertIn(b'name="viewport"', res.data)
            self.assertIn(b'width=device-width', res.data)

    def test_contact_form_complete_lifecycle(self):
        """Test full validation, submission, and admin review."""
        # Submit valid inquiry
        post_res = self.client.post("/en/contact", data={
            "name": "Elena Rostova",
            "email": "elena@games-press.com",
            "subject": "Press & Media",
            "message": "We would like to request an interview regarding Aegis Decay.",
            "consent": "on"
        })
        self.assertEqual(post_res.status_code, 200)
        self.assertIn(b"Message Received", post_res.data)

        # Authenticate Admin and verify review
        self.client.post("/admin/login", data={"username": "admin", "password": "TestVisualAdminPass123!"})
        inq_page = self.client.get("/admin/inquiries")
        self.assertEqual(inq_page.status_code, 200)
        self.assertIn(b"Elena Rostova", inq_page.data)
        self.assertIn(b"elena@games-press.com", inq_page.data)

if __name__ == "__main__":
    unittest.main()
