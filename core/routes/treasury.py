from flask import Blueprint, request
from core import db
from core.models.access import AccessLog

treasury_bp = Blueprint('treasury', __name__)

@treasury_bp.route('/pulse')
def process_vault_pulse():
    new_log = AccessLog(action="Vault pulse requested")
    db.session.add(new_log)
    db.session.commit()
    return "Vault pulse active"

# This will now map to /client-vault/<client_id>
@treasury_bp.route('/<string:client_id>', methods=['GET', 'POST'])
def client_vault_detail(client_id):
    if request.method == 'POST':
        pass
    return f"Accessing secure vault for: {client_id}"