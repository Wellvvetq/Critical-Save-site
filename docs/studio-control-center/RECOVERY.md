# CRITICAL SAVE STUDIO — DISASTER RECOVERY & BACKUP PROTOCOL

## 1. Backup Regimes

### 1.1 SQLite Database Backups
The authoritative studio database is located at `data/critical_save.db`.
- **Automatic Backup Location**: `data/critical_save.db.backup`
- **Manual Snapshot Command**:
  ```powershell
  Copy-Item data\critical_save.db data\critical_save_$(Get-Date -Format 'yyyyMMdd_HHmmss').db.bak
  ```

### 1.2 Static Bundle Rollback
Every production build is frozen into `dist/`.
If an unexpected issue occurs on the live GitHub Pages site:
1. Re-run `python -c "from app import create_app; from app.services.static_exporter import export_static_site; app = create_app(); export_static_site(app, 'dist')"`
2. Alternatively, rollback to the previous Git commit on the `main` branch:
   ```bash
   git revert HEAD
   git push origin main
   ```
   GitHub Actions will automatically redeploy the previous known-good static build.

---

## 2. Emergency Recovery Steps

### Scenario A: Operator Locks Themselves Out
To reset the owner password locally:
```powershell
python -c "from app.services.db import get_db; from app.models import User; from app import create_app; app = create_app();
with app.app_context():
    db = get_db()
    u = db.session.query(User).filter_by(username='admin').first()
    u.set_password('NewSecurePassword123!')
    u.is_active = True
    u.role = 'owner'
    db.session.commit()
    print('Password reset successful for user:', u.username)"
```

### Scenario B: Database File Corrupted
1. Stop any running Flask process.
2. Restore from backup:
   ```powershell
   Copy-Item data\critical_save.db.backup data\critical_save.db -Force
   ```
3. Run verification test suite:
   ```powershell
   pytest tests/test_studio_control_center.py tests/test_suite.py -v
   ```
