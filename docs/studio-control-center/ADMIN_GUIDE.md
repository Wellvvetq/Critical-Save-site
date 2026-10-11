# CRITICAL SAVE STUDIO — OPERATOR MANUAL & CONTROL CENTER GUIDE

Welcome to **Studio Control Center**, the administrative command hub for Critical Save Studio.

---

## 1. Access & Role Hierarchies

Access the admin interface at `/admin/login`.

| Role | Permissions & Authority | Typical User |
| :--- | :--- | :--- |
| **Owner** | Full authority: draft & publish content, create software releases, sign off 4-stage release gates, trigger production builds, invite/deactivate operators, view audit trails. | Studio Founder / Lead Architect |
| **Editor** | Content staging: draft pages, upload media assets, update copywriting, view translation completeness, stage release proposals. Cannot trigger live production publication or modify operator credentials. | Co-creator / Narrative Designer |

---

## 2. Navigating the Control Center

### 2.1 Overview
- **Dashboard (`/admin`)**: Telemetry overview showing active games, software products, live releases, pending draft changes, and recent audit events.
- **Publishing Center (`/admin/publishing`)**: Automated pre-flight checklist. Allows the Owner to freeze all changes and deploy to the live site with one click.

### 2.2 Content & Works
- **Pages & Blocks (`/admin/pages`)**: Edit hero badges, headlines, and lead manifestos for core pages without touching code. Supports draft staging.
- **Games & Worlds (`/admin/games`)**: Manage game projects, genres, release statuses, cover artwork, and feature lists.
- **Software & Tools (`/admin/software`)**: Register standalone desktop tools (e.g. Avenor / Financial War Room).
- **Releases & SHA-256 (`/admin/releases`)**: Manage software versions and configure the 4-Stage Verification Gate.
- **Media Library (`/admin/media`)**: Securely upload artworks (`.png`, `.jpg`, `.webp`, `.svg`). One-click copy for clean asset URLs.
- **Journal Entries (`/admin/articles`)**: Publish devlogs, production dispatches, and narrative explorations.
- **Careers (`/admin/careers`)**: Manage studio openings and job descriptions.

### 2.3 Management & Access
- **Localization RU/EN (`/admin/localization`)**: Live parity checker comparing English and Russian dictionaries. Surfaces missing keys instantly.
- **Team & Access (`/admin/team`)**: Owner-only interface for registering new operator accounts or revoking active credentials.
- **Inbound Inquiries (`/admin/inquiries`)**: View and triage incoming contact form submissions.

---

## 3. The 4-Stage Release Verification Gate

Before any binary installer is served to visitors on the Download Center, it must pass all 4 stages:

1. **Stage 1 (Files Found)**: Confirm installer binary exists on target distribution storage.
2. **Stage 2 (Checksum Verified)**: Confirm SHA-256 hash matches the output of `Get-FileHash`.
3. **Stage 3 (Backend Smoke Tested)**: Confirm local AI backend and model loading pass verification.
4. **Stage 4 (Owner Sign-off)**: Owner reviews all three stages and authorizes live publication.

Once all four are checked, `is_live` becomes active, and the download card immediately lights up for public visitors.
