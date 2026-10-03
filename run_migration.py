from app import app, db
from flask_migrate import Migrate, upgrade, migrate

migrate_obj = Migrate(app, db)

with app.app_context():
    migrate(message="add rejection_reason to prospect")
    upgrade()
    print("Migration complete.")