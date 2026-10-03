from core import create_app, db
from core.models.vehicles import AccessLog
app = create_app()
with app.app_context():
    db.session.add(AccessLog(vin_dna='SYNC-TEST-001', action='SYSTEM_SYNC_VERIFIED'))
    db.session.commit()
    print('Test entry injected.')
