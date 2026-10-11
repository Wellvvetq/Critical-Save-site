"""
Iteration 5 Verification Test Suite
Confirms that:
1. All original concept artwork files exist in app/static/images/artwork/.
2. The redesigned cold-blue, midnight navy, and silver palette is active.
3. No legacy acid-lime styles (#B8F36B) exist in main.css.
4. All public routes (EN and RU) render successfully with HTTP 200 and reference the new artwork.
"""
import unittest
import os
from app import create_app
from config import TestConfig
from app.services.db import get_db
from app.models import User, Game, Article, Career

class Iteration5ArtAndPaletteVerification(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db = get_db()
        game = Game(
            slug="project-aegis-decay",
            title_en="Aegis Decay",
            short_description_en="Atmospheric survival.",
            is_published=True,
            is_featured=True
        )
        db.session.add(game)
        db.session.commit()

    def tearDown(self):
        db = get_db()
        db.session.rollback()
        self.app_context.pop()

    def test_original_artwork_package_exists(self):
        """Verify all master and responsive concept art derivatives exist and are non-empty."""
        art_dir = os.path.join(self.app.root_path, "static", "images", "artwork")
        required_assets = [
            "studio-hero-master.jpg",
            "studio-hero-desktop.jpg",
            "studio-hero-mobile.jpg",
            "aegis-keyart-master.jpg",
            "aegis-keyart-desktop.jpg",
            "aegis-keyart-thumb.jpg",
            "aegis-cover-master.jpg",
            "aegis-cover-card.jpg",
            "meridian-keyart-master.jpg",
            "meridian-keyart-desktop.jpg",
            "meridian-keyart-thumb.jpg",
            "meridian-cover-master.jpg",
            "meridian-cover-card.jpg",
            "studio-manifesto-master.jpg",
            "studio-manifesto-desktop.jpg"
        ]
        for asset in required_assets:
            path = os.path.join(art_dir, asset)
            self.assertTrue(os.path.exists(path), f"Missing required asset: {asset}")
            self.assertGreater(os.path.getsize(path), 10000, f"Asset file is too small or corrupt: {asset}")

    def test_stylesheet_palette_cold_blue_silver(self):
        """Verify main.css defines the midnight navy, cold blue, and silver design tokens."""
        css_path = os.path.join(self.app.root_path, "static", "css", "main.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check required cold blue & midnight navy tokens
        self.assertIn("#080D14", css_content)
        self.assertIn("#8FCBFA", css_content)
        self.assertIn("#C0E5FF", css_content)
        self.assertIn("#6F91B5", css_content)
        self.assertIn("#121E2B", css_content)

        # Check that legacy acid-lime is eliminated
        self.assertNotIn("#B8F36B", css_content)
        self.assertNotIn("#b8f36b", css_content)

    def test_homepage_artwork_integration(self):
        """Verify that the homepage renders the studio hero and responsive picture elements."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"studio-hero-desktop.jpg", res.data)
            self.assertIn(b"studio-hero-mobile.jpg", res.data)
            self.assertIn(b"WORLDS BEYOND THE FRAME", res.data)

    def test_games_catalog_artwork_integration(self):
        """Verify that the games catalog uses the concept art."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/games")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"aegis-keyart-desktop.jpg", res.data)

    def test_about_page_manifesto_artwork_integration(self):
        """Verify that the about page renders the panoramic observation gallery artwork."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/about")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"studio-manifesto-desktop.jpg", res.data)
            self.assertIn(b"WORLDS BEYOND THE FRAME", res.data)

if __name__ == "__main__":
    unittest.main()
