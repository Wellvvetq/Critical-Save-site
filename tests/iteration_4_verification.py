"""
Iteration 4 Verification Test Suite
Confirms that the structural redesign is present on all public pages (EN and RU),
and that all telemetry ribbons, asymmetric layouts, and editorial headers are active.
"""
import unittest
from app import create_app
from config import TestConfig
from app.services.db import get_db
from app.models import User, Game, Article, Career, ContactInquiry

class Iteration4DesignVerification(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db = get_db()
        admin = User(username="admin", role="admin")
        admin.set_password("AdminPass2026!Secure")
        db.session.add(admin)

        # Seed two games to verify asymmetric flagship and secondary stream
        game1 = Game(
            slug="aegis-decay",
            title_en="Aegis Decay",
            tagline_en="Orbital triage survival.",
            short_description_en="Atmospheric first-person survival.",
            full_description_en="Full narrative dossier text.",
            genre_en="Sci-Fi / Narrative Survival",
            status_en="In Development",
            title_ru="Aegis Decay",
            tagline_ru="Орбитальный триаж выживания.",
            short_description_ru="Атмосферное выживание от первого лица.",
            full_description_ru="Полное описание проекта.",
            genre_ru="НФ / Нарратив",
            status_ru="В разработке",
            features_json_en='["Tactical Resource Triage", "Atmospheric Physics Simulation", "Non-Linear Consequence Tree"]',
            features_json_ru='["Тактический триаж ресурсов", "Физика атмосферы", "Нелинейное древо последствий"]',
            cover_image="/static/images/aegis_cover.svg",
            hero_image="/static/images/aegis_hero.svg",
            is_featured=True,
            is_published=True
        )
        game2 = Game(
            slug="meridian-zero",
            title_en="Meridian Zero",
            tagline_en="Sub-surface acoustics.",
            short_description_en="Experimental tactical telemetry.",
            genre_en="Tactical Simulation",
            status_en="Pre-Production",
            title_ru="Meridian Zero",
            tagline_ru="Акустика глубин.",
            short_description_ru="Экспериментальная тактическая телеметрия.",
            genre_ru="Тактический симулятор",
            status_ru="Пре-продакшн",
            cover_image="/static/images/meridian_cover.svg",
            hero_image="/static/images/meridian_hero.svg",
            is_featured=True,
            is_published=True
        )
        db.session.add_all([game1, game2])

        # Seed two articles to verify lead article and secondary stack
        art1 = Article(
            slug="consequential-systems",
            title_en="Systems That Consequence",
            excerpt_en="Why tactile agency matters.",
            content_en="Manifesto text body 1.",
            category_en="Philosophy",
            title_ru="Системы с последствиями",
            excerpt_ru="Почему важна осязаемая агентность.",
            content_ru="Текст статьи 1.",
            category_ru="Философия",
            is_published=True
        )
        art2 = Article(
            slug="acoustic-architecture",
            title_en="Acoustic Architecture",
            excerpt_en="Spatial sound design in dead corridors.",
            content_en="Manifesto text body 2.",
            category_en="Engineering",
            title_ru="Акустическая архитектура",
            excerpt_ru="Пространственный звук в заброшенных коридорах.",
            content_ru="Текст статьи 2.",
            category_ru="Инженерия",
            is_published=True
        )
        db.session.add_all([art1, art2])

        career = Career(
            slug="systems-architect",
            title_en="Systems Architect",
            department_en="Core Tech",
            location_en="Remote / Orbital",
            description_en="Engine low-level performance.",
            requirements_en="C++, memory layout, deterministic networks.",
            title_ru="Архитектор систем",
            department_ru="Базовые технологии",
            location_ru="Удаленно",
            description_ru="Низкоуровневая оптимизация.",
            requirements_ru="C++, оптимизация памяти, детерминированные сети.",
            is_published=True
        )
        db.session.add(career)
        db.session.commit()

    def tearDown(self):
        db = get_db()
        db.session.rollback()
        self.app_context.pop()

    def test_global_hud_telemetry_presence(self):
        """Verify the footer telemetry ribbon on all pages and top HUD removal."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}")
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(b"telemetry-hud-strip", res.data)
            self.assertIn(b"footer-telemetry-ribbon", res.data)

    def test_homepage_asymmetric_flagship_and_axioms(self):
        """Verify Homepage features the asymmetric editorial hero, flagship showcase, and axioms."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}")
            self.assertIn(b"hero-editorial-grid", res.data)
            self.assertIn(b"flagship-showcase-card", res.data)
            self.assertIn(b"secondary-projects-grid", res.data)
            self.assertIn(b"axioms-editorial-layout", res.data)
            self.assertIn(b"axiom-card", res.data)
            self.assertIn(b"journal-lead-card", res.data)
            self.assertIn(b"journal-secondary-stack", res.data)

    def test_games_catalog_dossier_structure(self):
        """Verify Catalog features the lead showcase and dossier cards."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/games")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"catalog-lead-showcase", res.data)
            self.assertIn(b"catalog-dossier-grid", res.data)
            self.assertIn(b"telemetry-filter-bar", res.data)

    def test_game_detail_widescreen_and_specs_ribbon(self):
        """Verify Game Detail features widescreen visual, specs ribbon, and systems terminal."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/games/aegis-decay")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"project-hero-section", res.data)
            self.assertIn(b"telemetry-specs-ribbon", res.data)
            self.assertIn(b"project-body-grid", res.data)
            self.assertIn(b"systems-terminal-panel", res.data)

    def test_about_manifesto_and_metrics_terminal(self):
        """Verify About page features editorial manifesto spread and studio status terminal."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/about")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"about-manifesto-grid", res.data)
            self.assertIn(b"studio-status-terminal", res.data)
            self.assertIn(b"about-pillars-editorial-grid", res.data)
            self.assertIn(b"collaboration-terminal-card", res.data)

    def test_news_ledger_and_article_detail(self):
        """Verify News listing features lead card + ledger stack, and detail features longform spread."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/news")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"journal-lead-card", res.data)
            self.assertIn(b"journal-ledger-stack", res.data)

            res_detail = self.client.get(f"/{lang}/news/consequential-systems")
            self.assertEqual(res_detail.status_code, 200)
            self.assertIn(b"article-editorial-header", res_detail.data)
            self.assertIn(b"article-editorial-footer", res_detail.data)

    def test_careers_terminal_and_roles(self):
        """Verify Careers page features recruitment dossier and station billets."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/careers")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"careers-philosophy-dossier", res.data)
            self.assertIn(b"station-role-card", res.data)
            self.assertIn(b"STATION BILLET", res.data)

    def test_contact_transmission_console(self):
        """Verify Contact page features console HUD bar, CSRF token, and channels."""
        for lang in ["en", "ru"]:
            res = self.client.get(f"/{lang}/contact")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"terminal-console-panel", res.data)
            self.assertIn(b"console-hud-bar", res.data)
            self.assertIn(b'name="csrf_token"', res.data)
            self.assertIn(b"dossier-terminal-box", res.data)

if __name__ == "__main__":
    unittest.main()
