from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# 1. Database & Migrations
# Engine options configured for stable connection pooling
db = SQLAlchemy(engine_options={
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_size": 10,
    "max_overflow": 20
})

# Migration object to manage database schema changes
migrate = Migrate()

# 2. Email Dispatch
# Flask-Mail for handling transactional emails
mail = Mail()

# 3. Authentication & Security
# Flask-Login for user session management
login_manager = LoginManager()
# Flask-WTF CSRF protection for all POST/PUT/DELETE requests
csrf = CSRFProtect()

# Security Configurations
# Specifies the login route and flash message category
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "info"

def init_extensions(app):
    """
    Initialize all extensions with the provided Flask app instance.
    This pattern ensures clean separation and avoids circular imports.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)