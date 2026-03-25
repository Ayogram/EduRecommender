import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration."""

    # ── Secret Key ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())

    # ── Database ────────────────────────────────────────────────
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "edurecommender.db")

    # ── Session ─────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ── CSRF ────────────────────────────────────────────────────
    WTF_CSRF_ENABLED = True

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    # ── Super Admin & Admin Access ──────────────────────────
    SUPER_ADMIN_EMAIL = 'aajumobi.2202540@stu.cu.edu.ng'
    
    # ── Email Configuration (Flask-Mail) ─────────────────────────
    # Use environment variables for sensitive SMTP credentials
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')

    # ── Uploads ──────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
