from flask_sqlalchemy import SQLAlchemy

# 1. Primary Database Engine
db = SQLAlchemy(engine_options={'pool_recycle': 280, 'pool_pre_ping': True})


# 2. Authentication & Session Manager
try:
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
except Exception:
    class DummyLoginManager:
        def init_app(self, app): pass
        def user_loader(self, callback): return callback
    login_manager = DummyLoginManager()

# 3. CSRF Protection Engine
try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
except Exception:
    class DummyCSRF:
        def init_app(self, app): pass
        def exempt(self, view): return view
    csrf = DummyCSRF()

# 4. Mail Dispatch Engine
try:
    from flask_mail import Mail
    mail = Mail()
except Exception:
    class DummyMail:
        def init_app(self, app): pass
        def send(self, message): pass
    mail = DummyMail()

# 5. Rate Limiter Engine
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=['200 per day', '50 per hour'],
        storage_uri='memory://'
    )
except Exception:
    class DummyLimiter:
        def init_app(self, app): pass
        def limit(self, *args, **kwargs):
            def decorator(f): return f
            return decorator
    limiter = DummyLimiter()

def init_extensions(app):
    db.init_app(app)
    for ext in [login_manager, csrf, mail, limiter]:
        if hasattr(ext, 'init_app'):
            try:
                ext.init_app(app)
            except Exception:
                pass

__all__ = ['db', 'login_manager', 'csrf', 'mail', 'limiter', 'init_extensions']
