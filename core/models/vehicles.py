from datetime import datetime
from core.extensions import db
from core import db

# ==========================================
# 1. SovereignLedger (The Root)
# ==========================================
class SovereignLedger(db.Model):
    __tablename__ = 'sovereign_ledger'

    id = db.Column(db.Integer, primary_key=True)
    client_pin = db.Column(db.String(6), nullable=True)
    vin_dna = db.Column(db.String(17), unique=True, nullable=False)
    sovereign_key = db.Column(db.String(256), nullable=True)

    # 💰 WARDEN INSPECTION ESTIMATE CAPTURE
    target_repair_cost = db.Column(db.Float, default=0.0)

    member_name = db.Column(db.String(100), nullable=False)
    member_phone = db.Column(db.String(50), nullable=False)
    member_email = db.Column(db.String(120), nullable=True)
    trauma_indicator = db.Column(db.Boolean, default=False)
    baseline_trauma = db.Column(db.String(255), nullable=True)
    initial_notes = db.Column(db.Text, nullable=True)
    base_mileage = db.Column(db.Integer, default=0)
    odometer = db.Column(db.Integer, default=0)
    current_odometer = db.Column(db.Integer, default=0)
    latitude = db.Column(db.String(100), nullable=True)
    longitude = db.Column(db.String(100), nullable=True)
    tread_fl = db.Column(db.Float, default=8.0)
    tread_fr = db.Column(db.Float, default=8.0)
    tread_rl = db.Column(db.Float, default=8.0)
    tread_rr = db.Column(db.Float, default=8.0)
    tire_brand = db.Column(db.String(100), default='UNKNOWN')
    tire_months_remaining = db.Column(db.Integer, default=60)
    tire_health_pct = db.Column(db.Integer, default=100)
    marketplace_image = db.Column(db.String(255), nullable=True)
    marketplace_image_2 = db.Column(db.String(255), nullable=True)
    marketplace_image_3 = db.Column(db.String(255), nullable=True)
    vehicle_class = db.Column(db.String(10), default='B')
    membership_type = db.Column(db.String(50), default='INDIVIDUAL')
    corporate_cohort = db.Column(db.String(150), default='BAY_01_INTAKE')
    funding_method = db.Column(db.String(50), default='EFT')

    # 🏛️ INSTITUTIONAL B2G & B2B ARCHITECTURE
    entity_type = db.Column(db.String(20), default='INDIVIDUAL')  # INDIVIDUAL, GOVERNMENT, ENTERPRISE
    government_ministry = db.Column(db.String(50), nullable=True)  # CTO, HEALTH, AGRICULTURE, etc.
    government_department = db.Column(db.String(100), nullable=True)  # Depot / Station Name
    transport_officer_name = db.Column(db.String(100), nullable=True)  # Authorizing Signatory
    vote_code = db.Column(db.String(100), nullable=True)  # Ministry Account / Vote Code
    company_name = db.Column(db.String(150), nullable=True)  # Enterprise Corporate Name
    company_uin = db.Column(db.String(50), nullable=True)  # Enterprise Tax / UIN Number
    fleet_plant_number = db.Column(db.String(50), nullable=True)  # BX Reg / Fleet Unit No.
    requisition_number = db.Column(db.String(100), nullable=True)  # GPO / CTO Requisition No.
    driver_staff_id = db.Column(db.String(50), nullable=True)  # Driver Staff ID

    # 🔒 Cryptographic Vault Recovery Fields
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # --- FINANCIAL PRECISION FIELDS ---
    monthly_commitment = db.Column(db.Numeric(12, 2), default=0.00)
    current_status = db.Column(db.String(50), default='STABLE')
    admin_status = db.Column(db.String(50), default='ONBOARDING')
    deposit_status = db.Column(db.String(50), default='INACTIVE')
    payroll_authorized = db.Column(db.Boolean, default=False)
    savings_balance = db.Column(db.Numeric(12, 2), default=0.00)
    shield_reservoir = db.Column(db.Numeric(12, 2), default=0.00)
    active_loan_principal = db.Column(db.Numeric(12, 2), default=0.00)
    yield_interest = db.Column(db.Numeric(12, 2), default=0.00)
    yield_principal = db.Column(db.Numeric(12, 2), default=0.00)
    # ----------------------------------

    months_in_green = db.Column(db.Integer, default=0)

    # --- FINANCIAL PRECISION FIELDS ---
    lvt_balance = db.Column(db.Numeric(12, 2), default=0.00)
    lvt_locked_bond = db.Column(db.Numeric(12, 2), default=0.00)
    fiat_high_water_mark = db.Column(db.Numeric(12, 2), default=0.00)
    # ----------------------------------

    # 🚨 PHASE III VERIFICATION COLUMNS
    omang_number = db.Column(db.String(50), nullable=True)
    government_employee_number = db.Column(db.String(50), nullable=True)
    omang_scan_path = db.Column(db.String(255), nullable=True)
    employment_letter_path = db.Column(db.String(255), nullable=True)
    payslip_path = db.Column(db.String(255), nullable=True)
    government_po_path = db.Column(db.String(255), nullable=True)
    fleet_authorization_path = db.Column(db.String(255), nullable=True)

    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    vehicle_year = db.Column(db.Integer, default=2026)
    vehicle_make = db.Column(db.String(100), default='UNKNOWN')
    vehicle_model = db.Column(db.String(100), default='UNKNOWN')

    # Relationships
    ghost_orders = db.relationship('GhostOrder', backref='ledger', lazy='dynamic', cascade="all, delete-orphan")
    mandates = db.relationship('PayrollMandate', back_populates='ledger', lazy='dynamic', cascade="all, delete-orphan")

    # 🚨 EXPLICIT JOIN: Tells SQLAlchemy exactly where to look, ignoring the registry cache
    transactions = db.relationship(
        'SovereignTransaction',
        primaryjoin='SovereignLedger.id == SovereignTransaction.ledger_id',
        back_populates='ledger',
        lazy='dynamic',
        cascade="all, delete-orphan"
    )

    @property
    def status(self):
        return self.current_status

    @status.setter
    def status(self, value):
        self.current_status = value

    @property
    def is_operationally_active(self):
        restricted_statuses = ['MAINTENANCE_DUE', 'SERVICE_REQUIRED', 'LIQUIDATION', 'RETIRED']
        return (
            self.current_status == 'ACTIVE' and
            not self.baseline_trauma and
            self.current_status not in restricted_statuses
        )

    # 🚨 TEMPLATE SHIM: Prevents 'projection is undefined' crashes in ledger.html
    @property
    def projection(self):
        return "N/A"

