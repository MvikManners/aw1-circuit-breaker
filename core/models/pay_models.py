# core/models/pay_models.py
# Laveto Pay Models: Merchant, PayLink, PaymentTransaction, LayawayOrder, PlatformLedger, AdCampaign, Cashier, MasterSKU, MerchantPriceListing, BasketSubOrder

from datetime import datetime, timezone
from core.extensions import db


def get_naive_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ==========================================
# 🏪 MERCHANTS & STORES MODEL
# ==========================================
class Merchant(db.Model):
    __tablename__ = 'merchants'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    phone_number = db.Column(db.String(32), nullable=True)
    store_pin = db.Column(db.String(64), nullable=True)

    # Financial Routing & Wallets
    settlement_wallet = db.Column(db.String(64), nullable=False, default='72000000')
    settlement_provider = db.Column(db.String(30), default='ORANGE_MONEY')  # ORANGE_MONEY, MYZAKA, SMEGA, CARD
    unsettled_balance = db.Column(db.Numeric(10, 2), default=0.00)
    settled_balance = db.Column(db.Numeric(10, 2), default=0.00)

    # 🛡️ Architecture & Logistics Columns
    business_type = db.Column(db.String(50), default='STANDARD_RETAIL')
    what3words_address = db.Column(db.String(128), default='gaborone.central')
    delivery_fee = db.Column(db.Numeric(10, 2), default=40.00)
    pass_fees_to_customer = db.Column(db.Boolean, default=False)

    # 🛵 Runner Identity & Vehicle Declaration
    runner_photo_url = db.Column(db.String(255), nullable=True)
    vehicle_type = db.Column(db.String(32), default='HATCHBACK')
    vehicle_make_model = db.Column(db.String(64), nullable=True)
    vehicle_plate_number = db.Column(db.String(20), nullable=True)
    vehicle_color = db.Column(db.String(32), nullable=True)
    driver_license_number = db.Column(db.String(32), nullable=True)
    is_runner_verified = db.Column(db.Boolean, default=False)
    is_runner_active = db.Column(db.Boolean, default=False)
    runner_last_active = db.Column(db.DateTime, nullable=True)
    runner_service_area = db.Column(db.String(128), default='Gaborone Central')

    # 🌐 V3 White-Label Custom Domain Mapping
    custom_domain = db.Column(db.String(120), unique=True, nullable=True, index=True)

    # 🛡️ 2-Tier Progressive KYC & Trust Badge
    omang_number = db.Column(db.String(20), nullable=True)
    kyc_document_path = db.Column(db.String(255), nullable=True)
    kyc_status = db.Column(db.String(20), default='UNVERIFIED')  # UNVERIFIED, PENDING, VERIFIED
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)

    # Auth & Security
    pin_hash = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)

    # Float settlement and sweeps
    auto_settle = db.Column(db.Boolean, default=True)
    pending_sweep_amount = db.Column(db.Float, default=0.0)
    pending_sweep_ref = db.Column(db.String(64), nullable=True)

    created_at = db.Column(db.DateTime, default=get_naive_utc)

    # Relationships
    pay_links = db.relationship('PayLink', backref='merchant', lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship(
        'PaymentTransaction',
        backref='merchant_record',
        lazy=True,
        foreign_keys='PaymentTransaction.merchant_id'
    )
    runner_transactions = db.relationship(
        'PaymentTransaction',
        backref='runner_record',
        lazy=True,
        foreign_keys='PaymentTransaction.runner_id'
    )
    layaway_orders = db.relationship('LayawayOrder', backref='merchant', lazy=True)


# ==========================================
# 🛍️ PRODUCTS & PAY LINKS MODEL
# ==========================================
class PayLink(db.Model):
    __tablename__ = 'pay_links'
    __table_args__ = (
        db.UniqueConstraint('merchant_id', 'slug', name='uq_merchant_slug'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    slug = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    is_flexible = db.Column(db.Boolean, default=False)
    stock_quantity = db.Column(db.Integer, default=-1)
    allow_escrow = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_naive_utc)

    # Relationships
    transactions = db.relationship('PaymentTransaction', backref='pay_link', lazy=True)
    layaway_orders = db.relationship('LayawayOrder', backref='pay_link', lazy=True)


# ==========================================
# 💳 PAYMENT TRANSACTIONS MODEL
# ==========================================
class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    runner_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=True)
    pay_link_id = db.Column(db.Integer, db.ForeignKey('pay_links.id'), nullable=True)

    aggregator_ref = db.Column(db.String(64), unique=True, nullable=True, index=True)
    order_ref = db.Column(db.String(64), nullable=True, index=True)
    item_title = db.Column(db.String(180), nullable=True)

    buyer_name = db.Column(db.String(128), nullable=True)
    buyer_phone = db.Column(db.String(32), nullable=True)
    buyer_email = db.Column(db.String(128), nullable=True)

    gross_amount = db.Column(db.Float, default=0.0, nullable=False)
    merchant_share = db.Column(db.Float, default=0.0, nullable=False)
    platform_fee = db.Column(db.Float, default=0.0, nullable=False)
    laveto_fee = db.Column(db.Float, default=0.0)
    is_delivery = db.Column(db.Boolean, default=False)
    delivery_pin = db.Column(db.String(10), nullable=True)
    escrow_release_code = db.Column(db.String(10), nullable=True)
    failed_pin_attempts = db.Column(db.Integer, default=0)
    drive_receipt_url = db.Column(db.String(500), nullable=True)
    is_locked = db.Column(db.Boolean, default=False)
    delivery_fee = db.Column(db.Float, default=0.0, nullable=False)

    delivery_w3w = db.Column(db.String(128), nullable=True)
    courier_name = db.Column(db.String(100), nullable=True)
    tracking_number = db.Column(db.String(100), nullable=True)
    shipment_status = db.Column(db.String(50), default='PENDING')

    payment_method = db.Column(db.String(32), default='ORANGE_MONEY')
    payment_status = db.Column(db.String(32), default='PENDING')

    is_escrow = db.Column(db.Boolean, default=False)
    escrow_status = db.Column(db.String(32), default='NONE')
    escrow_pin = db.Column(db.String(8), nullable=True)

    created_at = db.Column(db.DateTime, default=get_naive_utc)
    updated_at = db.Column(db.DateTime, default=get_naive_utc, onupdate=get_naive_utc)


# ==========================================
# 💎 MOTSHELO LAYAWAY ORDERS MODEL
# ==========================================
class LayawayOrder(db.Model):
    __tablename__ = 'layaway_orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    pay_link_id = db.Column(db.Integer, db.ForeignKey('pay_links.id'), nullable=True)

    buyer_name = db.Column(db.String(128), nullable=True)
    buyer_phone = db.Column(db.String(32), nullable=True)
    item_title = db.Column(db.String(180), nullable=True)

    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    deposit_amount = db.Column(db.Float, default=0.0, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0, nullable=False)

    status = db.Column(db.String(32), default='ACTIVE')  # ACTIVE, COMPLETED, CANCELLED
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=get_naive_utc)
    updated_at = db.Column(db.DateTime, default=get_naive_utc, onupdate=get_naive_utc)


