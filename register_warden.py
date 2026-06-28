from core import create_app, db
from core.models.actors import Warden

def create_warden():
    app = create_app()
    with app.app_context():
        # Check if it exists first
        if not Warden.query.filter_by(warden_id='WARDEN-01').first():
            new_warden = Warden(warden_id='WARDEN-01', name='Forensic Warden')
            new_warden.set_password('Alpha2026!')
            db.session.add(new_warden)
            db.session.commit()
            print("Success: Warden WARDEN-01 created with password 'Alpha2026!'")
        else:
            print("Warden already exists.")

if __name__ == '__main__':
    create_warden()
