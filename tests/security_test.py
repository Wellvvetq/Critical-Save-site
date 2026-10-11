"""
Security and Regression Test Suite for Critical Save Studio (Iteration 2).
Specifically verifies CSRF protection, sliding-window Rate Limiting, 
and unauthorized request rejections.
"""
import unittest
from app import create_app
from config import Config
from app.services.db import get_db
from app.models import User, Game, ContactInquiry
from app.services.limiter import reset_rate_limiter

class StrictSecurityConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = True  # Enable strict CSRF enforcement during test

class SecurityTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app(StrictSecurityConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        reset_rate_limiter()

        db = get_db()
        admin = User(username="secadmin", role="admin")
        admin.set_password("SecurePassword2026!")
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db = get_db()
        db.session.rollback()
        self.app_context.pop()
        reset_rate_limiter()

    def test_csrf_token_enforced_on_contact_post(self):
        # 1. Post without CSRF token should fail with 400 Bad Request
        res_no_csrf = self.client.post("/en/contact", data={
            "name": "Attacker",
            "email": "attacker@evil.com",
            "subject": "Spam",
            "message": "Forged request without token",
            "consent": "on"
        })
        self.assertEqual(res_no_csrf.status_code, 400)
        self.assertIn(b"CSRF token validation failed", res_no_csrf.data)

        # 2. Get the contact page to generate session CSRF token
        get_res = self.client.get("/en/contact")
        self.assertEqual(get_res.status_code, 200)

        # Retrieve token from session
        with self.client.session_transaction() as sess:
            token = sess.get("_csrf_token")
        self.assertIsNotNone(token)

        # 3. Post with valid CSRF token succeeds
        res_valid = self.client.post("/en/contact", data={
            "csrf_token": token,
            "name": "Valid Citizen",
            "email": "valid@studio.com",
            "subject": "General Studio Inquiry",
            "message": "Valid transmission with correct cryptographic token.",
            "consent": "on"
        })
        self.assertEqual(res_valid.status_code, 200)
        self.assertIn(b"Message Received", res_valid.data)

    def test_contact_form_rate_limiting(self):
        # Obtain session CSRF token
        self.client.get("/en/contact")
        with self.client.session_transaction() as sess:
            token = sess.get("_csrf_token")

        payload = {
            "csrf_token": token,
            "name": "Repetitive Sender",
            "email": "sender@spam-test.com",
            "subject": "Spam Loop",
            "message": "Checking rate limit boundaries.",
            "consent": "on"
        }

        # First 5 submissions are accepted
        for _ in range(5):
            res = self.client.post("/en/contact", data=payload, environ_base={'REMOTE_ADDR': '198.51.100.1'})
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Message Received", res.data)

        # 6th submission from same IP is rate-limited
        blocked_res = self.client.post("/en/contact", data=payload, environ_base={'REMOTE_ADDR': '198.51.100.1'})
        self.assertEqual(blocked_res.status_code, 200)
        self.assertIn(b"Rate limit exceeded", blocked_res.data)

    def test_csrf_token_enforced_on_admin_login(self):
        # Post to login without CSRF token fails
        res_no_csrf = self.client.post("/admin/login", data={
            "username": "secadmin",
            "password": "SecurePassword2026!"
        })
        self.assertEqual(res_no_csrf.status_code, 400)

        # Retrieve valid token
        self.client.get("/admin/login")
        with self.client.session_transaction() as sess:
            token = sess.get("_csrf_token")

        # Post with valid CSRF token succeeds
        res_valid = self.client.post("/admin/login", data={
            "csrf_token": token,
            "username": "secadmin",
            "password": "SecurePassword2026!"
        }, follow_redirects=True)
        self.assertEqual(res_valid.status_code, 200)
        self.assertIn(b"Operational Telemetry", res_valid.data)

if __name__ == "__main__":
    unittest.main()
