from datetime import datetime, timezone
import json
import secrets
import bcrypt
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), default="admin", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    
    # English content
    title_en = Column(String(256), nullable=False)
    tagline_en = Column(String(512), nullable=True)
    short_description_en = Column(Text, nullable=True)
    full_description_en = Column(Text, nullable=True)
    genre_en = Column(String(128), nullable=True)
    status_en = Column(String(128), default="In Development", nullable=False)
    
    # Russian content
    title_ru = Column(String(256), nullable=True)
    tagline_ru = Column(String(512), nullable=True)
    short_description_ru = Column(Text, nullable=True)
    full_description_ru = Column(Text, nullable=True)
    genre_ru = Column(String(128), nullable=True)
    status_ru = Column(String(128), default="В разработке", nullable=False)

    # Metadata & Media
    cover_image = Column(String(512), nullable=True)
    hero_image = Column(String(512), nullable=True)
    trailer_url = Column(String(512), nullable=True)
    gallery_images_json = Column(Text, default="[]")  # JSON array of image URLs
    features_json_en = Column(Text, default="[]")     # JSON array of features
    features_json_ru = Column(Text, default="[]")
    platforms = Column(String(256), nullable=True)    # e.g., "PC / Steam"
    release_date_info = Column(String(128), nullable=True)  # Honesty: e.g. "TBA" or verified date
    
    # Control flags
    is_featured = Column(Boolean, default=False, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def get_title(self, lang="en"):
        return self.title_ru if lang == "ru" and self.title_ru else self.title_en

    def get_tagline(self, lang="en"):
        return self.tagline_ru if lang == "ru" and self.tagline_ru else self.tagline_en

    def get_short_description(self, lang="en"):
        return self.short_description_ru if lang == "ru" and self.short_description_ru else self.short_description_en

    def get_full_description(self, lang="en"):
        return self.full_description_ru if lang == "ru" and self.full_description_ru else self.full_description_en

    def get_genre(self, lang="en"):
        return self.genre_ru if lang == "ru" and self.genre_ru else self.genre_en

    def get_status(self, lang="en"):
        return self.status_ru if lang == "ru" and self.status_ru else self.status_en

    def get_status_display(self, lang="en"):
        return self.get_status(lang)

    @property
    def status(self):
        return self.status_en or "development"

    def get_gallery_images(self):
        try:
            return json.loads(self.gallery_images_json or "[]")
        except Exception:
            return []

    def get_features(self, lang="en"):
        try:
            raw = self.features_json_ru if lang == "ru" and self.features_json_ru else self.features_json_en
            res = json.loads(raw or "[]")
            if not res and lang == "ru" and self.features_json_en:
                res = json.loads(self.features_json_en or "[]")
            return res
        except Exception:
            return []


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    
    # English
    title_en = Column(String(256), nullable=False)
    excerpt_en = Column(Text, nullable=True)
    content_en = Column(Text, nullable=False)
    category_en = Column(String(128), default="Announcement")
    
    # Russian
    title_ru = Column(String(256), nullable=True)
    excerpt_ru = Column(Text, nullable=True)
    content_ru = Column(Text, nullable=True)
    category_ru = Column(String(128), default="Анонс")

    cover_image = Column(String(512), nullable=True)
    author = Column(String(128), default="Critical Save Studio")
    reading_time_minutes = Column(Integer, default=3)
    
    is_published = Column(Boolean, default=False, nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def get_title(self, lang="en"):
        return self.title_ru if lang == "ru" and self.title_ru else self.title_en

    def get_excerpt(self, lang="en"):
        return self.excerpt_ru if lang == "ru" and self.excerpt_ru else self.excerpt_en

    def get_content(self, lang="en"):
        return self.content_ru if lang == "ru" and self.content_ru else self.content_en

    def get_category(self, lang="en"):
        return self.category_ru if lang == "ru" and self.category_ru else self.category_en


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)

    title_en = Column(String(256), nullable=False)
    department_en = Column(String(128), nullable=True)
    location_en = Column(String(128), default="Remote / Hybrid")
    description_en = Column(Text, nullable=False)
    requirements_en = Column(Text, nullable=True)  # Markdown or newline-separated
    responsibilities_en = Column(Text, nullable=True)

    title_ru = Column(String(256), nullable=True)
    department_ru = Column(String(128), nullable=True)
    location_ru = Column(String(128), default="Удалённо / Гибрид")
    description_ru = Column(Text, nullable=True)
    requirements_ru = Column(Text, nullable=True)
    responsibilities_ru = Column(Text, nullable=True)

    is_published = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def get_title(self, lang="en"):
        return self.title_ru if lang == "ru" and self.title_ru else self.title_en

    def get_department(self, lang="en"):
        return self.department_ru if lang == "ru" and self.department_ru else self.department_en

    def get_location(self, lang="en"):
        return self.location_ru if lang == "ru" and self.location_ru else self.location_en

    def get_description(self, lang="en"):
        return self.description_ru if lang == "ru" and self.description_ru else self.description_en

    def get_requirements(self, lang="en"):
        return self.requirements_ru if lang == "ru" and self.requirements_ru else self.requirements_en

    def get_responsibilities(self, lang="en"):
        return self.responsibilities_ru if lang == "ru" and self.responsibilities_ru else self.responsibilities_en


class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=False, index=True)
    subject = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    ip_address = Column(String(64), nullable=True)
    status = Column(String(32), default="new")  # new, processed, archived
    email_delivered = Column(Boolean, default=False)
    delivery_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class StudioSetting(Base):
    __tablename__ = "studio_settings"

    key = Column(String(64), primary_key=True)
    value_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    def get_value(self):
        try:
            return json.loads(self.value_json)
        except Exception:
            return self.value_json


