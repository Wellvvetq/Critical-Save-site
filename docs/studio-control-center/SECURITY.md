# CRITICAL SAVE STUDIO — SECURITY & INTEGRITY SPECIFICATION

## 1. Threat Model & Safeguards

The Studio Control Center implements defense-in-depth principles across authentication, persistence, and static distribution.

---

## 2. Authentication & Session Security

1. **Password Hashing**: Uses `werkzeug.security` (`pbkdf2:sha256` or `scrypt`) with per-user salt and high iteration counts. Plaintext passwords are never stored.
2. **Role-Based Access Control (RBAC)**:
   - `@login_required`: Blocks unauthenticated requests and redirects to `/admin/login`.
   - `@role_required("owner")`: Restricts critical actions (publishing live builds, managing operator accounts, authorizing releases) exclusively to Owner accounts.
3. **Session Cookies**: Configured with `HttpOnly`, `SameSite=Lax`, and session destruction upon logout.
4. **Self-Lockout Prevention**: Owners cannot deactivate their own active account session.

---

## 3. CSRF & Form Integrity

1. Every mutating administrative form (`POST`, `PUT`, `DELETE`) enforces a session-bound cryptographic CSRF token via `validate_csrf_token()`.
2. Missing or mismatched CSRF tokens immediately abort with HTTP 400 Bad Request.

---

## 4. Content Security Policy (CSP) & HTTP Headers

The Flask application and static outputs enforce strict security headers:
- `Content-Security-Policy`: Restricts scripts and styles to self and vetted Google Font domains.
- `X-Frame-Options: SAMEORIGIN`: Prevents clickjacking attacks.
- `X-Content-Type-Options: nosniff`: Prevents MIME-confusion exploits.
- `Referrer-Policy: strict-origin-when-cross-origin`.

---

## 5. File Upload Sanitation

1. Media uploads through `/admin/media/upload` are validated against a strict extension whitelist (`png`, `jpg`, `jpeg`, `webp`, `gif`, `svg`).
2. Uploaded files receive randomized UUID filenames via `uuid.uuid4().hex` to prevent directory traversal (`../`) attacks or script execution exploits.

---

## 6. Financial Data & Desktop Binary Isolation

1. **Zero Access to User Financial Data**: The website and Studio Control Center operate completely outside of `%LOCALAPPDATA%\FinancialWarRoom\` or any user desktop databases.
2. **Cryptographic Checksum Enforcement**: Installers published to users are verified with SHA-256 telemetry. Mismatched files are blocked by the 4-Stage Release Gate.
