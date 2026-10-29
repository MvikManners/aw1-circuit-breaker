from core import create_app
from core.extensions import db
app = create_app()

with app.app_context():
    # 🟢 REMOVE db.drop_all()
    # Use create_all() to add missing tables/columns, but it won't drop existing data.
    db.create_all()
    print("Database synchronization complete.")

if __name__ == '__main__':
    app.run()