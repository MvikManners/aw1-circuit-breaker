from app import app, db
from flask_migrate import Migrate, migrate, upgrade

# Force the configuration explicitly
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'laveto.db')

with app.app_context():
    migrate(message="add rejection_reason to prospect")
    upgrade()
    print("Migration sequence complete.")

# Auto-injected connection pool settings
app.config[SQLALCHEMY_ENGINE_OPTIONS] = {pool_recycle: 280, pool_pre_ping: True}
