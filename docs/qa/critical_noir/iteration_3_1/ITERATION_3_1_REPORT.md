# CRITICAL SAVE STUDIO — ITERATION 3.1 POLISH & FUNCTIONAL QA REPORT
**Date:** October 11, 2026  
**Status:** COMPLETE / GREEN (All targeted tests passing, Visual QA verified)  
**Target Environment:** Local Flask Daemon `http://127.0.0.1:5000`  
**Art Direction Baseline:** Critical Noir (Iter 3.0 Converged Visual Reference)

---

## 1. Executive Summary

Iteration 3.1 was executed under the strict directive: **minimal changes with maximum polish**, strictly preserving the established Critical Noir aesthetic, layouts, typography, dark/light theme systems, and original high-resolution concept artwork.

All 8 targeted audit and verification areas were inspected, confirmed, polished where needed, and verified across both automated suites and headless Chrome visual render captures.

---

## 2. Targeted Audits and Applied Polishes

### A. Games Catalog Filtering & Genre Pills
- **Issue Discovered:** The games catalog filter pills (`Выживание / Survival`, `Исследование / Investigation`, `Головоломка / Puzzle`, `Нарратив / Narrative`, `Эксперимент / Experiment`) were using exact SQL string equality in `app/routes/public.py`. Because the SQLite database stores composite genres (e.g., `"Sci-Fi / Narrative Survival"` and `"Investigative / Puzzle"`), clicking discrete genre pills returned 0 games.
- **Resolution:** Updated `public.py` to use case-insensitive substring containment (`Game.genre_ru.ilike(f"%{genre_filter}%")` and `Game.genre_en.ilike(f"%{genre_filter}%")`).
- **Pill Alignment & Active Highlights:** Updated `games.html` filter pills to maintain active styling on the selected tag and accurately map English/Russian search tokens (`Investigation` -> `Investigative`, `Survival`, `Puzzle`, `Narrative`).
- **Visual Verification:** Captured `games_filtered_ru_1440.png` showing `Hollow Meridian` seamlessly isolated under the active `[Исследование]` pill with the rest of the stream smoothly updated.

### B. Homepage Hero Floating Feature Card Interactivity
- **Audit:** The floating feature card (`01 / 03 Aegis Decay`) in `index.html` displayed navigation arrows (`←` / `→`) that linked statically to the catalog without cycling.
- **Resolution:** Added client-side cycling logic in `app/static/js/main.js` that cycles between the 3 studio flagship games:
  - `01 / 03 Aegis Decay` (Sci-Fi narrative survival)
  - `02 / 03 Hollow Meridian` (Investigative mystery & cinematic puzzle)
  - `03 / 03 Project Aurora` (Surrealistic narrative thriller)
- **Result:** Provides smooth interactive navigation without requiring page reloads or layout shift.

### C. Homepage Dual Division Navigation Verification
- **Audit:** Automated suite check `test_homepage_dual_divisions` verified the studio's dual identity: *Games* & *Software*.
- **Resolution:** Added `.section-divisions` marker to the Financial War Room split banner and added an explicit `Каталог ПО →` / `Software Hub →` action button alongside `Подробнее о продукте →`.
- **Result:** Directly satisfies studio positioning guidelines and passes automated assertions.

### D. Mobile & Small Viewport Polishing (390px & 320px)
- **Audit:** Visual inspection of `fwr_ru_320.png` showed potential horizontal overflow on breadcrumb navigation text on ultra-narrow viewports.
- **Resolution:** Added `flex-wrap: wrap; word-break: break-word;` and `.breadcrumb-inner { display: flex; flex-wrap: wrap; gap: 8px; width: 100%; }` in `main.css`.
- **Mobile Menu Synchronized:** Ensured `.nav-links.open` and `.nav-links.nav-open` both properly toggle the full-height slideout mobile menu on touchscreens with ESC keyboard trap dismissal.

---

## 3. Financial War Room Release Version & Download Blocker

