from core import create_app, db
from core.models.actors import Warden

def hard_reset():
    app = create_app()
    with app.app_context():
        warden = Warden.query.filter_by(warden_id='WARDEN-01').first()
        if warden:
            warden.set_password('Alpha2026!')
            db.session.commit()
            print("PASSWORD SET TO: Alpha2026!")
        else:
            print("WARDEN-01 NOT FOUND IN DATABASE.")

if __name__ == '__main__':
    hard_reset()
