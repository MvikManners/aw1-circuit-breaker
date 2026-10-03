from datetime import datetime
from core.extensions import db

# ==========================================
# Pure Financial & System Logic Models
# ==========================================

class PriorityAlert(db.Model):
    __tablename__ = 'priority_alerts'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SystemStability(db.Model):
    __tablename__ = 'system_stability'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    red_soil_mode = db.Column(db.Boolean, default=False)
    last_toggled = db.Column(db.DateTime, default=datetime.utcnow)
    savings_balance = db.Column(db.Float, default=0.0)

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    systemic_crisis_mode = db.Column(db.Boolean, default=False)

class StaggeredPayoutQueue(db.Model):
    __tablename__ = 'staggered_payout_queue'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    total_requested = db.Column(db.Float, nullable=False)
    amount_released = db.Column(db.Float, default=0.0)
    release_stage = db.Column(db.Integer, default=1)
    next_release_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='ACTIVE')

class Treasury(db.Model):
    __tablename__ = 'treasury'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    revenue_balance = db.Column(db.Numeric(12, 2), default=0.00)
    total_lvt_minted = db.Column(db.Numeric(12, 2), default=0.00)
    total_fiat_in_escrow = db.Column(db.Numeric(12, 2), default=0.00)
    last_yield_harvest = db.Column(db.DateTime, nullable=True)

class CorporateTreasury(db.Model):
    __tablename__ = 'corporate_treasury'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False, default="Master Treasury Vault")
    total_saas_tax = db.Column(db.Float, default=0.0)
    total_sanctity_fees = db.Column(db.Float, default=0.0)
    scrap_reclamation_profits = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    class_a_fee = db.Column(db.Float, default=100.0)
    class_a_min = db.Column(db.Float, default=450.0)
    class_b_fee = db.Column(db.Float, default=150.0)
    class_b_min = db.Column(db.Float, default=650.0)
    class_c_fee = db.Column(db.Float, default=200.0)
    class_c_min = db.Column(db.Float, default=1000.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    laveto_operational_float = db.Column(db.Float, default=0.0)

class StopOrderMandate(db.Model):
    __tablename__ = 'stop_order_mandate'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    mandate_code = db.Column(db.String(100), unique=True, nullable=False)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'), nullable=False)
    employer_name = db.Column(db.String(100), default="Government of Botswana")
    department = db.Column(db.String(100), nullable=True)
    employee_number = db.Column(db.String(50), nullable=False)
    omang_number = db.Column(db.String(20), nullable=False)
    monthly_deduction = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='PENDING SIGNATURE')
    date_issued = db.Column(db.DateTime, default=datetime.utcnow)

class SilkRoadQuote(db.Model):
    __tablename__ = 'silk_road_quote'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ghost_order_id = db.Column(db.Integer, db.ForeignKey('ghost_order.id'), nullable=False)
    supplier_name = db.Column(db.String(100))
    price_quoted = db.Column(db.Float)
    eta_days = db.Column(db.Integer)
    raw_reply = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SilkRoadLedger(db.Model):
    __tablename__ = 'silk_road_ledger'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100))
    part_name = db.Column(db.String(100))
    part_number = db.Column(db.String(50))
    price_pula = db.Column(db.Float)
    lead_time_days = db.Column(db.Integer)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)

class FlickerAlert(db.Model):
    __tablename__ = 'flicker_alert'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'))
    gps_location = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='PENDING DISPATCH (24H)')

class Prospect(db.Model):
    __tablename__ = 'prospect'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    status = db.Column(db.String(255), default="PENDING")
    phone_number = db.Column(db.String(20))
    vin_dna = db.Column(db.String(17))
    membership_type = db.Column(db.String(50), default='INDIVIDUAL')
    corporate_cohort = db.Column(db.String(150), nullable=True)
    funding_method = db.Column(db.String(50), nullable=True)
    monthly_pulse = db.Column(db.Float, default=0.0)
    vehicle_class = db.Column(db.String(10), default='B')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    initial_symptom = db.Column(db.String(255), nullable=True)
    rejection_reason = db.Column(db.String(100), nullable=True)
    baseline_trauma = db.Column(db.Text, nullable=True)
    initial_notes = db.Column(db.Text, nullable=True)
    vehicle_year = db.Column(db.Integer, nullable=True)
    vehicle_make = db.Column(db.String(100), nullable=True)
    vehicle_model = db.Column(db.String(100), nullable=True)

class VaultTransaction(db.Model):
    __tablename__ = 'vault_transaction'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(100), nullable=False)
    intent = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, default=0.0)
    network_fee = db.Column(db.Float, default=0.0)
    running_balance = db.Column(db.Float, default=0.0)
    lvt_utility = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    authorized_by = db.Column(db.String(100), default="SYSTEM")
    status = db.Column(db.String(50), default="CLEARED")

class SourcingQueue(db.Model):
    __tablename__ = 'sourcing_queue'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(50), nullable=False)
    component_name = db.Column(db.String(100), nullable=False)
    calculated_wear_km = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='PENDING ADMIN APPROVAL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LvtOrderBook(db.Model):
    __tablename__ = 'lvt_order_book'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'), nullable=False)
    lvt_amount = db.Column(db.Float, nullable=False)
    asking_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='OPEN')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AIQuote(db.Model):
    __tablename__ = 'ai_quote' # Added table name for safety
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100))
    part_details = db.Column(db.String(255))
    price = db.Column(db.Float)
    eta = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class EmailQueue(db.Model):
    __tablename__ = 'email_queue'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120))
    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    status = db.Column(db.String(50), default='QUEUED')