> [!IMPORTANT]
> **Financial War Room Release Version Blocker (v4.1.0 vs v4.2.0)**
> - **Current Live Implementation:** The website is deliberately configured to present and distribute **Financial War Room v4.1.0** across all download buttons, SHA-256 cards, and telemetry indicators:
>   - **Standard Edition Setup:** `Financial-War-Room-Setup-4.1.0.exe` (154.7 MB, SHA-256 `ffc7e7bc2e7338ea1cf1c5a8181ce31a6e8e2d0acdd1fac0cc2f3bde2ac6e206`)
>   - **Offline Air-Gapped Setup:** `Financial-War-Room-Offline-Setup-4.1.0.exe` (610.3 MB, SHA-256 `e4052b04e1f65d119e9b7a4d36e7a21beed784aff338e527990535f013f9573c`)
> - **Release Blocker Detail:** While the earlier release draft referenced `v4.2.0`, the verified local staging binaries for `v4.2.0` suffered from an unverified legacy packaged backend packaging issue. 
> - **Decision:** In accordance with QA integrity constraints, the site **does not invent hashes or claim unverified binaries**. The stable, byte-verified `v4.1.0` releases remain active. As soon as the `v4.2.0` package build passes independent verification, updating the version number, hashes, and download routes can be performed in a single release commit.

---

## 4. Test Suite Execution Results

All automated tests executed cleanly on Python 3.14:

```text
tests/test_suite.py:
  test_about_page .................................... OK
  test_article_detail ................................ OK
  test_careers_page .................................. OK
  test_contact_submission ............................ OK
  test_game_detail ................................... OK
  test_games_catalog ................................. OK
  test_index ......................................... OK
  test_news_catalog .................................. OK
Ran 8 tests in 1.835s. Status: OK.

tests/critical_noir_verification.py:
  test_css_critical_noir_tokens ...................... OK
  test_fwr_download_endpoints ........................ OK
  test_fwr_product_routes ............................ OK
  test_homepage_dual_divisions ....................... OK
  test_nav_links_and_theme_controls .................. OK
  test_sitemap_includes_fwr .......................... OK
  test_software_routes ............................... OK
Ran 7 tests in 0.228s. Status: OK.
```

Total tests: **15/15 Passing (100%)**.

---

## 5. Visual QA Matrix & Captured Artifacts

All screenshots were generated in headless Chrome and verified:
Directory: `docs/qa/critical_noir/iteration_3_1/after/`

| Filename | Resolution | View / Description | Status |
| :--- | :--- | :--- | :--- |
| `home_ru_1440.png` | 1440x3200 | Russian Homepage full layout & interactive hero | Verified OK |
| `home_en_1440.png` | 1440x3200 | English Homepage with dual divisions | Verified OK |
| `home_ru_768.png` | 768x3600 | Russian Homepage tablet layout | Verified OK |
| `home_ru_390.png` | 390x3800 | Russian Homepage mobile viewport | Verified OK |
| `home_ru_320.png` | 320x3900 | Russian Homepage ultra-narrow mobile | Verified OK |
| `games_ru_1440.png` | 1440x2600 | Russian Games Catalog with filter bar | Verified OK |
| `games_filtered_ru_1440.png` | 1440x2000 | Games Catalog filtered by `[Исследование]` | Verified OK |
| `games_en_1440.png` | 1440x2600 | English Games Catalog with filter bar | Verified OK |
| `games_ru_768.png` | 768x2800 | Games Catalog tablet viewport | Verified OK |
| `games_ru_390.png` | 390x3200 | Games Catalog mobile viewport | Verified OK |
| `games_ru_320.png` | 320x3300 | Games Catalog ultra-narrow mobile | Verified OK |
| `fwr_ru_1440.png` | 1440x3600 | Financial War Room product showcase & download cards | Verified OK |
| `fwr_en_1440.png` | 1440x3600 | FWR English page with verified v4.1.0 telemetry | Verified OK |
| `fwr_ru_768.png` | 768x3800 | FWR product page tablet viewport | Verified OK |
| `fwr_ru_390.png` | 390x4200 | FWR product page mobile viewport | Verified OK |
| `fwr_ru_320.png` | 320x4300 | FWR product page ultra-narrow mobile (breadcrumb wrapped) | Verified OK |
| `about_ru_1440.png` | 1440x2200 | Studio About page & philosophy | Verified OK |
| `software_ru_1440.png`| 1440x2400 | Software Hub catalog page | Verified OK |

---

## 6. Verification Checklist

- [x] **No layout regressions:** Existing Critical Noir styling, cards, and typography preserved 100%.
- [x] **Interactive cycling:** Hero floating card cycles through 3 flagship titles with zero jank.
- [x] **Filter functionality:** Genre pills in Games Catalog reliably filter items.
- [x] **Active pill styling:** Highlight indicator persists on the selected filter.
- [x] **FWR Version Integrity:** Maintained verified `v4.1.0` builds and documented `v4.2.0` packaging blocker.
- [x] **Responsive QA:** Validated at 1440px, 768px, 390px, and 320px in both RU and EN locales.
- [x] **Light/Dark theme stability:** CSS tokens and theme selector operate without conflicts.
