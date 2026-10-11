# Critical Save Studio — Production Website

A distinctive, atmospheric, bilingual (EN / RU) web platform for **Critical Save Studio**, an independent game development studio specializing in narrative agency, tension, and consequential choices.

Built with Python 3, Flask, SQLAlchemy, semantic HTML5, and a custom cinematic dark design system.

---

## 1. Architecture & Design Principles

- **Framework**: Python 3.14 + Flask 3.1 + SQLAlchemy 2.0.
- **Visual Identity**: Cinematic dark graphite palette (`#07080a`, `#0e1015`), electric amber focal accents (`#f59e0b`), typographic hierarchy (`Cinzel` / `Inter` / `JetBrains Mono`), restrained geometric brand mark, and high-contrast composition.
- **Bilingual Strategy**: Full URL-based localization (`/en/...` and `/ru/...`) with complete dictionaries for UI, forms, and database-level bilingual attributes (`title_en`/`title_ru`, `description_en`/`description_ru`, etc.).
- **Content Management**: Production-grade Administrative Control Center (`/admin/`) with bcrypt password hashing, session authentication, CSRF/method enforcement, draft/publish workflows, and file upload validation.
- **Inquiry Queue**: Public inquiries are persisted to `contact_inquiries` with status lifecycles (`new`, `in_review`, `processed`, `archived`) and optional SMTP dispatch.
- **Accessibility & SEO**: WCAG 2.2 AA compliant focus rings, skip-to-content links, `prefers-reduced-motion` overrides, dynamic `sitemap.xml`, and security-tailored `robots.txt`.

---

## 2. Directory Structure

```
critical_save_studio/
├── app/
│   ├── models/            # SQLAlchemy database schemas (User, Game, Article, Career, Inquiry)
│   ├── routes/            # Blueprint route definitions (public.py, admin.py)
│   ├── services/          # Services (auth.py, db.py, i18n.py, contact.py, media.py)
│   ├── static/
│   │   ├── css/           # Cinematic design system (main.css, admin.css)
│   │   ├── js/            # Client scripts (mobile navigation, accessible lightbox)
│   │   ├── images/        # Original vector logos and concept artwork
│   │   └── uploads/       # Secure file upload storage
│   ├── templates/
│   │   ├── public/        # Bilingual public templates (index, games, about, news, careers, contact)
│   │   ├── admin/         # Control center templates (dashboard, CRUD forms, inquiries)
│   │   └── errors/        # Styled 404 & 500 error pages
│   └── __init__.py        # Application factory & security middleware
├── data/                  # SQLite database directory (critical_save.db)
├── tests/                 # Unit & integration test suite (test_suite.py)
├── config.py              # Configuration classes
├── seed_db.py             # Database initialization & seeding script
├── run.py                 # Application launcher
├── requirements.txt       # Dependencies
└── .env.example           # Environment template
```

---

## 3. Getting Started

### Prerequisites
- Python 3.10+ (Current runtime: Python 3.14)
- Packages: `Flask`, `SQLAlchemy`, `bcrypt`, `Werkzeug`

### Quick Start Commands
1. **Initialize & Seed the Database**:
   ```bash
   python seed_db.py
   ```
   *Creates the SQLite schema, registers the initial administrator (`admin` with password configured in `.env` or randomly generated on first run), and seeds studio projects, journal essays, and career requisitions.*

2. **Run Automated Test Suite**:
   ```bash
   python -m unittest tests/test_suite.py
   ```

3. **Start the Local Development Server**:
   ```bash
   python run.py
   ```
   Open your browser to [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 4. Administrative Gateway

- **URL**: `http://127.0.0.1:5000/admin/login`
- **Default Username**: `admin`
- **Password**: Configured via `INITIAL_ADMIN_PASSWORD` in `.env` (or printed by `seed_db.py` on first run).

---

## 5. Environment Variables

Refer to `.env.example`:
- `SECRET_KEY`: Random session secret.
- `DATABASE_URL`: `sqlite:///data/critical_save.db` or PostgreSQL connection URI.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Optional credentials for outbound transactional mail. If omitted, inquiries are securely queued in the database.
