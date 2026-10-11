# CRITICAL SAVE STUDIO — WEBSITE REDESIGN & FWR INTEGRATION AUDIT
## Project: CRITICAL NOIR (Phase A: Preliminary Audit)

**Date:** 2026-10-11  
**Auditor:** Critical Save Studio Product & Engineering Team  
**Workspace:** `C:\Users\PLATINUM\.gemini\antigravity\scratch\critical_save_studio`  
**Related Product Repo:** `C:\Users\PLATINUM\.gemini\antigravity\scratch\financial-war-room`  

---

## 1. Executive Summary & Stack Discovery

Critical Save Studio is an independent studio developing atmospheric games, creative technology, and software products. The current web application is built on:
- **Backend / Routing:** Python 3.14 + Flask (`app/` application factory pattern)
- **Database / ORM:** SQLite (`data/critical_save.db`) + SQLAlchemy ORM (models: `Game`, `Article`, `Career`, `ContactInquiry`, `User`)
- **Internationalization:** Custom dictionary-based i18n (`app/services/i18n.py`) supporting English (`/en/...`) and Russian (`/ru/...`)
- **Security & Infrastructure:** Cryptographic CSRF session protection (`app/services/csrf.py`), in-memory sliding-window IP rate limiting (`app/services/limiter.py`), secure HTTP headers
- **Frontend Layer:** Jinja2 templates (`app/templates/`), responsive CSS (`app/static/css/main.css`), vanilla ES6 JavaScript (`app/static/js/main.js`)

---

## 2. Inventory of Existing Routes & Pages

| Route | Template | Purpose & Content | Status |
| :--- | :--- | :--- | :--- |
| `GET /` | Redirect | 302 redirect to `/{default_lang}` (`/en`) | Active |
| `GET /<lang>` | `public/index.html` | Homepage: Studio positioning, hero artwork, featured games, manifesto, journal | Active |
| `GET /<lang>/games` | `public/games.html` | Projects & Games Catalog with genre filter | Active |
| `GET /<lang>/games/<slug>` | `public/game_detail.html` | Game detail dossier (e.g., `project-aegis-decay`, `hollow-meridian`) | Active |
| `GET /<lang>/about` | `public/about.html` | Studio ethos, philosophy, creative pillars | Active |
| `GET /<lang>/news` | `public/news.html` | Studio Journal / Transmission feed | Active |
| `GET /<lang>/news/<slug>` | `public/article_detail.html` | Journal article longform reader | Active |
| `GET /<lang>/careers` | `public/careers.html` | Studio roles & competencies | Active |
| `GET, POST /<lang>/contact` | `public/contact.html` | Contact form with server-side validation & rate limiting | Active |
| `GET /sitemap.xml` | `public/sitemap.xml` | XML sitemap for search engines | Active |
| `GET /robots.txt` | Raw response | Search engine crawler rules | Active |
| `GET, POST /admin/login` | `admin/login.html` | Studio staff administration portal | Active |
| `GET /admin/dashboard` | `admin/dashboard.html` | Admin CMS dashboard | Active |
| `404 / 500` | `errors/*.html` | Custom error pages | Active |

---

## 3. Financial War Room (FWR) Discovery & Artifact Audit

We conducted an in-depth audit of `C:\Users\PLATINUM\.gemini\antigravity\scratch\financial-war-room`:

### 3.1. Product Positioning & Architecture
- **Nature of Product:** Local-first, privacy-focused desktop financial control center.
- **Core Engine:** FastAPI backend (`fwr-backend.exe`), deterministic decimal math (`Decimal`), SQLite database (`war_room.db`), React + TypeScript UI.
- **Key Modules:**
  1. Multicurrency account & transaction tracking (double-entry transfer invariant).
  2. Cash Flow Projection (7, 30, 90, 180-day trajectory with liquidity gap detection).
  3. Debt Payoff Engine (Avalanche vs Snowball comparison with interest savings).
  4. Scenario Lab (What-if stress testing without touching actual financial registers).
  5. Local AI Financial Advisor (read-only analytical advisor via Ollama or deterministic heuristic fallback).
  6. 2-phase import/export with JSON backup & restore.

### 3.2. Real Verified Installers & Release Files
Found in `financial-war-room/apps/web/dist-release/`:
- **Standard Edition:**
  - Filename: `Financial-War-Room-Setup-4.1.0.exe`
  - Exact Size: 162,232,092 bytes (~154.7 MB)
  - Date: 2026-10-11
  - Verified SHA-256: `ffc7e7bc2e7338ea1cf1c5a8181ce31a6e8e2d0acdd1fac0cc2f3bde2ac6e206`
  - Requirements: Windows 10/11 64-bit, 4 GB RAM. Connects to local Ollama if AI analysis is configured.
- **Offline Edition:**
  - Filename: `Financial-War-Room-Offline-Setup-4.1.0.exe`
  - Exact Size: 639,975,053 bytes (~610.3 MB)
  - Date: 2026-10-11
  - Verified SHA-256: `e4052b04e1f65d119e9b7a4d36e7a21beed784aff338e527990535f013f9573c`
  - Requirements: Windows 10/11 64-bit, 8 GB RAM. Bundles standalone runtime for zero-internet initial run.

### 3.3. Real Verified Screenshots
Available in `financial-war-room/docs/screenshots/`:
- `dashboard_final_1440.png` / `dashboard_en_dark_1440.png` / `dashboard_ru_dark_1440.png`
- `forecast_desktop_1440.png`
- `debts_ru_light_1440.png`
- `transactions_en_dark_1440.png`
- `iteration_4_0/01_ai_assistant_ready.png`
- `iteration_4_0/02_ai_financial_analysis_response.png`
- `iteration_3_1/05_settings_backup_restore.png`

---

## 4. Current Deficiencies & Redesign Scope

1. **Brand Aesthetic:** Currently uses cold-ice blue tokens (`#8FCBFA`). Needs full migration to the **CRITICAL NOIR** system:
   - Void (`#0B0B12`), Obsidian (`#12121C`), Aubergine (`#1B1928`), Violet (`#8B78E6`), Iris (`#A99AFB`), Platinum (`#D9DCE6`), Silver (`#A7ADBD`), Frost (`#F4F3F8`).
2. **Missing Product Integration:** The studio currently presents only games (`project-aegis-decay`, `hollow-meridian`), but lacks any product page or catalog integration for Financial War Room.
3. **Download Flow:** No Download Center exists for FWR installers.
4. **Theme Support:** Site needs explicit, polished Dark/Light/System theme toggling while preserving accessibility and high contrast.
5. **Mobile Refinement:** Navigation, hero layouts, and tables require dedicated QA across 390px, 768px, 1024px, 1440px, and 1920px.

---

## 5. Execution Plan

- **Phase B:** Deploy **Critical Noir** design tokens, typography, component library, and Dark/Light/System theme engine in `main.css` & `main.js`.
- **Phase C:** Redesign global header, navigation, footer, catalog, games, about, news, careers, and contact.
- **Phase D & E:** Implement `/products/financial-war-room` with real screenshots, verified feature breakdown, and Download Center with SHA-256 checksums and real installer delivery.
- **Phase F & G:** Comprehensive responsive QA and automated visual screenshot capture via headless Chrome.
- **Phase H:** Verification of all tests and generation of `docs/GLOBAL_WEBSITE_REDESIGN_REPORT.md`.
