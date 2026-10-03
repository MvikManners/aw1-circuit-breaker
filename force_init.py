from run import app
from core.extensions import db

# Models from vehicles.py
from core.models.vehicles import (
    SovereignLedger, GhostOrder, AccessLog, ForensicEvidence
)

# Models from finance.py
from core.models.finance import (
    PriorityAlert, SystemStability, SystemSettings, StaggeredPayoutQueue, 
    Treasury, CorporateTreasury, SystemConfig, StopOrderMandate, 
    Transaction, SovereignTransaction, SilkRoadQuote, SilkRoadLedger, 
    Supplier, SupplierDirectory, FlickerAlert, Prospect, 
    SourcingQueue, LvtOrderBook
)

# Models from actors.py
from core.models.actors import User, HubPartner, Warden

with app.app_context():
    print("🔄 Initializing database schema...")
    db.create_all()
    print("✅ Database tables have been synchronized and created.")