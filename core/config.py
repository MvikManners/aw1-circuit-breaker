import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Calculate the true base directory (one level up from core/)
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(basedir, '.env')

# ---------------------------------------------------
# 🚨 THE DIAGNOSTIC TRIPWIRE
# ---------------------------------------------------
load_dotenv(env_path)

raw_password = ""
extracted_secret = ""

if not os.path.exists(env_path):
    print(f"🚨 TRIPWIRE TRIGGERED: I cannot find the .env file! Looking at [{env_path}]")
else:
    with open(env_path, 'r') as file:
        for line in file:
            clean_line = line.strip()
            if clean_line.startswith('DB_PASSWORD='):
                raw_password = clean_line.split('=', 1)[1].strip().strip('\'"')
            elif clean_line.startswith('SECRET_KEY='):
                extracted_secret = clean_line.split('=', 1)[1].strip().strip('\'"')

safe_password = quote_plus(raw_password) if raw_password else ""
# ---------------------------------------------------

class Config:
    """The Master Configuration Matrix"""
    
    # Security Keys
    SECRET_KEY = extracted_secret if extracted_secret else 'laveto_absolute_fallback_secret_key_2026_forge'
    
    # 🟢 THE DATABASE WELD (FIXED)
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://LavetoLab:{safe_password}@LavetoLab.mysql.pythonanywhere-services.com/LavetoLab$gospel_os'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gospel Security Protocol
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_TIME_LIMIT = 86400
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # File Systems
    UPLOAD_FOLDER = os.path.join(basedir, 'static')
    
    # Mail Dispatch Engine
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Laveto Admin', os.environ.get('MAIL_USERNAME'))