# ==========================================
# 2. SovereignTransaction
# ==========================================
class SovereignTransaction(db.Model):
    __tablename__ = 'sovereign_transaction'

    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50), default="MAYDAY_BEACON")
    amount = db.Column(db.Float, default=0.0)
    balance_after = db.Column(db.Float, default=0.0)
    intent = db.Column(db.String(255))
    status = db.Column(db.String(50), default="CRITICAL_ALERT")
    pin_hash = db.Column(db.String(256), nullable=True)

    # 🚨 FORCE MAP: Ensures the ORM sees ledger_id even if it's hallucinating
    __mapper_args__ = {
        'properties': {
            'ledger_id': ledger_id
        }
    }

    ledger = db.relationship(
        'SovereignLedger',
        back_populates='transactions'
    )

# ==========================================
# 3. GhostOrder
# ==========================================
class GhostOrder(db.Model):
    __tablename__ = 'ghost_order'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'))
    component_name = db.Column(db.String(255))
    status = db.Column(db.String(100), default='PENDING ORDER')
    category = db.Column(db.String(50), default='MECHANICAL')
    grade = db.Column(db.Integer, default=1)
    oem_part_number = db.Column(db.String(100))
    tier1_brand = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    shipping_routing = db.Column(db.String(100))
    wholesale_cost = db.Column(db.Float, default=0.0)
    estimated_cost = db.Column(db.Float, default=0.0)
    estimated_arrival = db.Column(db.DateTime, nullable=True)
    date_logged = db.Column(db.DateTime, default=db.func.current_timestamp())

