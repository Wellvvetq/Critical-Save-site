"""
Critical Save Studio — Critical Noir & Financial War Room Verification Tests
Verifies:
1. Product routes (/products/financial-war-room, /ru/products/financial-war-room, /en/products/financial-war-room)
2. Download endpoints (/download/fwr/standard, /download/fwr/offline)
3. SHA-256 and metadata accuracy
4. Critical Noir CSS tokens and Light Theme styles
5. Product spotlight in Index & Games templates
"""

import unittest
from pathlib import Path
from app import create_app
from config import TestConfig


class TestCriticalNoirAndFWR(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.root_dir = Path(__file__).resolve().parent.parent

    def test_fwr_product_routes(self):
        # Base route should redirect to default language or localized path
        response = self.client.get('/products/financial-war-room')
        self.assertIn(response.status_code, [200, 301, 302])

        # Localized Russian route
        res_ru = self.client.get('/ru/products/financial-war-room')
        self.assertEqual(res_ru.status_code, 200)
        self.assertIn("Financial War Room".encode('utf-8'), res_ru.data)
        self.assertIn("Центр загрузки".encode('utf-8'), res_ru.data)
        self.assertIn("ffc7e7bc2e7338ea1cf1c5a8181ce31a6e8e2d0acdd1fac0cc2f3bde2ac6e206".encode('utf-8'), res_ru.data)

        # Localized English route
        res_en = self.client.get('/en/products/financial-war-room')
        self.assertEqual(res_en.status_code, 200)
        self.assertIn("Financial War Room".encode('utf-8'), res_en.data)
        self.assertIn("Download Center".encode('utf-8'), res_en.data)
        self.assertIn("e4052b04e1f65d119e9b7a4d36e7a21beed784aff338e527990535f013f9573c".encode('utf-8'), res_en.data)

    def test_fwr_download_endpoints(self):
        # Head request for standard download
        res_std = self.client.head('/download/fwr/standard')
        self.assertEqual(res_std.status_code, 200)
        self.assertIn("attachment", res_std.headers.get("Content-Disposition", ""))

        # Head request for offline download
        res_off = self.client.head('/download/fwr/offline')
        self.assertEqual(res_off.status_code, 200)
        self.assertIn("attachment", res_off.headers.get("Content-Disposition", ""))

        # Invalid edition
        res_inv = self.client.get('/download/fwr/unknown')
        self.assertEqual(res_inv.status_code, 404)

    def test_css_critical_noir_tokens(self):
        css_path = self.root_dir / 'app' / 'static' / 'css' / 'main.css'
        self.assertTrue(css_path.exists())
        content = css_path.read_text(encoding='utf-8')

        # Check Critical Noir palette tokens
        self.assertIn('--color-noir-void: #0B0B12;', content)
        self.assertIn('--color-noir-obsidian: #12121C;', content)
        self.assertIn('--color-noir-violet: #8B78E6;', content)
        self.assertIn('--color-noir-iris: #A99AFB;', content)

        # Check light theme data attribute
        self.assertIn('[data-theme="light"]', content)

        # Check FWR components
        self.assertIn('.fwr-hero-section', content)
        self.assertIn('.download-cards-grid', content)
        self.assertIn('.checksum-box', content)

    def test_nav_links_and_theme_controls(self):
        res = self.client.get('/ru')
        self.assertEqual(res.status_code, 200)
        self.assertIn("theme-toggle-btn".encode('utf-8'), res.data)
        self.assertIn("/products/financial-war-room".encode('utf-8'), res.data)

    def test_sitemap_includes_fwr(self):
        res = self.client.get('/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        self.assertIn("/products/financial-war-room".encode('utf-8'), res.data)

    def test_software_routes(self):
        # Base software route redirect
        res_redir = self.client.get('/software')
        self.assertIn(res_redir.status_code, [200, 301, 302])

        # Localized Russian software catalog
        res_ru = self.client.get('/ru/software')
        self.assertEqual(res_ru.status_code, 200)
        self.assertIn("Financial War Room".encode('utf-8'), res_ru.data)
        self.assertIn("Программное обеспечение".encode('utf-8'), res_ru.data)

        # Localized English software catalog
        res_en = self.client.get('/en/software')
        self.assertEqual(res_en.status_code, 200)
        self.assertIn("Financial War Room".encode('utf-8'), res_en.data)
        self.assertIn("Software & Digital Tools".encode('utf-8'), res_en.data)

    def test_homepage_dual_divisions(self):
        res = self.client.get('/ru')
        self.assertEqual(res.status_code, 200)
        self.assertIn("section-divisions".encode('utf-8'), res.data)
        self.assertIn("/ru/games".encode('utf-8'), res.data)
        self.assertIn("/ru/software".encode('utf-8'), res.data)


if __name__ == '__main__':
    unittest.main()
