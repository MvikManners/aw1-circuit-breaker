from core import create_app, db
from core.models.actors import Warden

def reset_warden_password():
    app = create_app()
    with app.app_context():
        # Replace 'YOUR_WARDEN_ID' with the actual ID (e.g., 'WARDEN-01')
        target_id = 'YOUR_WARDEN_ID' 
        warden = Warden.query.filter_by(warden_id=target_id).first()
        
        if warden:
            # Use 'set_password' as defined in your actors.py
            warden.set_password('NEW_PASSWORD_HERE') 
            db.session.commit()
            print(f"Success: Password updated for Warden {target_id}.")
        else:
            print(f"Error: Warden ID {target_id} not found.")

if __name__ == '__main__':
    reset_warden_password()
