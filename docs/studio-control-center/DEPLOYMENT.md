# CRITICAL SAVE STUDIO — ZERO-COST DEPLOYMENT MANUAL

This guide covers deploying Critical Save Studio to **GitHub Pages** (primary static distribution) and optionally configuring **Cloudflare Serverless Edge** (remote headless administration) with \$0.00 infrastructure cost.

---

## 1. Primary Deployment: GitHub Pages (Recommended)

### Step 1: Create a Remote GitHub Repository
1. On GitHub, create a new repository: e.g. `critical-save-studio` or `<username>.github.io`.
2. Do **NOT** upload installer executables (`.exe`) directly into Git. The repository's `.gitignore` already excludes `*.exe`, `.env`, and database files.

### Step 2: Push Local Code to GitHub
Open PowerShell in the project directory:
```powershell
cd C:\Users\PLATINUM\.gemini\antigravity\scratch\critical_save_studio
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git add .
git commit -m "feat: Critical Save Studio with Studio Control Center 1.0"
git push -u origin main
```

### Step 3: Configure GitHub Pages Settings
1. Navigate to your repository on GitHub -> **Settings** -> **Pages**.
2. Under **Build and deployment** -> **Source**, select **GitHub Actions**.
3. The `.github/workflows/deploy.yml` workflow will automatically trigger on push:
   - Sets up Python 3.11.
   - Executes test suite (`pytest tests/test_studio_control_center.py tests/test_suite.py`).
   - Freezes static website to `dist/`.
   - Publishes directly to your GitHub Pages URL (e.g. `https://<username>.github.io/<repo>/`).

---

## 2. Binary Distribution: Avenor Desktop Installers

GitHub Pages and Git repositories have file size limits (100MB per file recommendation). The verified Avenor installers are:
- `Avenor-Setup-5.0.0.exe`: **159.0 MB**
- `Avenor-Offline-Setup-5.0.0.exe`: **614.7 MB**

### Recommended Distribution Methods (100% Free Tier):
1. **GitHub Releases (Recommended)**:
   - Go to your GitHub repository -> **Releases** -> **Draft a new release**.
   - Tag: `v5.0.0`, Title: `Avenor — Personal Finance Intelligence v5.0.0`.
   - Upload both `.exe` files into the release assets.
   - Copy the direct download links into the Studio Control Center release editor.
2. **Cloudflare R2 (Alternative Free Tier)**:
   - Cloudflare R2 includes 10GB free storage and \$0.00 egress bandwidth fees.

---

## 3. Remote Serverless Edge (Cloudflare Workers + D1)

When the host PC is turned off, operators can still manage releases and trigger rebuilds using Cloudflare Workers:

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```
2. Authenticate with Cloudflare:
   ```bash
   wrangler login
   ```
3. Create D1 Database:
   ```bash
   wrangler d1 create critical_save_studio_db
   ```
4. Update `cloudflare/wrangler.toml` with the generated `database_id`.
5. Execute schema migration:
   ```bash
   wrangler d1 execute critical_save_studio_db --file=cloudflare/schema.sql
   ```
6. Deploy the edge worker:
   ```bash
   wrangler deploy
   ```
