from datetime import datetime
from core.extensions import db

# 1. SovereignLedger (The Root)
class SovereignLedger(db.Model):
    __tablename__ = 'sovereign_ledger'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(17), unique=True, nullable=False)
    sovereign_key = db.Column(db.String(50), unique=True, nullable=True)

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
    monthly_commitment = db.Column(db.Float, default=0.0)
    current_status = db.Column(db.String(50), default='STABLE')

    savings_balance = db.Column(db.Float, default=0.0)
    shield_reservoir = db.Column(db.Float, default=0.0)
    active_loan_principal = db.Column(db.Float, default=0.0)
    yield_interest = db.Column(db.Float, default=0.0)
    yield_principal = db.Column(db.Float, default=0.0)

    months_in_green = db.Column(db.Integer, default=0)
    lvt_balance = db.Column(db.Float, default=0.0)
    lvt_locked_bond = db.Column(db.Float, default=0.0)
    fiat_high_water_mark = db.Column(db.Float, default=0.0)

    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    vehicle_year = db.Column(db.Integer, default=2026)
    vehicle_make = db.Column(db.String(100), default='UNKNOWN')
    vehicle_model = db.Column(db.String(100), default='UNKNOWN')

    ghost_orders = db.relationship('GhostOrder', backref='ledger', lazy='dynamic', cascade="all, delete-orphan")
    mandates = db.relationship('PayrollMandate', backref='ledger', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def status(self): return self.current_status
    @status.setter
    def status(self, value): self.current_status = value

# 2. GhostOrder
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

# 3. ForensicEvidence
class ForensicEvidence(db.Model):
    __tablename__ = 'forensic_evidence'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ghost_order_id = db.Column(db.Integer, db.ForeignKey('ghost_order.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    evidence_type = db.Column(db.String(50), default="INSPECTION_PHOTO")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    technician_note = db.Column(db.Text, nullable=True)

# 4. CorporateTreasury
class CorporateTreasury(db.Model):
    __tablename__ = 'corporate_treasury'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    total_saas_tax = db.Column(db.Float, default=0.0)
    total_sanctity_fees = db.Column(db.Float, default=0.0)
    scrap_reclamation_profits = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# 5. AccessLog
class AccessLog(db.Model):
    __tablename__ = 'access_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(17), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 6. VaultTransaction
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

# 7. AuditLog
class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    audit_score = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))

# 8. PayrollMandate
class PayrollMandate(db.Model):
    __tablename__ = 'payroll_mandate'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'), nullable=False)
    employer = db.Column(db.String(100), default="Government of Botswana")
    department = db.Column(db.String(100), nullable=False)
    omang_number = db.Column(db.String(50), nullable=False)
    employee_number = db.Column(db.String(50), nullable=False)
    monthly_pledge = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="ACTIVE")
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

# 9. LiquidationRecord
class LiquidationRecord(db.Model):
    __tablename__ = 'liquidation_record'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(100), nullable=False)
    asking_price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='PENDING')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# 10. SupplierDirectory (The Sovereign Rolodex)
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

    def __repr__(self):
        return f'<Supplier {self.name}>'

# 11
class RFQDispatchLog(db.Model):
    __tablename__ = 'rfq_dispatch_log'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('ghost_order.id'), nullable=False)
    supplier_name = db.Column(db.String(150), nullable=False)
    dispatch_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='SENT') # Useful for future 'Awaiting Reply' tracking
    message_content = db.Column(db.Text) # Storing a summary of what was sent

    # Relationship to easily access the order details
    order = db.relationship('GhostOrder', backref='rfq_logs')