# core/config.py
import os
from urllib.parse import quote_plus
from datetime import timedelta
from dotenv import load_dotenv

# Calculate the true base directory (one level up from core/)
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(basedir, '.env')

# Load environment variables cleanly with forced runtime overrides
load_dotenv(env_path, override=True)


class Config:
    """The Master Configuration Matrix (Production Hardened & Fully Integrated)"""

    # ==========================================
    # 🔐 CRYPTOGRAPHIC & SESSION SECURITY
    # ==========================================
    SECRET_KEY = (
        os.environ.get('LAVETO_FLASK_SECRET')
        or os.environ.get('SECRET_KEY')
        or 'laveto_absolute_fallback_secret_key_2026_forge'
    )

    # Production Cookie Hardening (Enforces HTTPS, prevents XSS & CSRF)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    WTF_CSRF_TIME_LIMIT = 86400
    WTF_CSRF_ENABLED = False  # Managed dynamically via gateway & API tokens
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB Max Upload Cap

    # ==========================================
    # 🟢 THE DATABASE WELD (Production MySQL via PyMySQL)
    # ==========================================
    raw_password = os.environ.get('DB_PASSWORD', '')
    safe_password = quote_plus(raw_password) if raw_password else ""

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f'mysql+pymysql://LavetoLab:{safe_password}@LavetoLab.mysql.pythonanywhere-services.com/LavetoLab$gospel_os'
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,          # Verifies connection vitality prior to query execution
        'pool_recycle': 280,            # Recycles connections under PythonAnywhere 300s timeout
        'pool_timeout': 30,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_reset_on_return': 'rollback'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    # ==========================================
    # 📁 FILE SYSTEM, STORAGE & BACKUP PATHS
    # ==========================================
    UPLOAD_FOLDER = os.path.join(basedir, 'static')
    BACKUP_FOLDER = os.path.join(basedir, 'backups')

    # ==========================================
    # 📡 GOSPEL OS & CLOUD STORAGE ANCHORS
    # ==========================================
    GOSPEL_DRIVE_ROOT_ANCHOR = os.environ.get('GOSPEL_DRIVE_ROOT_ANCHOR', '0AO4NRDoHSKuxUk9PVA')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get(
        'GOOGLE_APPLICATION_CREDENTIALS',
        '/home/LavetoLab/google_key.json'
    )

    # ==========================================
    # 🛒 LAVETO PAY & PROJECT LVT FINTECH ENGINE
    # ==========================================
    PLATFORM_FEE_RATE = float(os.environ.get('PLATFORM_FEE_RATE', 0.015))  # 1.5% Platform Cut

    # Webhook HMAC Integrity Secret
    AGGREGATOR_WEBHOOK_SECRET = os.environ.get('AGGREGATOR_WEBHOOK_SECRET', '')

    # WhatsApp Business Cloud API Credentials (Cost-Saving Utility Tier)
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')

    # Africa's Talking SMS Gateway
    AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
    AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY', '')

    # what3words Geolocation Engine
    W3W_API_KEY = os.environ.get('W3W_API_KEY', '')

    # Rate Limiting Engine (Flask-Limiter)
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"

    # ==========================================
    # 📧 DISPATCH ENGINES (MAIL & TELEGRAM)
    # ==========================================
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Laveto Admin', os.environ.get('MAIL_USERNAME'))

    TELEGRAM_TOKEN = os.environ.get(
        'TELEGRAM_TOKEN',
        '8635200479:AAGCIeRa_doRyHVH_tpj5WsKJZJsc-IZAqg'
    )
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '1054436202')