class SoftwareProduct(Base):
    __tablename__ = "software_products"

    id = Column(Integer, primary_key=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)

    # Naming & Identity
    title_en = Column(String(256), nullable=False)
    tagline_en = Column(String(512), nullable=True)
    short_description_en = Column(Text, nullable=True)
    full_description_en = Column(Text, nullable=True)

    title_ru = Column(String(256), nullable=True)
    tagline_ru = Column(String(512), nullable=True)
    short_description_ru = Column(Text, nullable=True)
    full_description_ru = Column(Text, nullable=True)

    category = Column(String(128), default="Desktop Application")
    publisher = Column(String(128), default="Critical Save Studio")
    hero_image = Column(String(512), nullable=True)
    features_json_en = Column(Text, default="[]")
    features_json_ru = Column(Text, default="[]")
    system_requirements_en = Column(Text, nullable=True)
    system_requirements_ru = Column(Text, nullable=True)

    is_published = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    releases = relationship("SoftwareRelease", back_populates="product", cascade="all, delete-orphan")

    def get_title(self, lang="en"):
        return self.title_ru if lang == "ru" and self.title_ru else self.title_en

    def get_tagline(self, lang="en"):
        return self.tagline_ru if lang == "ru" and self.tagline_ru else self.tagline_en


class SoftwareRelease(Base):
    __tablename__ = "software_releases"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("software_products.id"), nullable=False, index=True)
    version = Column(String(32), nullable=False)
    release_channel = Column(String(32), default="stable")  # stable, preview, lts

    # Standard Edition metadata
    standard_filename = Column(String(256), nullable=False)
    standard_download_url = Column(String(512), nullable=True)
    standard_size_bytes = Column(Integer, nullable=False, default=0)
    standard_size_display = Column(String(32), nullable=True)
    standard_sha256 = Column(String(64), nullable=False)

    # Offline Air-gapped Edition metadata
    offline_filename = Column(String(256), nullable=False)
    offline_download_url = Column(String(512), nullable=True)
    offline_size_bytes = Column(Integer, nullable=False, default=0)
    offline_size_display = Column(String(32), nullable=True)
    offline_sha256 = Column(String(64), nullable=False)

    # 4-Stage Release Verification Gate
    file_exists_verified = Column(Boolean, default=False, nullable=False)
    hash_verified = Column(Boolean, default=False, nullable=False)
    backend_verified = Column(Boolean, default=False, nullable=False)
    owner_approved = Column(Boolean, default=False, nullable=False)

    approved_by = Column(String(64), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    is_live = Column(Boolean, default=False, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    product = relationship("SoftwareProduct", back_populates="releases")


class PageContent(Base):
    __tablename__ = "page_contents"

    id = Column(Integer, primary_key=True)
    page_key = Column(String(64), unique=True, nullable=False, index=True)  # e.g. "home", "about", "manifesto"
    title_en = Column(String(256), nullable=False)
    title_ru = Column(String(256), nullable=True)

    # Dual-Track Draft vs Published Block Content
    draft_data_json = Column(Text, default="{}")
    published_data_json = Column(Text, default="{}")

    has_unpublished_changes = Column(Boolean, default=False, nullable=False)
    last_edited_by = Column(String(64), nullable=True)
    published_by = Column(String(64), nullable=True)
    published_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def get_draft(self):
        try:
            return json.loads(self.draft_data_json or "{}")
        except Exception:
            return {}

    def get_published(self):
        try:
            return json.loads(self.published_data_json or "{}")
        except Exception:
            return {}


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)  # login, create, edit, publish, rollback, approve_release
    target_type = Column(String(64), nullable=True)
    target_id = Column(String(128), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

