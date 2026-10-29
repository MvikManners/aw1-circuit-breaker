# core/models/__init__.py
from datetime import datetime
from core.extensions import db

# 1. Fintech & Laveto Pay Models
from .pay_models import (
    Merchant,
    PayLink,
    PaymentTransaction,
    AdCampaign,
    LayawayOrder,
    PlatformLedger,
    Cashier,
    MasterSKU,
    MerchantPriceListing,
    BasketSubOrder, EscrowAuditLog
)

# 2. Vehicle & Forensic Sovereign Models
from .vehicles import (
    SovereignLedger,
    GhostOrder,
    ForensicEvidence,
    CorporateTreasury,
    AccessLog,
    VaultTransaction,
    AuditLog,
    PayrollMandate,
    LiquidationRecord,
    SovereignTransaction
)

# 3. Finance & CRM Models
from .finance import Prospect

# 4. Clean exports for application-wide imports
__all__ = [
    'db',
    'Merchant',
    'PayLink',
    'PaymentTransaction',
    'AdCampaign',
    'LayawayOrder',
    'PlatformLedger',
    'Cashier',
    'MasterSKU',
    'MerchantPriceListing',
    'BasketSubOrder, EscrowAuditLog',
    'SovereignLedger',
    'GhostOrder',
    'ForensicEvidence',
    'CorporateTreasury',
    'AccessLog',
    'VaultTransaction',
    'AuditLog',
    'PayrollMandate',
    'LiquidationRecord',
    'SovereignTransaction',
    'Prospect'
]