# ==========================================
# 🏛️ PLATFORM LEDGER MODEL
# ==========================================
class PlatformLedger(db.Model):
    __tablename__ = 'platform_ledger'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, nullable=True)
    revenue_type = db.Column(db.String(50), nullable=True, default='TRANSACTION_FEE')
    net_revenue = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=get_naive_utc)

# ==========================================
# 📢 AD CAMPAIGNS MODEL
# ==========================================
class MerchantAdCampaign(db.Model):
    __tablename__ = 'merchant_ad_campaigns'

    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    advertiser_name = db.Column(db.String(128), nullable=False)
    logo_icon = db.Column(db.String(32), default='📢')
    ad_copy_text = db.Column(db.Text, nullable=False)
    target_url = db.Column(db.String(255), nullable=True)
    impressions_count = db.Column(db.Integer, default=0)
    clicks_count = db.Column(db.Integer, default=0)
    budget_total = db.Column(db.Float, default=500.0)
    budget_spent = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_naive_utc)

    merchant = db.relationship('Merchant', backref='ad_campaigns')


# Alias for backward compatibility
AdCampaign = MerchantAdCampaign


# ==========================================
# 👥 MULTI-CASHIER & SHIFT AUDITING MODEL
# ==========================================
class Cashier(db.Model):
    __tablename__ = 'cashiers'

    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    role = db.Column(db.String(32), default='CASHIER')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_naive_utc)

    merchant = db.relationship('Merchant', backref='cashiers')


# ==========================================
# 📦 WHOLESALE CATALOG & SMART BASKET SUB-ORDERS
# ==========================================
class MasterSKU(db.Model):
    __tablename__ = 'master_skus'

    id = db.Column(db.Integer, primary_key=True)
    sku_code = db.Column(db.String(64), unique=True, index=True, nullable=False)
    name = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(80), default="Pantry Staples")
    unit = db.Column(db.String(32), default="pack")

    listings = db.relationship('MerchantPriceListing', backref='master_sku', lazy=True)


class MerchantPriceListing(db.Model):
    __tablename__ = 'merchant_price_listings'

    id = db.Column(db.Integer, primary_key=True)
    master_sku_id = db.Column(db.Integer, db.ForeignKey('master_skus.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    price = db.Column(db.Float, default=0.0, nullable=False)
    in_stock = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=100)
    updated_at = db.Column(db.DateTime, default=get_naive_utc, onupdate=get_naive_utc)

    merchant = db.relationship('Merchant', backref='price_listings')


class BasketSubOrder(db.Model):
    __tablename__ = 'basket_sub_orders'

    id = db.Column(db.Integer, primary_key=True)
    parent_tx_id = db.Column(db.Integer, db.ForeignKey('payment_transactions.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    subtotal_amount = db.Column(db.Float, default=0.0)
    merchant_payout = db.Column(db.Float, default=0.0)
    items_json = db.Column(db.Text, nullable=False)
    fulfillment_status = db.Column(db.String(32), default="PENDING")
    runner_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=get_naive_utc)

    merchant = db.relationship('Merchant', foreign_keys=[merchant_id], backref='sub_orders')
    runner = db.relationship('Merchant', foreign_keys=[runner_id], backref='runner_runs')
    parent_transaction = db.relationship('PaymentTransaction', backref='sub_orders')


class EscrowAuditLog(db.Model):
    __tablename__ = 'escrow_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('payment_transactions.id'), nullable=False, index=True)
    action = db.Column(db.String(32), nullable=False)  # UNLOCK, RELEASE, REFUND
    previous_state = db.Column(db.String(64), nullable=False)
    new_state = db.Column(db.String(64), nullable=False)
    gross_amount = db.Column(db.Float, default=0.0)
    operator_identifier = db.Column(db.String(128), default='MASTER_OPERATOR')
    client_ip = db.Column(db.String(64), nullable=True)
    reason_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_naive_utc, nullable=False, index=True)

    transaction = db.relationship('PaymentTransaction', backref=db.backref('escrow_audit_logs', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'action': self.action,
            'previous_state': self.previous_state,
            'new_state': self.new_state,
            'gross_amount': float(self.gross_amount or 0.0),
            'operator_identifier': self.operator_identifier,
            'client_ip': self.client_ip,
            'reason_notes': self.reason_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
