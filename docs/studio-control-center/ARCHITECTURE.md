# CRITICAL SAVE STUDIO — CONTROL CENTER ARCHITECTURE

## 1. System Overview

**Studio Control Center** is a dual-track content management and release orchestration architecture designed specifically for Critical Save Studio. It bridges local-first administrative ergonomics with zero-cost, high-availability static edge distribution.

```
+---------------------------------------------------------------------------------------+
|                               CRITICAL SAVE STUDIO ECOSYSTEM                          |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   [ LOCAL / SELF-HOSTED CONTROL TIER ]                                                |
|   Flask Application (`app/`)                                                          |
|   ├── Studio Control Center (`/admin`)                                                |
|   │   ├── Owner & Editor RBAC                                                        |
|   │   ├── Structured Block Editor (`PageContent`)                                     |
|   │   ├── Software Catalog & 4-Stage Release Gate (`SoftwareRelease`)                 |
|   │   ├── Media Library & Asset Ingestion                                             |
|   │   ├── Localization Verification (`TRANSLATIONS` RU/EN)                           |
|   │   └── Audit Logging (`AuditLog`)                                                 |
|   │                                                                                   |
|   └── Static Exporter Pipeline (`app/services/static_exporter.py`)                    |
|       └── Freezes 30+ endpoints -> `dist/` (HTML + Assets + `.nojekyll`)              |
|                                                                                       |
+---------------------------------------+-----------------------------------------------+
                                        | Push / CI Dispatch
                                        v
+---------------------------------------------------------------------------------------+
|   [ PRODUCTION DISTRIBUTION TIER (FREE EDGE) ]                                        |
|                                                                                       |
|   1. GitHub Pages (Primary Public Site)                                               |
|      - Serves static bundle from `dist/`                                              |
|      - Ultra-fast global CDN, HTTPS included, 99.99% uptime                           |
|      - Unlimited public bandwidth within fair use                                     |
|                                                                                       |
|   2. External Binary Distribution Gate                                                |
|      - GitHub Releases / Cloudflare R2 / External Object Storage                      |
|      - Hosts `Avenor-Setup-5.0.0.exe` (159 MB) & `Avenor-Offline-Setup-5.0.0.exe` (614 MB)|
|      - Verified via SHA-256 telemetry before download authorization                  |
|                                                                                       |
|   3. Cloudflare Serverless Edge (`cloudflare/worker.js` + D1)                         |
|      - Standby remote API when local machine is offline                               |
|      - Authenticates operators & dispatches GitHub Actions build workflows            |
+---------------------------------------------------------------------------------------+
```

---

## 2. Core Components

### 2.1 Dual-Track Content Model (`PageContent`)
To prevent accidental breakages, all editable pages support a draft-staging lifecycle:
- **`draft_data_json`**: Editable by both `Editor` and `Owner`. Changes take effect in preview mode.
- **`published_data_json`**: Immutable until authorized.
- **`has_unpublished_changes`**: Telemetry flag driving the badge count in the Publishing Center.
- **`publish_now`**: Only authorized for `Owner`. Promotes draft JSON to published JSON and freezes to `dist/`.

### 2.2 4-Stage Release Verification Gate (`SoftwareRelease`)
Distributing standalone desktop binaries (`Avenor` / `Financial War Room`) requires strict integrity verification before installers are surfaced on the Download Center:
1. **Stage 1 (Artifact Staging)**: Verifies that physical installer files exist at the designated path or URL.
2. **Stage 2 (Checksum Telemetry)**: Verifies file size and independent SHA-256 checksums match physical bytes.
3. **Stage 3 (Backend Architecture Smoke Test)**: Verifies that the bundled Python AI backend loads cleanly without errors.
4. **Stage 4 (Owner Sign-Off)**: Only an account with role `Owner` can toggle `owner_approved = True`.

`is_live` is enforced programmatically:
$$\text{is\_live} = \text{file\_exists\_verified} \land \text{hash\_verified} \land \text{backend\_verified} \land \text{owner\_approved}$$

### 2.3 Static Exporter Pipeline (`app/services/static_exporter.py`)
- Simulates requests using Flask's native WSGI client.
- Renders all 30 core localized routes (`/en`, `/ru`, `/en/games`, `/ru/games`, game detail pages, `/en/products/financial-war-room`, `/ru/products/financial-war-room`, `/en/software`, `/ru/software`, `/en/about`, `/ru/about`, `/en/news`, `/ru/news`, `/en/careers`, `/ru/careers`, `/en/contact`, `/ru/contact`, `sitemap.xml`, `robots.txt`, `404.html`).
- Recursively copies `app/static/` (stylesheets, images, fonts, icons) into `dist/static/`.
- Emits `.nojekyll` to disable Jekyll processing on GitHub Pages.
- Supports configurable `base_path` for custom GitHub Pages subpath repositories.
