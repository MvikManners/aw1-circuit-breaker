from sqlalchemy import MetaData
from datetime import datetime
import urllib.parse
import re
from core.extensions import db
from core import db

class PriorityAlert(db.Model):
    __tablename__ = 'priority_alerts'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def whatsapp_link(self):
        clean_number = re.sub(r'[^\d+]', '', self.contact_info)
        vin_tail = self.vin_dna[-4:] if len(self.vin_dna) >= 4 else self.vin_dna
        script = urllib.parse.quote(f"This is the Laveto Architect. I received a Priority Flare for VIN ending in {vin_tail}. Please confirm the vehicle make and model to verify identity.")
        return f"https://wa.me/{clean_number}?text={script}"

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

from datetime import datetime
# Ensure 'db' and 'SovereignLedger' are imported correctly from your application context

class StopOrderMandate(db.Model):
    __tablename__ = 'stop_order_mandate'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Now that you have run the ALTER TABLE command,
    # this field is fully supported by your database table.
    mandate_code = db.Column(db.String(100), unique=True, nullable=False)

    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'), nullable=False)
    employer_name = db.Column(db.String(100), default="Government of Botswana")
    department = db.Column(db.String(100), nullable=True)
    employee_number = db.Column(db.String(50), nullable=False)
    omang_number = db.Column(db.String(20), nullable=False)
    monthly_deduction = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='PENDING SIGNATURE')
    date_issued = db.Column(db.DateTime, default=datetime.utcnow)

    ledger = db.relationship('SovereignLedger', backref=db.backref('stop_order', uselist=False))

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

class SovereignTransaction(db.Model):
    __tablename__ = 'sovereign_transaction'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    balance_after = db.Column(db.Float)
    intent = db.Column(db.String(50))

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
    ghost_order = db.relationship('GhostOrder', backref=db.backref('quotes', lazy=True))

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

class Supplier(db.Model):
    __tablename__ = 'supplier'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    specialty = db.Column(db.String(200))
    portal_url = db.Column(db.String(300))

class SupplierDirectory(db.Model):
    __tablename__ = 'supplier_directory'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    specialty = db.Column(db.String(100))
    portal_url = db.Column(db.String(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class FlickerAlert(db.Model):
    __tablename__ = 'flicker_alert'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('sovereign_ledger.id'))
    gps_location = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='PENDING DISPATCH (24H)')
    ledger = db.relationship('SovereignLedger', backref=db.backref('flicker_alerts', lazy=True, cascade="all, delete-orphan"))

class Prospect(db.Model):
    __tablename__ = 'prospect'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120))

    # 🟢 FIX: Expanded to String(255) to safely hold long statuses and smuggled trauma data
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

    # 🟢 ADDED: Dedicated columns to hold Patient Zero Intel in the waiting room
    baseline_trauma = db.Column(db.Text, nullable=True)
    initial_notes = db.Column(db.Text, nullable=True)

    # 🟢 ADDED: Vehicle details passed from the Intake Form
    vehicle_year = db.Column(db.Integer, nullable=True)
    vehicle_make = db.Column(db.String(100), nullable=True)
    vehicle_model = db.Column(db.String(100), nullable=True)

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
    seller = db.relationship('SovereignLedger', backref=db.backref('market_listings', lazy=True))

class VaultTransaction(db.Model):
    __tablename__ = 'vault_transactions'
    id = db.Column(db.Integer, primary_key=True)
    vin_dna = db.Column(db.String(50))
    intent = db.Column(db.String(255))
    amount = db.Column(db.Float)
    network_fee = db.Column(db.Float)
    lvt_utility = db.Column(db.Float, default=0.0)
    running_balance = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    authorized_by = db.Column(db.String(50))
    status = db.Column(db.String(50))