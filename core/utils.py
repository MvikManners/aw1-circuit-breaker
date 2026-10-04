from core.models.vehicles import SovereignLedger
from core.models.finance import Prospect
from sqlalchemy import or_

def get_system_counts():
    liq = SovereignLedger.query.filter(
        or_(
            SovereignLedger.current_status.ilike('%SALE%'),
            SovereignLedger.current_status.ilike('%LIQUIDATION%')
        )
    ).count() or 0

    bleeding = SovereignLedger.query.filter(getattr(SovereignLedger, 'health_score', 0) <= 20).count() or 0
    quarantine = Prospect.query.filter_by(status='PENDING').count() or 0

    return {
        "liquidation_requests": liq,
        "bleeding_count": bleeding,
        "quarantine_count": quarantine
    }

import secrets
import string

def generate_human_pin(length=4):
    """Generates a secure numeric human PIN."""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_sovereign_pin(prefix='SOV', length=8):
    """Generates a sovereign vault alphanumeric authorization PIN."""
    chars = string.ascii_uppercase + string.digits
    token = ''.join(secrets.choice(chars) for _ in range(length))
    return f'{prefix}-{token}'
