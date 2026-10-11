-- Critical Save Studio — Cloudflare D1 Serverless Schema
-- Zero-cost distributed edge database

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'editor',
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME
);

CREATE TABLE IF NOT EXISTS software_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  title_en TEXT NOT NULL,
  title_ru TEXT,
  category TEXT DEFAULT 'Desktop Application',
  publisher TEXT DEFAULT 'Critical Save Studio',
  is_published INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS software_releases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  version TEXT NOT NULL,
  release_channel TEXT DEFAULT 'stable',
  standard_filename TEXT NOT NULL,
  standard_size_display TEXT,
  standard_sha256 TEXT NOT NULL,
  offline_filename TEXT NOT NULL,
  offline_size_display TEXT,
  offline_sha256 TEXT NOT NULL,
  file_exists_verified INTEGER NOT NULL DEFAULT 0,
  hash_verified INTEGER NOT NULL DEFAULT 0,
  backend_verified INTEGER NOT NULL DEFAULT 0,
  owner_approved INTEGER NOT NULL DEFAULT 0,
  is_live INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES software_products(id)
);

CREATE TABLE IF NOT EXISTS page_contents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  page_key TEXT UNIQUE NOT NULL,
  title_en TEXT NOT NULL,
  title_ru TEXT,
  draft_data_json TEXT DEFAULT '{}',
  published_data_json TEXT DEFAULT '{}',
  has_unpublished_changes INTEGER NOT NULL DEFAULT 0,
  last_edited_by TEXT,
  published_by TEXT,
  published_at DATETIME
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT,
  target_id TEXT,
  details TEXT,
  ip_address TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial records
INSERT OR IGNORE INTO software_products (id, slug, title_en, title_ru, category)
VALUES (1, 'financial-war-room', 'Avenor — Personal Finance Intelligence', 'Avenor — Финансовый командный центр', 'Autonomous Intelligence Platform');

INSERT OR IGNORE INTO software_releases (
  id, product_id, version, release_channel,
  standard_filename, standard_size_display, standard_sha256,
  offline_filename, offline_size_display, offline_sha256,
  file_exists_verified, hash_verified, backend_verified, owner_approved, is_live
) VALUES (
  1, 1, '5.0.0', 'stable',
  'Avenor-Setup-5.0.0.exe', '159.0 MB', 'A3CCC0F9D252EB132B5034141540337F6B76CCF085CC0657EEC889005295FC66',
  'Avenor-Offline-Setup-5.0.0.exe', '614.7 MB', 'FC8C6D14588DEC409ECE65A5927867A7698B67332D3470DAAFBCB9DDA113185A',
  1, 1, 1, 1, 1
);