# ==========================================
# 4. ForensicEvidence
# ==========================================
class ForensicEvidence(db.Model):
    __tablename__ = 'forensic_evidence'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ghost_order_id = db.Column(db.Integer, db.ForeignKey('ghost_order.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    evidence_type = db.Column(db.String(50), default="INSPECTION_PHOTO")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    technician_note = db.Column(db.Text, nullable=True)

# ==========================================
# 5. CorporateTreasury
# ==========================================
class CorporateTreasury(db.Model):
    __tablename__ = 'corporate_treasury'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    total_saas_tax = db.Column(db.Float, default=0.0)
    total_sanctity_fees = db.Column(db.Float, default=0.0)
    scrap_reclamation_profits = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 6. AccessLog
# ==========================================
class AccessLog(db.Model):
    __tablename__ = 'access_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(17), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 7. VaultTransaction
# ==========================================
class VaultTransaction(db.Model):
    __tablename__ = 'vault_transaction'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(17), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    intent = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    running_balance = db.Column(db.Float, default=0.0)
    authorized_by = db.Column(db.String(50), default='SYSTEM')
    status = db.Column(db.String(20), default='CLEARED')
    lvt_utility = db.Column(db.Float, default=0.0)
    debt_loan = db.Column(db.Float, default=0.0)
    network_fee = db.Column(db.Float, default=0.0)
    labour_funds = db.Column(db.Float, default=0.0)
    parts_ordered = db.Column(db.String(255), default='NONE')

# ==========================================
# 8. AuditLog
# ==========================================
class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    audit_score = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))

# ==========================================
# 9. PayrollMandate
# ==========================================
class PayrollMandate(db.Model):
    __tablename__ = 'payroll_mandate'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'), nullable=False)
    mandate_code = db.Column(db.String(100), unique=True, nullable=True)
    signature_data = db.Column(db.Text, nullable=True)
    ledger = db.relationship(lambda: SovereignLedger, back_populates='mandates', lazy='joined')
    employer = db.Column(db.String(100), default="Government of Botswana")
    department = db.Column(db.String(100), nullable=False)
    omang_number = db.Column(db.String(50), nullable=False)
    employee_number = db.Column(db.String(50), nullable=False)
    monthly_pledge = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

# ==========================================
# 10. LiquidationRecord
# ==========================================
class LiquidationRecord(db.Model):
    __tablename__ = 'liquidation_record'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(100), nullable=False)
    asking_price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='PENDING')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# ==========================================
# 11. SupplierDirectory
# ==========================================
class SupplierDirectory(db.Model):
    __tablename__ = 'supplier_directory'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    specialty = db.Column(db.String(150))
    portal_url = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    sovereign_key = db.Column(db.String(256), nullable=True)
    client_pin = db.Column(db.String(6), nullable=True)

# ==========================================
# 12. RFQDispatchLog
# ==========================================
class RFQDispatchLog(db.Model):
    __tablename__ = 'rfq_dispatch_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    status = db.Column(db.String(20), default='PENDING')
    details = db.Column(db.Text)

# ==========================================
# 13. ComponentGrade
# ==========================================
class ComponentGrade(db.Model):
    __tablename__ = 'component_grades'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    grade_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# ==========================================
# 14. Supplier
# ==========================================
class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    specialty = db.Column(db.String(255), nullable=True)
    portal_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Supplier {self.name}>"

# ==========================================
# 15. Transaction
# ==========================================
class Transaction(db.Model):
    __tablename__ = 'transaction_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'))
    type = db.Column(db.String(100))
    amount = db.Column(db.Float)
    balance_after = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    intent = db.Column(db.String(255))

# ==========================================
# 16. MarketOrder
# ==========================================
class MarketOrder(db.Model):
    __tablename__ = 'market_orders'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'), nullable=False)
    lvt_amount = db.Column(db.Float, nullable=False)
    asking_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, SOLD, CANCELLED
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to the seller
    seller = db.relationship('SovereignLedger', backref=db.backref('market_listings', lazy=True))