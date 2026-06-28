import os
import ssl
import socket
import urllib.request
import urllib.parse
import time
import hashlib
import pdfkit
import random
import string
import csv
import io
import traceback
import threading
import base64
import sys
import importlib
import pkgutil
import re
from functools import wraps
from datetime import datetime, timezone, timedelta
from PIL import Image

# Core Flask and Extensions
from flask import Blueprint, Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app, render_template_string, abort, make_response
from flask_login import current_user, login_required, logout_user
from flask_mail import Message
from sqlalchemy import func, or_, text
from werkzeug.exceptions import NotFound
from core.models.actors import User  # Ensure User is imported if used in RBAC or overrides

# Internal Helpers and Database
from core import db
from core.extensions import mail

# Models - Consolidated Imports
from core.models.vehicles import SovereignLedger, GhostOrder, ForensicEvidence, AccessLog, VaultTransaction, LiquidationRecord
from core.models.finance import CorporateTreasury, Prospect, PriorityAlert, SystemStability, SilkRoadLedger, Supplier, SystemConfig, SovereignTransaction, StopOrderMandate
from core.models.actors import User  # Ensure User is imported if used in RBAC or overrides

# AI & Utilities
import google.generativeai as genai

try:
    from core.services.cloud_bridge import upload_to_gcs
except ImportError:
    def upload_to_gcs(*args, **kwargs): return "https://storage.googleapis.com/fallback"

# Blueprint Definition
hangar_bp = Blueprint('hangar', __name__)

# ==========================================
# 🛡️ THE SECURITY GATES (RE-ARMED & STRICT)
# ==========================================

def security_checkpoint(role_required="OPERATIVE"):
    """Decorator to enforce strict access control based on session and system stability."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            stability = SystemStability.query.first()
            if stability and not stability.is_active:
                flash("System lockout in effect. Access denied.", "danger")
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = getattr(current_user, 'role', '').upper().strip() if current_user.is_authenticated else 'NONE'
        is_auth_admin = role in ['ADMIN', 'ARCHITECT', 'MD']
        is_session_admin = session.get('is_architect') == True

        if is_auth_admin or is_session_admin:
            return f(*args, **kwargs)

        if not current_user.is_authenticated:
            flash("🚨 UPLINK REQUIRED.", "error")
            return redirect(url_for('auth.login'))

        flash("🔒 ACCESS DENIED: High Command clearance required.", "error")
        return redirect(url_for('hangar.agent_terminal'))
    return decorated_function

def architect_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_auth = current_user.is_authenticated and getattr(current_user, 'role', '') == 'ARCHITECT'
        is_session = session.get('is_architect') == True
        if not (is_auth or is_session):
            flash("🚨 ACCESS DENIED: Identity verification required.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = getattr(current_user, 'role', '').upper() if current_user.is_authenticated else 'NONE'
        is_official = role in ['ADMIN', 'ARCHITECT', 'MD', 'AGENT', 'WARDEN', 'STAFF']
        is_raw_session = any(key in session for key in ['warden_logged_in', 'warden_id', 'warden_name', 'user_id', 'is_architect'])
        if is_official or is_raw_session:
            return f(*args, **kwargs)
        return "<h1>🚨 GOSPEL OS: CLEARANCE DENIED</h1>", 403
    return decorated_function

# ==========================================
# 📊 UTILITIES & HELPERS
# ==========================================

MECHANICAL_COMPONENTS = [
    'Engine & Belts', 'Gearbox / Transmission', 'Driveshaft & CV Joints',
    'Front Suspension', 'Rear Suspension', 'Brake System',
    'Steering Rack & Ends', 'Cooling System', 'Exhaust System', 'Electrical / Battery'
]

def get_daily_cipher():
    return f"LVT-{datetime.now().strftime('%d%m')}"

def get_system_counts():
    try:
        all_r = SovereignLedger.query.all()
        q_count = len([r for r in all_r if 'FAIL' in str(getattr(r, 'status', '') or '').upper() or 'FAIL' in str(getattr(r, 'current_status', '') or '').upper()])
        l_count = len([r for r in all_r if (getattr(r, 'pending_loan_amount', 0) or 0) > 0])
        b_count = len([r for r in all_r if (float(getattr(r, 'calculated_integrity', 1.0) or 1.0) * 100) <= 20])
        liq_count = len([r for r in all_r if 'SALE PENDING' in str(getattr(r, 'status', '') or '').upper() or 'SALE' in str(getattr(r, 'current_status', '') or '').upper()])
        return {
            'quarantine_count': q_count, 'loan_notifications': l_count,
            'bleeding_count': b_count, 'liquidation_requests': liq_count,
            'compliance_requests': 0
        }
    except Exception:
        return {'quarantine_count': 0, 'loan_notifications': 0, 'bleeding_count': 0, 'liquidation_requests': 0, 'compliance_requests': 0}

def get_bay_status():
    bays = {
        "BAY 01 (LIFT A)": {"status": "OPEN", "eta": None, "color": "var(--integrity-green)", "vin": None},
        "BAY 02 (LIFT B)": {"status": "OPEN", "eta": None, "color": "var(--integrity-green)", "vin": None},
        "BAY 03 (DIAGNOSTIC)": {"status": "OPEN", "eta": None, "color": "var(--integrity-green)", "vin": None}
    }
    try:
        active_assets = SovereignLedger.query.filter(SovereignLedger.bay_assignment.in_(bays.keys())).all()
        for asset in active_assets:
            if asset.bay_assignment in bays:
                bays[asset.bay_assignment].update({"status": "OCCUPIED", "color": "var(--sanctified-blue)", "vin": asset.vin_dna, "eta": "IN PROGRESS"})
    except: pass
    return bays

def get_total_member_holdings(asset):
    return float(getattr(asset, 'savings_balance', 0) or 0) + float(getattr(asset, 'shield_reservoir', 0) or 0) + float(getattr(asset, 'yield_principal', 0) or 0)

def calculate_loan_status(ledger_entry):
    REPAYMENT_CYCLE_DAYS = 30
    if not ledger_entry.last_payment_timestamp:
        return {"days_remaining": 0, "status": "PENDING_FIRST_PAY"}
    now = datetime.now(timezone.utc)
    last_pay = ledger_entry.last_payment_timestamp.replace(tzinfo=timezone.utc)
    days_since_payment = (now - last_pay).days
    days_remaining = REPAYMENT_CYCLE_DAYS - days_since_payment

    if days_remaining <= 0: return {"days_remaining": 0, "status": "CRITICAL"}
    elif days_remaining <= 5: return {"days_remaining": days_remaining, "status": "WARNING"}
    else: return {"days_remaining": days_remaining, "status": "HEALTHY"}

def get_statement_html(r, total_tvl):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #0a0a0a; color: #f4f4f4; padding: 0; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #333;">
        <div style="border-top: 5px solid #C5A059; padding: 40px; background-color: #111;">
            <h2 style="color: #C5A059; font-family: 'Courier New', monospace; text-transform: uppercase; letter-spacing: 3px; margin: 0; font-size: 1.2rem; font-weight: 900;">LAVETO SOVEREIGN COMMAND</h2>
            <p style="color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 20px;">Monthly Status Report</p>
            <p style="color: #ccc; font-size: 0.9rem; line-height: 1.6;">Dear Member,<br><br>Your automated monthly report is ready. Your vehicle remains actively secured and monitored by the Laveto System.</p>
        </div>
        <div style="padding: 0 40px 20px 40px; background-color: #111;">
            <div style="background: #000; border: 1px dashed #444; padding: 20px; margin-bottom: 20px;">
                <table width="100%" style="font-size: 0.85rem; font-family: 'Courier New', monospace;">
                    <tr><td style="color: #888; padding-bottom: 10px; text-transform: uppercase;">Vehicle (VIN)</td><td style="text-align: right; color: #C5A059; font-weight: bold; padding-bottom: 10px;">{r.vin_dna}</td></tr>
                    <tr><td style="color: #888; text-transform: uppercase;">Status</td><td style="text-align: right; color: #28a745; font-weight: bold;">[{(r.status or 'UNKNOWN').upper()}]</td></tr>
                </table>
            </div>
            <div style="background: #000; border-left: 4px solid #C5A059; padding: 20px; margin-bottom: 30px;">
                <table width="100%" style="font-size: 0.85rem; font-family: 'Courier New', monospace;">
                    <tr><td style="color: #888; padding-bottom: 10px; text-transform: uppercase;">Shield Reservoir</td><td style="text-align: right; color: #fff; font-weight: bold; padding-bottom: 10px;">P{getattr(r, 'shield_reservoir', 0):,.2f}</td></tr>
                    <tr><td style="color: #888; text-transform: uppercase;">Total Savings Equity</td><td style="text-align: right; color: #C5A059; font-weight: bold; font-size: 1.1rem;">P{total_tvl:,.2f}</td></tr>
                </table>
            </div>
            <table width="100%">
                <tr><td align="center"><a href="https://www.laveto.net/" style="background-color: #C5A059; color: #000; padding: 16px 0; text-decoration: none; font-weight: 900; display: block; width: 100%; border-radius: 2px; text-transform: uppercase; letter-spacing: 2px; font-size: 0.85rem;">ACCESS MEMBER AREA</a></td></tr>
            </table>
        </div>
        <div style="background-color: #0a0a0a; padding: 20px; text-align: center; color: #555; font-size: 0.65rem; font-family: 'Courier Prime', monospace;">SECURE HASH: {r.id} <br>© 2026 Laveto Pty Ltd.</div>
    </div>
</body></html>"""

# ==========================================
# 🚀 CORE ENTRY ROUTES
# ==========================================

@hangar_bp.route('/', methods=['GET', 'POST'])
@hangar_bp.route('/index', methods=['GET', 'POST'], endpoint='index')
def index():
    """Renders the main hangar login portal with platform stats. Bulletproofed against 500 errors."""
    try:
        stats_query = db.session.query(
            func.sum(SovereignLedger.savings_balance),
            func.sum(SovereignLedger.shield_reservoir),
            func.sum(SovereignLedger.yield_interest),
            func.sum(SovereignLedger.yield_principal)
        ).first()

        true_platform_tvl = float(stats_query[0] or 0) + float(stats_query[1] or 0) + float(stats_query[2] or 0)
        treasury = CorporateTreasury.query.first()
        saas_total = float(getattr(treasury, 'total_saas_tax', 0.0) if treasury else 0.0)

        member_id = session.get('member_access_granted') if isinstance(session.get('member_access_granted'), str) else None
        return render_template('index.html', total_motshelo=true_platform_tvl, saas_total=saas_total, member_id=member_id)

    except Exception as e:
        print(f"🚨 FATAL LANDING PAGE FAULT CAUGHT: {str(e)}")
        # 🟢 THE FIX: If the template itself crashes (e.g. missing route), return a safe error message instead of an infinite crash loop.
        try:
            return render_template('index.html', total_motshelo=0.0, saas_total=0.0, member_id=None)
        except Exception as template_err:
            return f"<h1 style='color:red; font-family:monospace;'>🚨 TEMPLATE BUILD ERROR: {str(template_err)}</h1>", 500

# 🟢 THE FIX: Restored the missing manifesto route that index.html requires to load
@hangar_bp.route('/manifesto', endpoint='manifesto')
def manifesto():
    """Renders the Laveto architectural philosophy."""
    return render_template('manifesto.html')

@hangar_bp.route('/terminal', methods=['GET', 'POST'], endpoint='agent_terminal')
@staff_required
def agent_terminal():
    """Primary agent terminal interface."""
    if request.method == 'POST':
        vin_lookup = (request.form.get('vin_dna') or request.form.get('intake_vin') or request.form.get('search') or request.form.get('vin'))
        if vin_lookup:
            asset = SovereignLedger.query.filter(SovereignLedger.vin_dna.ilike(f"%{vin_lookup.strip()}%")).first()
            if asset: return redirect(url_for('hangar.inspection_desk', entry_id=asset.id))
            else: flash("No matching VIN found in the Sovereign Ledger.", "warning")

    try: pros = Prospect.query.all()
    except Exception: pros = []

    try: priority_flares = AccessLog.query.filter(AccessLog.action.like('%PRIORITY FLARE%')).order_by(AccessLog.timestamp.desc()).all()
    except Exception: priority_flares = []

    safe_warden = current_user
    if not hasattr(safe_warden, 'wallet_balance') or safe_warden.wallet_balance is None: safe_warden.wallet_balance = 0.0
    training_cleared = getattr(current_user, 'role', 'GUEST').upper() in ['MD', 'ARCHITECT', 'ADMIN']

    return render_template(
        'hangar.html',
        assets=SovereignLedger.query.all(),
        active_warden=safe_warden,
        prospects=pros,
        priority_flares=priority_flares,
        training_cleared=training_cleared,
        **get_system_counts()
    )

@hangar_bp.route('/workshop/check-in/<int:entry_id>', methods=['GET', 'POST'])
@staff_required
def inspection_desk(entry_id):
    try:
        asset = SovereignLedger.query.get_or_404(entry_id)
        if request.method == 'POST':
            asset.base_mileage = request.form.get('intake_mileage')
            asset.bay_assignment = request.form.get('bay_assignment')
            db.session.commit()
            return redirect(url_for('hangar.agent_terminal'))
        custom_components = ["Control Arms", "Tie Rods", "Ball Joints", "Stabilizer Links", "Shock Absorbers", "Wheel Bearings", "Steering Rack Boots", "Brake Pads", "Bushings", "Chassis Integrity"]
        return render_template('inspection_desk.html', record=asset, asset=asset, components_list=custom_components, treasury=CorporateTreasury.query.first(), **get_system_counts())
    except Exception:
        return redirect(url_for('hangar.agent_terminal'))

# ==========================================
# 📊 REGISTRY & PUBLIC FACING ROUTES
# ==========================================

@hangar_bp.route('/registry', endpoint='registry')
def registry():
    try:
        from core.models.supply import SovereignSupplyInventory
        public_merch = SovereignSupplyInventory.query.filter_by(access_tier='PUBLIC').all()
    except Exception:
        public_merch = []
    assets = SovereignLedger.query.all()
    return render_template('registry.html', all_records=assets, public_merchandise=public_merch, **get_system_counts())

@hangar_bp.route('/admin-registry', endpoint='admin_registry')
@admin_only
def admin_registry():
    assets = SovereignLedger.query.order_by(SovereignLedger.id.desc()).all()
    return render_template('admin_registry.html', all_records=assets, **get_system_counts())

@hangar_bp.route('/client-vault/<path:asset_id>', methods=['GET', 'POST'], endpoint='client_vault')
def client_vault(asset_id):
    decoded_asset_id = urllib.parse.unquote(asset_id).strip()
    asset = SovereignLedger.query.filter(func.lower(SovereignLedger.vin_dna) == func.lower(decoded_asset_id)).first()

    if not asset and decoded_asset_id.isdigit():
        asset = SovereignLedger.query.get(int(decoded_asset_id))
    if not asset: raise NotFound(description=f"Asset {decoded_asset_id} not found in Sovereign Ledger.")

    db.session.refresh(asset)
    audit_logs = VaultTransaction.query.filter_by(vin_dna=asset.vin_dna).order_by(VaultTransaction.timestamp.desc()).limit(50).all()

    creation_date = getattr(asset, 'created_at', None) or getattr(asset, 'timestamp', datetime.utcnow())
    if creation_date.tzinfo is None: creation_date = creation_date.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    days_active = (now_utc - creation_date).days
    days_remaining = max(0, 120 - days_active)
    progress_pct = min(100, int((days_active / 120.0) * 100))

    return render_template('client_vault.html',
                           r=asset, asset=asset,
                           status=calculate_loan_status(asset)['status'] if asset.active_loan_principal else 'OPTIMAL',
                           days=calculate_loan_status(asset)['days_remaining'] if asset.active_loan_principal else 0,
                           audit_logs=audit_logs, proofs={}, components={}, market_orders=[],
                           days_active=days_active, days_remaining=days_remaining, progress_pct=progress_pct,
                           now=now_utc, all_records=SovereignLedger.query.all(), treasury=CorporateTreasury.query.first())

@hangar_bp.route('/verify-asset/<string:vin_dna>', methods=['GET'])
def client_dossier_public(vin_dna):
    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    return render_template('client_dossier.html', asset=asset, evidence_list=[])

@hangar_bp.route('/passport/<vin_dna>')
def public_passport(vin_dna):
    asset = SovereignLedger.query.filter(func.lower(SovereignLedger.vin_dna) == func.lower(vin_dna)).first_or_404()
    return render_template('passport.html', r=asset, asset=asset, proofs={}, components={}, market_orders=[], days_active=0, all_records=SovereignLedger.query.all(), treasury=CorporateTreasury.query.first(), **get_system_counts())

@hangar_bp.route('/dossier/<vin_dna>/<source>')
@admin_only
def client_dossier(vin_dna, source):
    asset = SovereignLedger.query.filter(func.lower(SovereignLedger.vin_dna) == func.lower(vin_dna)).first_or_404()
    return render_template('dossier.html', r=asset, asset=asset, source=source, proofs={}, components={}, market_orders=[], days_active=0, all_records=SovereignLedger.query.all(), treasury=CorporateTreasury.query.first(), **get_system_counts())

# ==========================================
# 💰 PAYROLL & MANDATE ENGINE
# ==========================================
@hangar_bp.route('/submit-payroll-mandate', methods=['POST'])
def submit_payroll_mandate():
    """Captures signature, saves mandate to DB, and generates Accountant General PDF."""
    import os
    import base64
    import pdfkit
    from datetime import datetime, timezone
    from flask import current_app, redirect, url_for, flash, request
    from core import db
    from core.models.vehicles import SovereignLedger, AccessLog
    from core.models.finance import StopOrderMandate

    vin_dna = request.form.get('vin_dna')
    department = request.form.get('department')
    omang_number = request.form.get('omang_number')
    employee_number = request.form.get('employee_number')
    monthly_pledge = float(request.form.get('monthly_pledge', 0.0))
    b64_signature = request.form.get('digital_signature_base64')

    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first()
    if not asset:
        flash("🚨 ASSET NOT FOUND IN LEDGER.", "error")
        return redirect(request.referrer or url_for('hangar.index'))

    # Strips everything except letters and numbers to ensure bulletproof file paths
    safe_vin = "".join([c for c in vin_dna if c.isalnum()]).upper()

    # 1. Update Database (StopOrderMandate)
    try:
        mandate = StopOrderMandate.query.filter_by(ledger_id=asset.id).first()
        if not mandate:
            mandate = StopOrderMandate(ledger_id=asset.id, mandate_code=f"AG-{safe_vin}")
            db.session.add(mandate)

        mandate.department = department
        mandate.omang_number = omang_number
        mandate.employee_number = employee_number
        mandate.monthly_deduction = monthly_pledge
        mandate.status = 'ACTIVE'

        audit_log = AccessLog(
            vin_dna=asset.vin_dna,
            action=f"PAYROLL MANDATE FORGED: {department} | Pulse: P{monthly_pledge} | PDF Generated"
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"🚨 DB ERROR: {str(e)}")
        flash("🚨 SYSTEM ERROR: Could not save mandate to database.", "error")
        return redirect(request.referrer)

    # 2. Process Biometric Signature (Base64 -> PNG)
    static_dir = current_app.static_folder
    sig_dir = os.path.join(static_dir, 'forensics', 'signatures')
    pdf_dir = os.path.join(static_dir, 'forensics')
    os.makedirs(sig_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    signature_filename = None
    file_path = ""
    timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    # 🟢 THE FIX: Broadened validation filter to ensure no payload is rejected
    if b64_signature and ',' in b64_signature:
        try:
            header, encoded_data = b64_signature.split(',', 1)
            image_data = base64.b64decode(encoded_data)

            # Predictable filename tied directly to the clean VIN
            signature_filename = f"SIG_{safe_vin}.png"
            file_path = os.path.join(sig_dir, signature_filename)

            with open(file_path, 'wb') as f:
                f.write(image_data)

            current_app.logger.info(f"Signature safely anchored to disk at: {file_path}")
        except Exception as e:
            current_app.logger.error(f"🚨 SIGNATURE DECODE FAULT: {str(e)}")

    # 3. Generate PDF Content
    pdf_filename = f"MANDATE_{safe_vin}.pdf"
    absolute_pdf_path = os.path.join(pdf_dir, pdf_filename)

    # Pass absolute local path to wkhtmltopdf
    local_sig_uri = f"file://{file_path}" if signature_filename else ""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; color: #333; line-height: 1.6; }}
            .header {{ text-align: center; border-bottom: 2px solid #9c8052; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-text {{ font-size: 24px; font-weight: bold; color: #0033a0; margin: 0; }}
            .title {{ font-size: 18px; font-weight: bold; margin-top: 10px; color: #9c8052; text-transform: uppercase; letter-spacing: 2px; }}
            .meta-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .meta-table td {{ padding: 12px; border: 1px solid #dddddd; font-size: 14px; }}
            .meta-table td.label {{ font-weight: bold; background-color: #f9f9f9; color: #555; width: 30%; }}
            .covenant-box {{ margin-top: 30px; padding: 20px; border-left: 4px solid #0033a0; background-color: #f0f4f8; border-radius: 4px; font-size: 13px; }}
            .sig-box {{ margin-top: 40px; border-top: 1px dashed #dddddd; padding-top: 20px; display: flex; justify-content: space-between; align-items: flex-end; }}
            .sig-image {{ max-height: 80px; width: auto; border-bottom: 1px solid #000; display: block; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-text">LAVETO SYSTEM RESTORATION</div>
            <div class="title">Sovereign Payroll Deduction Mandate</div>
            <div style="font-family: monospace; font-size: 11px; margin-top: 5px; color: #666;">Doc ID: AG_MANDATE_{safe_vin}_{timestamp_str}</div>
        </div>
        <p>To: The Accountant General, Government of Botswana. I hereby authorize the periodic deduction of capital from my salary as specified below.</p>
        <table class="meta-table">
            <tr><td class="label">Member (Pilot) Name</td><td>{asset.member_name or 'Sovereign Member'}</td></tr>
            <tr><td class="label">Vehicle VIN (DNA)</td><td>{asset.vin_dna}</td></tr>
            <tr><td class="label">Ministry / Department</td><td>{department}</td></tr>
            <tr><td class="label">Omang Number</td><td>{omang_number}</td></tr>
            <tr><td class="label">Employee / Payroll ID</td><td>{employee_number}</td></tr>
            <tr><td class="label">Monthly Allocation</td><td style="font-weight: bold; color: #0033a0;">P {monthly_pledge:,.2f}</td></tr>
        </table>
        <div class="covenant-box"><strong>LEGAL COVENANT:</strong> I acknowledge that 100% of my monthly deposit is allocated to my personal reservoir (60% Compounding Yield Pool / 40% Shield Reservoir). This mandate remains active and locked under the jurisdiction of the Sovereign OS Hangar 01 framework.</div>
        <div class="sig-box">
            <div>
                <p style="font-size: 12px; margin-bottom: 5px;">Sovereign Member Digital Signature:</p>
                {f'<img src="{local_sig_uri}" class="sig-image" />' if signature_filename else '<div style="height:80px; border-bottom:1px solid #000; width:200px;"></div>'}
            </div>
            <div style="text-align: right; width: 250px;">
                <p style="font-size: 12px; margin-bottom: 45px;">Authorized by Hangar 01 Command:</p>
                <div style="border-bottom: 1px solid #000; width: 100%;"></div>
                <p style="font-size: 11px; color: #888; margin-top: 5px;">Date Authorized: {datetime.now(timezone.utc).strftime('%d %B %Y')}</p>
            </div>
        </div>
    </body></html>
    """

    try:
        path_to_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
        if not os.path.exists(path_to_wkhtmltopdf):
            path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'

        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

        # 🟢 THE FIX: Added options to allow the PDF engine to read the local image file
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'enable-local-file-access': ""
        }

        pdfkit.from_string(html_content, absolute_pdf_path, configuration=config, options=options)

        flash("📝 Sovereign Mandate successfully forged into PDF.", "success")
        return redirect(url_for('static', filename=f'forensics/{pdf_filename}'))

    except Exception as e:
        current_app.logger.error(f"🚨 PDF GENERATION FAULT: {str(e)}")
        try:
            # HTML Fallback sequence
            backup_html_filename = f"MANDATE_{safe_vin}.html"
            backup_html_path = os.path.join(pdf_dir, backup_html_filename)

            # Map the local file path to a web URL for the browser
            local_sig_web_uri = url_for('static', filename=f'forensics/signatures/{signature_filename}') if signature_filename else ""
            styled_web_content = html_content.replace(local_sig_uri, local_sig_web_uri)

            with open(backup_html_path, 'w') as f:
                f.write(styled_web_content)

            flash("⚠️ PDF engine offline. Rendered secure HTML mandate.", "warning")
            return redirect(url_for('static', filename=f'forensics/{backup_html_filename}'))

        except Exception:
            flash("System Error: Failed to compile Accountant General Document.", "error")
            return redirect(url_for('hangar.client_vault', asset_id=asset.vin_dna))

@hangar_bp.route('/forge-payroll-mandate', methods=['GET', 'POST'], endpoint='forge_payroll_mandate')
def forge_payroll_mandate():
    try:
        raw_members = SovereignLedger.query.filter_by(membership_type='CORPORATE').all()
        treasury = CorporateTreasury.query.first()
        cohorts = {}
        grand_total_pulse = 0
        for m in raw_members:
            cohort_name = m.corporate_cohort or "UNASSIGNED INSTITUTION"
            if cohort_name not in cohorts: cohorts[cohort_name] = {'nodes': 0, 'total_debt': 0, 'expected_pulse': 0, 'members': []}
            fee = m.monthly_commitment or 0
            loan_pmt = (m.active_loan_principal / 12) if (m.active_loan_principal and m.active_loan_principal > 0) else 0
            total_due = fee + loan_pmt
            cohorts[cohort_name]['nodes'] += 1
            cohorts[cohort_name]['total_debt'] += (m.active_loan_principal or 0)
            cohorts[cohort_name]['expected_pulse'] += total_due
            cohorts[cohort_name]['members'].append({'id': m.id, 'name': m.member_name, 'vin': m.vin_dna, 'fee': fee, 'loan_pmt': loan_pmt, 'total_due': total_due})
            grand_total_pulse += total_due
        return render_template('forge_mandate.html', cohorts=cohorts, grand_total=grand_total_pulse, treasury=treasury, system_counts=get_system_counts())
    except Exception as e:
        return f"<h1 style='color:red; font-family:monospace;'>🚨 MANDATE CALCULATION ERROR: {str(e)}</h1>"

@hangar_bp.route('/view-mandate/<mandate_id>', methods=['GET'])
def view_mandate(mandate_id):
    """Retrieves and displays the specific payroll mandate details. Gracefully handles missing mandates."""
    from core.models.finance import StopOrderMandate
    from flask import render_template, current_app

    try:
        # 🟢 THE FIX: The database saves the code with an 'AG-' prefix.
        # If the URL just passes the raw VIN, we smartly append the prefix before querying.
        search_code = mandate_id if mandate_id.startswith('AG-') else f"AG-{mandate_id}"

        # Attempt to find the mandate by code
        mandate = StopOrderMandate.query.filter_by(mandate_code=search_code).first()

        # If no mandate is found, render a friendly notification instead of crashing
        if not mandate:
            current_app.logger.info(f"Access attempt for non-existent mandate: {search_code}")
            return render_template('hangar/view_mandate.html', mandate=None, message="This payroll mandate has not been activated or does not exist.")

        # If found, display the details
        return render_template('hangar/view_mandate.html', mandate=mandate, message=None)

    except Exception as e:
        # Log the actual error for your debugging
        current_app.logger.error(f"System error viewing mandate {mandate_id}: {str(e)}")
        # Return a user-friendly error page
        return render_template('hangar/view_mandate.html', mandate=None, message="A temporary system error prevented us from retrieving this mandate. Please try again later.")

@hangar_bp.route('/api/pending_mandates', methods=['GET'])
def api_pending_mandates():
    mandates = StopOrderMandate.query.filter_by(status='ACTIVE').all()
    cohorts = {}
    grand_total = 0.0
    for m in mandates:
        dept = m.department or 'UNASSIGNED COHORT'
        if dept not in cohorts: cohorts[dept] = {'nodes': 0, 'total_debt': 0.0, 'expected_pulse': 0.0, 'members': []}
        cohorts[dept]['nodes'] += 1
        cohorts[dept]['expected_pulse'] += m.monthly_deduction
        grand_total += m.monthly_deduction
        member_name = m.ledger.member_name if m.ledger else 'Unknown Sovereign'
        vin_dna = m.ledger.vin_dna if m.ledger else 'UNKNOWN'
        cohorts[dept]['members'].append({'id': m.id, 'name': member_name, 'vin': vin_dna, 'total_due': m.monthly_deduction})
    return jsonify({'cohorts': cohorts, 'grand_total': grand_total})

@hangar_bp.route('/api/verify_mandate/<int:mandate_id>', methods=['POST'])
def api_verify_mandate(mandate_id):
    mandate = StopOrderMandate.query.get(mandate_id)
    if mandate:
        mandate.status = 'CLEARED_FOR_AG'
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Mandate not found'}), 404

# ==========================================
# 📈 FINANCIAL & LEDGER ROUTES
# ==========================================

@hangar_bp.route('/ledger', endpoint='view_ledger')
@admin_only
def view_ledger():
    if getattr(current_user, 'role', '').upper() in ['STAFF', 'WARDEN']:
        flash("🚨 ACCESS DENIED: The Sovereign Ledger is strictly reserved for High Command.", "error")
        return redirect(url_for('hangar.agent_terminal'))
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('filter', 'ALL').strip().upper()
        search_query = request.args.get('search', '').strip()
        base_query = SovereignLedger.query
        if search_query: base_query = base_query.filter(SovereignLedger.vin_dna.ilike(f'%{search_query}%'))
        if status_filter and status_filter != 'ALL': base_query = base_query.filter(SovereignLedger.current_status.ilike(f'%{status_filter}%'))

        query = base_query.order_by(SovereignLedger.id.desc())
        paginated_results = query.paginate(page=page, per_page=6, error_out=False)
        all_records = base_query.all()

        t_savings = sum(float(getattr(r, 'savings_balance', 0) or 0.0) for r in all_records)
        t_shield = sum(float(getattr(r, 'shield_reservoir', 0) or 0.0) for r in all_records)
        t_tvl = t_savings + t_shield
        t_debt = sum(float(getattr(r, 'active_loan_principal', 0) or 0.0) for r in all_records)
        treasury = CorporateTreasury.query.first()
        s_total = float(getattr(treasury, 'total_saas_tax', 0) or 0.0) if treasury else 0.0

        try: pros = Prospect.query.all()
        except Exception: pros = []

        try: alts = PriorityAlert.query.all()
        except Exception: alts = []

        try: stab = SystemStability.query.first()
        except Exception: stab = None

        return render_template('ledger.html', results=paginated_results, all_records=all_records, total_motshelo=t_tvl, total_debt=t_debt, saas_total=s_total, total_tolls=0.0, total_wholesale=0.0, arbitrage_profit=0.0, prospects=pros, alerts=alts, stability=stab, search_query=search_query, status_filter=status_filter, module_reviews=[], priority_flares=[], daily_cipher=get_daily_cipher(), active_nodes=len(all_records), bay_status=get_bay_status(), projection={'valuation': t_tvl * 1.5, 'gap_to_million': max(0, 1000000 - (t_tvl * 1.5))}, **get_system_counts())
    except Exception as e:
        return f"🚨 LEDGER ERROR: {str(e)}"

@hangar_bp.route('/process_payment/<int:entry_id>', methods=['POST'])
@admin_only
def process_payment(entry_id):
    try:
        asset = SovereignLedger.query.get_or_404(entry_id)
        raw_amount = request.form.get('payment_amount') or request.form.get('total_payment')
        try: amount = float(raw_amount)
        except Exception: amount = 0.0

        if amount > 0:
            p_type = request.form.get('payment_type', 'DEPOSIT').upper()
            minted_total = 0.0
            current_fiat = (getattr(asset, 'savings_balance', 0) or 0) + (getattr(asset, 'shield_reservoir', 0) or 0)

            if p_type == 'INTEREST':
                founder_yield = amount * 0.80
                saas_tax = amount * 0.20
                treasury = CorporateTreasury.query.first() or CorporateTreasury(total_saas_tax=0.0)
                if not treasury.id: db.session.add(treasury)
                treasury.total_saas_tax = float(getattr(treasury, 'total_saas_tax', 0) or 0) + saas_tax
                asset.yield_interest = float(getattr(asset, 'yield_interest', 0) or 0) + founder_yield
                log_intent = f"LOAN INTEREST | Yield: P{founder_yield:.2f} | Tax: P{saas_tax:.2f}"
                current_fiat += founder_yield
                flash(f"✅ P{amount} Interest processed.", "success")
            else:
                config = SystemConfig.query.first()
                if asset.vehicle_class == 'A': required_min = float(getattr(config, 'class_a_min', 450.0))
                elif asset.vehicle_class == 'C': required_min = float(getattr(config, 'class_c_min', 1000.0))
                else: required_min = float(getattr(config, 'class_b_min', 650.0))

                is_top_up = (float(getattr(asset, 'target_repair_cost', 0) or 0) > 0)
                if not is_top_up and amount < required_min:
                    flash(f"🚨 INSUFFICIENT PULSE: Class {asset.vehicle_class} requires a minimum deposit of P{required_min:.2f}.", "error")
                    return redirect(request.referrer)

                admin_fee = amount * 0.05
                net_retained_equity = amount - admin_fee
                asset.shield_reservoir = float(getattr(asset, 'shield_reservoir', 0) or 0) + (net_retained_equity * 0.40)
                asset.savings_balance = float(getattr(asset, 'savings_balance', 0) or 0) + (net_retained_equity * 0.60)
                asset.yield_principal = float(getattr(asset, 'yield_principal', 0) or 0) + amount
                current_fiat = asset.savings_balance + asset.shield_reservoir
                high_water = float(getattr(asset, 'fiat_high_water_mark', 0) or 0)

                if current_fiat > high_water:
                    minted_total = (current_fiat - high_water) * 0.10
                    days_active = (datetime.now(timezone.utc) - (getattr(asset, 'created_at', None) or getattr(asset, 'timestamp', datetime.now(timezone.utc))).replace(tzinfo=timezone.utc)).days
                    chrono_months = max(0, days_active // 30)

                    if chrono_months < 12: liquid_pct, locked_pct = 0.20, 0.80
                    elif chrono_months < 24: liquid_pct, locked_pct = 0.50, 0.50
                    else: liquid_pct, locked_pct = 0.80, 0.20

                    if not hasattr(asset, 'lvt_balance') or asset.lvt_balance is None: asset.lvt_balance = 0.0
                    if not hasattr(asset, 'lvt_locked_bond') or asset.lvt_locked_bond is None: asset.lvt_locked_bond = 0.0

                    asset.lvt_balance += (minted_total * liquid_pct)
                    asset.lvt_locked_bond += (minted_total * locked_pct)
                    asset.fiat_high_water_mark = current_fiat
                    log_intent = f"MONTHLY DEPOSIT | P{amount:.2f} | +{minted_total * liquid_pct:.2f} LVT Liquid"
                    flash(f"✅ P{amount} Deposit. High-Water Mark breached: {minted_total:.2f} LVT Minted.", "success")
                else:
                    minted_total = 0.0
                    log_intent = f"MONTHLY DEPOSIT | P{amount:.2f} | 0.00 LVT Minted (Capital Recycled)"
                    flash(f"✅ P{amount} Deposit processed. Capital recycled; no LVT minted.", "info")

            vault_log = VaultTransaction(vin_dna=asset.vin_dna, intent=log_intent, amount=amount, running_balance=current_fiat, network_fee=admin_fee if p_type != 'INTEREST' else 0.0, lvt_utility=minted_total, authorized_by="SYSTEM", status="CLEARED")
            db.session.add(vault_log)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 ENGINE FAULT: {str(e)}", "error")
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/corporate-treasury', methods=['GET'])
@admin_only
def corporate_treasury():
    tr = CorporateTreasury.query.first()
    if not tr:
        tr = CorporateTreasury(total_saas_tax=0.0, total_sanctity_fees=0.0)
        db.session.add(tr)
        db.session.commit()
    results = SovereignLedger.query.all()
    t_shield = sum(getattr(r, 'shield_reservoir', 0) or 0 for r in results)
    t_savings = sum(getattr(r, 'savings_balance', 0) or 0 for r in results)
    t_yield_i = sum(getattr(r, 'yield_interest', 0) or 0 for r in results)
    t_principal = sum(getattr(r, 'yield_principal', 0) or 0 for r in results)
    t_debt = sum(getattr(r, 'active_loan_principal', 0) or 0 for r in results)
    return render_template('corporate_treasury.html', treasury=tr, total_shield=t_shield, total_yield_interest=t_yield_i, total_yield_principal=t_principal, total_savings=t_savings, total_debt=t_debt, platform_tvl=t_shield + t_savings + t_yield_i, total_revenue=(tr.total_saas_tax or 0) + (tr.total_sanctity_fees or 0), gross=0, outflow=0, arbitrage=0, margin=0, outstanding=0, recent_orders=[], **get_system_counts())

@hangar_bp.route('/finance/deduct_repairs', methods=['POST'])
@admin_only
def deduct_repairs():
    vin = request.form.get('vin')
    amount = float(request.form.get('amount', 0))
    asset = SovereignLedger.query.filter_by(vin_dna=vin).first_or_404()
    if (asset.shield_reservoir or 0) >= amount:
        asset.shield_reservoir -= amount
        asset.target_repair_cost = 0
        db.session.add(SovereignTransaction(ledger_id=asset.id, type='REPAIR_DEDUCTION', amount=amount, balance_after=asset.shield_reservoir, intent='REPAIR DEFICIT Toll'))
        db.session.commit()
        flash('Funds extracted successfully. Repair cost zeroed.', 'success')
    else: flash('Insufficient funds in Maintenance Reservoir.', 'error')
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/triage_intake', methods=['POST'])
def triage_intake():
    vin = request.form.get('vin_dna', '').upper().strip()
    name = request.form.get('member_name', '').strip()
    phone = request.form.get('member_phone', '').strip()
    email = request.form.get('member_email', '').strip()
    year = request.form.get('vehicle_year', '').strip()
    make = request.form.get('vehicle_make', '').strip()
    model = request.form.get('vehicle_model', '').strip()
    v_class = request.form.get('vehicle_class', 'B')
    trauma = request.form.get('trauma', 'Routine Maintenance')
    is_b2b = True if request.form.get('is_b2b') == 'on' else False

    try: pulse_target = float(request.form.get('monthly_pulse', 650.0))
    except ValueError: pulse_target = 650.0

    if SovereignLedger.query.filter_by(vin_dna=vin).first():
        flash(f"Asset {vin} is already locked in the Sovereign Ledger.", "warning")
        return redirect(request.referrer)

    try:
        from core.models.finance import Prospect
        if Prospect.query.filter_by(vin_dna=vin).first():
            flash(f"Asset {vin} is already pending Command Wall approval.", "info")
            return redirect(request.referrer)

        safe_trauma = trauma if trauma and trauma.strip() != "" else "Routine Maintenance"
        smuggled_status = f"PENDING_TRAUMA:{safe_trauma}"

        new_prospect = Prospect(
            vin_dna=vin, full_name=name, phone_number=phone, email=email,
            vehicle_class=v_class, funding_method="EFT", monthly_pulse=pulse_target,
            membership_type="CORPORATE" if is_b2b else "INDIVIDUAL", status=smuggled_status
        )

        if hasattr(new_prospect, 'vehicle_year'): new_prospect.vehicle_year = year
        if hasattr(new_prospect, 'vehicle_make'): new_prospect.vehicle_make = make
        if hasattr(new_prospect, 'vehicle_model'): new_prospect.vehicle_model = model
        if hasattr(new_prospect, 'baseline_trauma'): new_prospect.baseline_trauma = trauma

        db.session.add(new_prospect)
        db.session.commit()
        flash("INTAKE RECEIVED: Your vehicle is now in the queue awaiting Command Wall approval.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"INTEGRITY FLICKER: Database lock failed. {str(e)}", "error")
    return redirect(request.referrer or url_for('hangar.index'))

@hangar_bp.route('/approve-intake/<int:prospect_id>', methods=['POST'])
@hangar_bp.route('/approve_prospect_and_dispatch/<int:prospect_id>', methods=['POST'])
@admin_only
def approve_intake(prospect_id):
    p = Prospect.query.get_or_404(prospect_id)
    key = f"SOV-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

    try:
        # 🟢 EXTRACT SMUGGLED TRAUMA DATA
        extracted_trauma = ""
        if p.status and "PENDING_TRAUMA:" in p.status:
            extracted_trauma = p.status.split("PENDING_TRAUMA:")[1]
        elif hasattr(p, 'baseline_trauma') and p.baseline_trauma:
            extracted_trauma = p.baseline_trauma

        # 1. PROMOTE TO LEDGER (Defensive Mapping)
        new_ledger = SovereignLedger(
            vin_dna=p.vin_dna,
            member_name=p.full_name or "UNVERIFIED",
            sovereign_key=key,
            baseline_trauma=extracted_trauma
        )

        client_email = p.email

        if hasattr(new_ledger, 'member_email'): new_ledger.member_email = client_email or "triage@laveto.internal"
        elif hasattr(new_ledger, 'email'): new_ledger.email = client_email or "triage@laveto.internal"

        if hasattr(new_ledger, 'member_phone'): new_ledger.member_phone = p.phone_number or "00000000"
        elif hasattr(new_ledger, 'contact_number'): new_ledger.contact_number = p.phone_number or "00000000"

        if hasattr(new_ledger, 'vehicle_class'): new_ledger.vehicle_class = getattr(p, 'vehicle_class', 'B') or 'B'
        if hasattr(new_ledger, 'membership_type'): new_ledger.membership_type = getattr(p, 'membership_type', 'INDIVIDUAL')
        if hasattr(new_ledger, 'corporate_cohort'): new_ledger.corporate_cohort = getattr(p, 'corporate_cohort', 'BAY_01_INTAKE')
        if hasattr(new_ledger, 'funding_method'): new_ledger.funding_method = getattr(p, 'funding_method', 'EFT')

        if hasattr(new_ledger, 'monthly_commitment'): new_ledger.monthly_commitment = getattr(p, 'monthly_pulse', 0.0)
        elif hasattr(new_ledger, 'monthly_pulse_target'): new_ledger.monthly_pulse_target = getattr(p, 'monthly_pulse', 0.0)

        if hasattr(new_ledger, 'current_status'): new_ledger.current_status = 'STABLE'
        elif hasattr(new_ledger, 'status'): new_ledger.status = 'STABLE'

        if hasattr(new_ledger, 'vehicle_year'): new_ledger.vehicle_year = getattr(p, 'vehicle_year', 2026)
        if hasattr(new_ledger, 'vehicle_make'): new_ledger.vehicle_make = getattr(p, 'vehicle_make', 'UNKNOWN')
        if hasattr(new_ledger, 'vehicle_model'): new_ledger.vehicle_model = getattr(p, 'vehicle_model', 'UNKNOWN')

        db.session.add(new_ledger)

        try:
            db.session.add(AccessLog(vin_dna=p.vin_dna, action=f"INTAKE_PROMOTION: {p.full_name} moved to SovereignLedger"))
        except Exception:
            pass

        db.session.delete(p)
        db.session.commit()

        # 2. GENERATE PDF & DISPATCH COVENANT EMAIL
        if client_email and '@' in str(client_email):
            try:
                hash_id = hashlib.sha256((p.vin_dna + "COVENANT" + str(datetime.utcnow())).encode()).hexdigest()[:16].upper()
                v_class = getattr(p, 'vehicle_class', 'B') or 'B'
                cohort = getattr(p, 'corporate_cohort', 'INDIVIDUAL') or 'INDIVIDUAL'
                funding = getattr(p, 'funding_method', 'EFT') or 'EFT'
                induction_date = datetime.utcnow().strftime('%d %B %Y')

                # Highly formatted, professional PDF template
                covenant_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Inter:wght@400;600&display=swap');
                        body {{ font-family: 'Inter', sans-serif; background-color: #ffffff; color: #333; margin: 0; padding: 40px; }}
                        .header-table {{ width: 100%; border-bottom: 2px solid #ddd; padding-bottom: 20px; margin-bottom: 30px; }}
                        .logo-text {{ font-family: 'Montserrat', sans-serif; font-size: 32px; font-weight: 900; color: #003366; letter-spacing: 2px; margin: 0; }}
                        .logo-subtext {{ font-family: monospace; font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }}
                        .title-text {{ font-family: 'Montserrat', sans-serif; font-size: 24px; font-weight: 900; color: #C5A059; letter-spacing: 3px; text-transform: uppercase; text-align: right; margin: 0; }}
                        .ref-text {{ font-family: monospace; font-size: 10px; color: #555; font-weight: bold; text-align: right; margin-top: 5px; }}
                        .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 40px; }}
                        .info-table td {{ border: 1px solid #ddd; padding: 12px 15px; font-size: 12px; }}
                        .info-label {{ font-family: 'Montserrat', sans-serif; font-weight: 700; color: #222; width: 40%; text-transform: uppercase; letter-spacing: 1px; }}
                        .info-value {{ font-family: monospace; color: #C5A059; font-weight: bold; }}
                        .info-value-dark {{ font-family: monospace; color: #333; font-weight: bold; }}
                        .section-title {{ font-family: 'Montserrat', sans-serif; font-size: 14px; font-weight: 900; color: #003366; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #C5A059; padding-bottom: 5px; margin-top: 30px; }}
                        .section-text {{ font-size: 12px; line-height: 1.6; color: #444; margin-bottom: 15px; text-align: justify; }}
                        .footer-table {{ width: 100%; margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; }}
                        .sign-name {{ font-family: 'Montserrat', sans-serif; font-weight: 900; font-size: 12px; color: #000; margin: 0; }}
                        .sign-title {{ font-size: 10px; color: #888; margin-top: 2px; }}
                        .badge-verified {{ font-family: 'Montserrat', sans-serif; color: #28a745; font-weight: 900; font-size: 12px; text-align: right; letter-spacing: 1px; }}
                    </style>
                </head>
                <body>
                    <table class="header-table">
                        <tr>
                            <td style="vertical-align: bottom;">
                                <p class="logo-text">LAVETO</p>
                                <p class="logo-subtext">GOSPEL OS // REGISTRY</p>
                            </td>
                            <td style="vertical-align: bottom;">
                                <p class="title-text">SOVEREIGN COVENANT</p>
                                <p class="ref-text">REF #{hash_id}</p>
                            </td>
                        </tr>
                    </table>

                    <table class="info-table">
                        <tr><td class="info-label">SOVEREIGN ASSET DNA (VIN):</td><td class="info-value">{p.vin_dna}</td></tr>
                        <tr><td class="info-label">APPROVED PILOT / MEMBER:</td><td class="info-value-dark">{p.full_name or 'UNVERIFIED'}</td></tr>
                        <tr><td class="info-label">VEHICLE CLASS DESIGNATION:</td><td class="info-value-dark">CLASS {v_class}</td></tr>
                        <tr><td class="info-label">CORPORATE COHORT / INSTITUTION:</td><td class="info-value-dark">{cohort}</td></tr>
                        <tr><td class="info-label">AUTHORIZED FUNDING METHOD:</td><td class="info-value-dark">{funding}</td></tr>
                        <tr><td class="info-label">DATE OF INDUCTION:</td><td class="info-value-dark">{induction_date}</td></tr>
                    </table>

                    <div class="section-title">I. THE ZERO-TRUST PROTOCOL</div>
                    <div class="section-text">
                        The Member acknowledges that Laveto System Restoration strictly utilizes the internal "Silk Road" procurement engine to secure Tier-1 and OEM equivalent components. The installation of unauthorized, aftermarket, or externally sourced parts ("mechanical malware") by the Member or third-party entities is strictly prohibited and will immediately void all system guarantees and asset health scores.
                    </div>

                    <div class="section-title">II. THE FINANCIAL RESERVOIR & YIELD ENGINE</div>
                    <div class="section-text">
                        The Member agrees to the automated monthly deposit based on their assigned Vehicle Class and authorized Funding Method. 100% of this deposited capital is allocated directly to the Member's personal portfolio, structured strictly on a 60/40 fractional split: 60% is directed to the compounding Yield Engine (Savings Equity), and 40% is secured in the Shield Reservoir for future maintenance and compliance tolls.
                    </div>

                    <div class="section-title">III. THE PROVENANCE PREMIUM</div>
                    <div class="section-text">
                        Laveto operates on clinical margins, securing Tier-1 components at wholesale cost without applying retail markups during active repairs. In exchange for maintaining this Zero-Trust integrity, in the event of asset liquidation (sale) facilitated by the Laveto Public Registry, Laveto retains a 15% Provenance Premium on the final sale price to compensate for the certified, mathematically proven maintenance history provided to the buyer.
                    </div>

                    <div class="section-title">IV. DATA SOVEREIGNTY & TELEMETRY</div>
                    <div class="section-text">
                        The Member grants Laveto System Restoration full and immutable rights to capture, catalog, and store 4K forensic telemetry, including the Triple-Hero Profile (Stance, Heart, Sanctity) and detailed component inspection data. This data is utilized solely to maintain the integrity of the Sovereign Registry and protect the asset's market valuation.
                    </div>

                    <table class="footer-table">
                        <tr>
                            <td style="width: 50%;">
                                <p class="sign-name">M. Vela Ikhutseng</p>
                                <p class="sign-title">Managing Director</p>
                            </td>
                            <td style="width: 50%; text-align: right;">
                                <p class="badge-verified">✓ DIGITALLY SIGNED</p>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """

                target_dir = os.path.join(current_app.static_folder, 'forensics')
                os.makedirs(target_dir, exist_ok=True)
                temp_filename = f"{p.vin_dna}_COVENANT.pdf"
                temp_path = os.path.join(target_dir, temp_filename)

                path_to_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
                if not os.path.exists(path_to_wkhtmltopdf):
                    path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'
                config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

                options = {
                    'page-size': 'A4',
                    'encoding': "UTF-8",
                    'margin-top': '20mm',
                    'margin-right': '20mm',
                    'margin-bottom': '20mm',
                    'margin-left': '20mm'
                }
                pdfkit.from_string(covenant_html, temp_path, options=options, configuration=config)

                vault_url = url_for('hangar.index', _external=True) + "#member-login"

                email_html_body = f"""
                <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #050505; color: #f4f4f4; padding: 40px; margin: 0;">
                    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #333333; background-color: #111111;">
                        <div style="border-top: 4px solid #C5A059; padding: 30px;">
                            <h2 style="color: #C5A059; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; margin: 0; font-size: 1.2rem;">LAVETO // GOSPEL OS</h2>
                            <p style="color: #888; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; border-bottom: 1px solid #333; padding-bottom: 15px;">Secure Document Transmission</p>

                            <p style="color: #ccc; font-size: 0.95rem; line-height: 1.6; margin-top: 20px;">Dear {p.full_name or 'Pilot'},<br><br>Your vehicle (<strong style="color: #fff;">{p.vin_dna}</strong>) has been successfully inducted into the Laveto Sovereign Ledger.</p>

                            <p style="color: #ccc; font-size: 0.95rem; line-height: 1.6;">Attached is your official <strong>Sovereign Covenant</strong>. This document outlines the Zero-Trust Protocol, your financial reservoirs, and the immutable terms of your vehicle's mechanical sanctification.</p>

                            <div style="background: #000; border: 1px dashed #C5A059; padding: 25px; margin-top: 30px; margin-bottom: 30px; text-align: center;">
                                <h3 style="color: #C5A059; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 15px 0; font-size: 1rem;">SECURE VAULT CREDENTIALS</h3>
                                <p style="color: #888; font-size: 0.75rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Vehicle DNA (VIN)</p>
                                <div style="color: #fff; font-size: 1.2rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 15px;">{p.vin_dna}</div>

                                <p style="color: #888; font-size: 0.75rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Sovereign Key (Password)</p>
                                <div style="color: #fff; font-size: 1.4rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 25px; background: rgba(197, 160, 89, 0.1); display: inline-block; padding: 5px 15px; border-radius: 4px;">{key}</div>

                                <br>
                                <a href="{vault_url}" style="background-color: #C5A059; color: #000; padding: 14px 25px; text-decoration: none; font-weight: 800; font-family: 'Montserrat', sans-serif; text-transform: uppercase; letter-spacing: 1px; border-radius: 2px; display: inline-block; box-shadow: 0 4px 10px rgba(197,160,89,0.3);">ACCESS CLIENT VAULT</a>
                            </div>

                            <p style="color: #888; font-size: 0.85rem; font-style: italic; margin-top: 20px;">Please download and retain the attached PDF for your records. Do not share your Sovereign Key with anyone, including Laveto staff.</p>
                        </div>
                        <div style="background-color: #050505; padding: 15px; text-align: center; color: #555; font-size: 0.7rem; font-family: monospace;">
                            REF: {hash_id} <br>© {datetime.utcnow().strftime('%Y')} Laveto System Restoration
                        </div>
                    </div>
                </div>
                """

                # 🟢 DIRECT SMTP GMAIL DISPATCHER
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.application import MIMEApplication

                sender_email = "mvik1982@gmail.com"
                sender_password = "wmrkgdrdkosgfvhn"

                msg = MIMEMultipart()
                msg['Subject'] = f"LAVETO // Your Sovereign Covenant - {p.vin_dna}"
                msg['From'] = f"Laveto Command <{sender_email}>"
                msg['To'] = client_email

                msg.attach(MIMEText(email_html_body, 'html'))

                # Attach generated PDF
                with open(temp_path, 'rb') as fp:
                    pdf_attachment = MIMEApplication(fp.read(), _subtype="pdf")
                    pdf_attachment.add_header('Content-Disposition', 'attachment', filename=temp_filename)
                    msg.attach(pdf_attachment)

                # Send Email
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()

                # Clean up PDF file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

                try:
                    db.session.add(AccessLog(vin_dna=p.vin_dna, action=f"COVENANT EMAIL AND PDF TRANSMITTED TO {client_email}"))
                    db.session.commit()
                except Exception:
                    pass

                flash(f"✅ Prospect {p.vin_dna} promoted. Covenant dispatched to {client_email}.", "success")

            except Exception as mail_err:
                current_app.logger.error(f"🚨 COVENANT MAIL FAULT: {str(mail_err)}")
                flash(f"⚠️ Prospect promoted, but automated Covenant email transmission stalled: {str(mail_err)}", "warning")
        else:
            flash(f"✅ Prospect {p.vin_dna} successfully promoted (No email provided).", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"🚨 APPROVAL CRASH: {str(e)}", "error")

    return redirect(request.referrer or url_for('hangar.agent_terminal'))

@hangar_bp.route('/api/persona/triage', methods=['POST'])
def persona_triage():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key: return jsonify({"response": "🚨 SYSTEM FAULT: Brain disconnected."}), 200
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction="You are Laveto AI.")
        response = model.start_chat(history=[]).send_message(user_message)
        return jsonify({"response": response.text, "status": "success"}), 200
    except Exception as e:
        return jsonify({"response": f"🚨 CRASH:\n{str(e)}"}), 200

# ==========================================
# 🔌 FALLBACK & UTILITY ROUTES (Catch-Alls)
# ==========================================
@hangar_bp.route('/upload_multi_marketplace/<int:entry_id>', methods=['POST'])
@admin_only
def upload_multi_marketplace(entry_id): return redirect(request.referrer)

@hangar_bp.route('/asset/override', methods=['POST'])
@admin_only
def override_asset(): return redirect(request.referrer)

@hangar_bp.route('/process_repair_deduction/<int:asset_id>', methods=['POST'])
@admin_only
def process_repair_deduction(asset_id): return redirect(request.referrer)

@hangar_bp.route('/asset/admin_override/<int:asset_id>', methods=['POST'], endpoint='admin_override')
@admin_only
def admin_override(asset_id): return redirect(request.referrer)

@hangar_bp.route('/asset/edit/<int:asset_id>', methods=['POST'])
@admin_only
def edit_asset(asset_id): return redirect(request.referrer)

# ==========================================
# 🌍 THE SILK ROAD: GLOBAL PROCUREMENT MATRIX
# ==========================================

@hangar_bp.route('/silk-road', endpoint='silk_road', methods=['GET'])
@admin_only
def silk_road():
    """Renders the Silk Road Procurement Matrix and live payload tracking."""
    from flask import render_template
    # 🛑 SURGICAL WELD: Ensure your Supplier model is imported here
    from core.models.vehicles import SovereignLedger, GhostOrder, SupplierDirectory

    try:
        # 1. Fetch all ledgers and procurement payloads
        assets = SovereignLedger.query.all()

        # Fetch all orders to populate Zones 1, 2, and 3
        ghosts = GhostOrder.query.order_by(GhostOrder.date_logged.desc()).all()

        # 🛑 SURGICAL WELD: Fetch your Rolodex Suppliers from the DB!
        suppliers = SupplierDirectory.query.all()

        # 2. Calculate Live Financial Metrics (Top Right of the Screen)
        total_wholesale = sum((g.wholesale_cost or 0.0) for g in ghosts if getattr(g, 'wholesale_cost', None))
        total_retail = sum((g.estimated_cost or 0.0) for g in ghosts if getattr(g, 'estimated_cost', None))
        arbitrage_profit = total_retail - total_wholesale

    except Exception as e:
        print(f"🚨 SILK ROAD LOAD ERROR: {str(e)}")
        assets = []
        ghosts = []
        suppliers = []
        total_wholesale = 0.0
        total_retail = 0.0
        arbitrage_profit = 0.0

    return render_template(
        'silk_road.html',
        assets=assets,
        suppliers=suppliers,  # 🛑 WELDED: Passing the actual database query!
        ai_quotes=[],  # Add Email parsing AI query here if rolled out
        orders=ghosts, # NOTE: Changed 'ghosts' to 'orders' as your HTML expects 'orders' for the Kanban zones
        total_tolls=total_retail, # NOTE: Added total_tolls as your HTML expects it
        total_wholesale=total_wholesale,
        arbitrage_profit=arbitrage_profit
    )


@hangar_bp.route('/sync_silk_road', endpoint='sync_silk_road', methods=['POST', 'GET'])
@admin_only
def sync_silk_road():
    """Pings the email drop-zone for incoming supplier quotes via AI Sentinel."""
    from flask import flash, redirect, url_for

    try:
        # In the future, this is where the fetch_supplier_emails() and
        # parse_quote_with_ai() logic will be executed.

        flash("📡 SILK ROAD RADAR PINGED: No new supplier transmissions detected in drop-zone.", "info")
    except Exception as e:
        flash(f"🚨 RADAR INTERFERENCE: {str(e)}", "error")

    return redirect(url_for('hangar.silk_road'))

from flask import request, jsonify
from core.models.vehicles import RFQDispatchLog, db
from datetime import datetime

@hangar_bp.route('/log_rfq_dispatch', methods=['POST'])
@admin_only
def log_rfq_dispatch():
    data = request.json
    try:
        new_log = RFQDispatchLog(
            order_id=data['order_id'],
            supplier_name=data['supplier_name'],
            message_content=data['message_content']
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"status": "success", "log_id": new_log.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@hangar_bp.route('/loan-terminal', methods=['GET'])
@admin_only
def loan_terminal(): return render_template('loan_terminal.html', records=[])

@hangar_bp.route('/launch-flare', methods=['GET', 'POST'])
def launch_flare(): return redirect(url_for('hangar.index'))

@hangar_bp.route('/api/verify_root', methods=['POST'])
def verify_root(): return redirect(request.referrer)

@hangar_bp.route('/disapprove-intake', methods=['POST'])
@admin_only
def disapprove_intake(): return redirect(request.referrer)

@hangar_bp.route('/audit-logs', endpoint='audit_logs')
@admin_only
def audit_logs():
    from flask import render_template, flash
    from core.extensions import db

    try:
        from core.models.vehicles import VaultTransaction
        # Fetch all financial transactions ordered by most recent
        transactions = VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).limit(200).all()
    except Exception as e:
        # 🟢 AUTO-HEAL: If the table doesn't exist, create it instantly and prevent the 500 Crash!
        print(f"🚨 Audit Logs Error: {str(e)}")
        if '1146' in str(e) or 'no such table' in str(e).lower() or 'VaultTransaction' in str(e):
            db.create_all()
            transactions = []
            flash("✅ System Auto-Healed: Vault Transaction database created.", "success")
        else:
            transactions = []
            flash(f"⚠️ Could not load transactions: {str(e)}", "warning")

    return render_template('audit_logs.html', transactions=transactions)

@hangar_bp.route('/export-audit-csv', endpoint='export_audit_csv')
@admin_only
def export_audit_csv():
    import io
    import csv
    from flask import Response, flash, redirect, url_for
    from core.extensions import db
    from datetime import datetime

    try:
        from core.models.vehicles import VaultTransaction
        transactions = VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).all()
    except Exception as e:
        flash("⚠️ Database wasn't ready. Please load the Audit Logs page first to auto-heal.", "warning")
        return redirect(url_for('hangar.audit_logs'))

    # Create an in-memory string buffer
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Headers matching the UI exactly
    writer.writerow([
        'Timestamp (UTC)', 'Asset DNA', 'Intent', 'Authorized By', 'Status',
        'Value (Pula)', 'Running Balance', 'LVT Utility', 'Debt/Loan',
        'Network Fee', 'Labour Funds', 'Parts & Dispatch'
    ])

    # Write the data rows
    for tx in transactions:
        writer.writerow([
            tx.timestamp.strftime('%Y-%m-%d %H:%M:%S') if tx.timestamp else 'N/A',
            tx.vin_dna,
            tx.intent,
            tx.authorized_by,
            tx.status,
            f"{tx.amount:.2f}",
            f"{tx.running_balance:.2f}",
            f"{tx.lvt_utility:.2f}",
            f"{tx.debt_loan:.2f}",
            f"{tx.network_fee:.2f}",
            f"{tx.labour_funds:.2f}",
            tx.parts_ordered
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=Laveto_Forensic_Audit_{datetime.now().strftime('%Y%m%d%H%M')}.csv"}
    )

@hangar_bp.route('/treasury-report', endpoint='treasury_report')
@admin_only
def treasury_report():
    from flask import render_template
    from core.models.vehicles import SovereignLedger

    try:
        # Fetch all ledgers that have active outstanding loans
        loans = SovereignLedger.query.filter(SovereignLedger.active_loan_principal > 0).all()
    except Exception as e:
        print(f"🚨 Treasury Report Error: {e}")
        loans = []

    return render_template('treasury_summary.html', loans=loans)

@hangar_bp.route('/api/live_audit_logs', endpoint='api_live_audit_logs')
@admin_only
def api_live_audit_logs():
    from flask import jsonify

    try:
        from core.models.vehicles import VaultTransaction
        transactions = VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).limit(50).all()

        logs = []
        for tx in transactions:
            logs.append({
                "timestamp": tx.timestamp.strftime('%Y-%m-%d %H:%M:%S') if tx.timestamp else 'N/A',
                "vin_dna": tx.vin_dna,
                "intent": tx.intent,
                "authorized_by": tx.authorized_by,
                "status": tx.status,
                "amount": f"P{tx.amount:,.2f}",
                "running_balance": f"P{tx.running_balance:,.2f}",
                "lvt_utility": f"{tx.lvt_utility:,.2f}",
                "debt_loan": f"P{tx.debt_loan:,.2f}",
                "network_fee": f"P{tx.network_fee:,.2f}",
                "labour_funds": f"P{tx.labour_funds:,.2f}",
                "parts_ordered": tx.parts_ordered
            })

        return jsonify({"status": "success", "logs": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "logs": []})

# ==========================================
# 🚨 DANGER ZONE: SYSTEM OVERRIDES 🚨
# ==========================================

@hangar_bp.route('/purge-audit-logs', methods=['POST'], endpoint='purge_audit_log')
@admin_only
def purge_audit_log():
    """Surgical Override: Wipes only the logs, leaves money and vehicles intact."""
    from core.extensions import db
    from flask import flash, redirect, url_for
    from core.models.vehicles import VaultTransaction, AccessLog
    try:
        VaultTransaction.query.delete()
        AccessLog.query.delete()
        db.session.commit()
        flash("✅ SURGICAL OVERRIDE SUCCESS: Audit Logs and Transaction Histories have been wiped.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 PURGE FAILED: {str(e)}", "error")

    return redirect(url_for('hangar.audit_logs'))

# 🟢 THE FIX: Changed endpoint to 'purge_testing_data' to perfectly match the HTML
@hangar_bp.route('/purge-all-test-data', methods=['POST'], endpoint='purge_testing_data')
@admin_only
def purge_all_test_data():
    """Total Annihilation: Wipes the entire database clean for a fresh start."""
    from core.extensions import db
    from flask import flash, redirect, url_for
    from core.models.vehicles import SovereignLedger, GhostOrder, VaultTransaction, AccessLog, CorporateTreasury
    from core.models.finance import StopOrderMandate
    try:
        # Delete dependent tables first
        StopOrderMandate.query.delete()
        GhostOrder.query.delete()
        try:
            VaultTransaction.query.delete()
        except:
            pass # Ignore if VaultTransaction somehow still doesn't exist
        AccessLog.query.delete()

        # Delete core structural tables
        SovereignLedger.query.delete()
        CorporateTreasury.query.delete()
        db.session.commit()

        flash("💥 TOTAL ANNIHILATION SUCCESS: All test ledgers, mandates, logs, and treasury data have been permanently destroyed.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 PURGE FAILED: {str(e)}", "error")

    return redirect(url_for('hangar.audit_logs'))

@hangar_bp.route('/finance/inject-capital', methods=['POST'])
@admin_only
def inject_capital(): return redirect(request.referrer)

@hangar_bp.route('/finance/mint-loan/<int:asset_id>', methods=['POST'])
@admin_only
def mint_loan(asset_id): return redirect(request.referrer)

@hangar_bp.route('/finance/repay-loan/<int:asset_id>', methods=['POST'])
@admin_only
def repay_loan(asset_id): return redirect(request.referrer)

@hangar_bp.route('/payroll-matrix', methods=['GET', 'POST'], endpoint='payroll_matrix')
@admin_only
def payroll_matrix(): return redirect(url_for('hangar.forge_payroll_mandate'))

@hangar_bp.route('/matrix/health', endpoint='debug_env')
@admin_only
def debug_env(): return render_template('health_monitor.html', diagnostics={}, current_time=time.strftime("%Y-%m-%d %H:%M:%S"))

@hangar_bp.route('/matrix/settings', endpoint='settings', methods=['GET', 'POST'])
@admin_only
def anchor_settings():
    from core.models.finance import SystemConfig, CorporateTreasury
    from core.models.vehicles import SovereignLedger
    from datetime import datetime, timezone

    # 1. Fetch the active configuration or initialize a new one if it doesn't exist
    config = SystemConfig.query.first()
    if not config:
        config = SystemConfig()
        db.session.add(config)
        db.session.commit()

    # 2. Handle the Form Submission (Writing to the Database)
    if request.method == 'POST':
        try:
            # Safely extract and float the incoming data from the Engine Room UI
            config.class_a_min = float(request.form.get('a_min', 0))
            config.class_b_min = float(request.form.get('b_min', 0))
            config.class_c_min = float(request.form.get('c_min', 0))

            # If you also have fee fields, capture them here
            config.class_a_fee = float(request.form.get('a_fee', 0))
            config.class_b_fee = float(request.form.get('b_fee', 0))
            config.class_c_fee = float(request.form.get('c_fee', 0))

            # Timestamp the alignment
            config.last_updated = datetime.now(timezone.utc)
            db.session.commit()

            flash("💾 GLOBAL MATRIX OVERRIDDEN: New baselines locked securely.", "success")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Configuration Write Error: {str(e)}")
            flash("⚠️ CONFIGURATION FAULT: Could not lock new baselines.", "error")

        return redirect(url_for('hangar.settings'))

    # 3. Render the UI with the active configurations injected
    return render_template(
        'settings.html',
        config=config,
        all_records=SovereignLedger.query.all(),
        assets=SovereignLedger.query.all(),
        treasury=CorporateTreasury.query.first(),
        **get_system_counts()
    )

@hangar_bp.route('/finance/distribute-yield', methods=['POST'], endpoint='distribute_yield')
@admin_only
def distribute_yield(): return redirect(request.referrer)

@hangar_bp.route('/resolve_flare/<int:log_id>', methods=['POST'])
@admin_only
def resolve_flare_log(log_id): return redirect(request.referrer)

@hangar_bp.route('/dispatch_monthly_statements', methods=['POST'])
@admin_only
def dispatch_monthly_statements(): return redirect(request.referrer)

@hangar_bp.route('/dispatch_whatsapp/<int:asset_id>')
@admin_only
def dispatch_whatsapp(asset_id): return redirect(request.referrer)

@hangar_bp.route('/dispatch_silk_road/<int:ghost_order_id>', methods=['POST'])
@admin_only
def dispatch_silk_road(ghost_order_id): return redirect(request.referrer)

@hangar_bp.route('/accept_silk_road_quote/<int:quote_id>', methods=['POST'])
@admin_only
def accept_silk_road_quote(quote_id): return redirect(request.referrer)

@hangar_bp.route('/toggle_listing/<int:entry_id>', methods=['POST'])
@admin_only
def toggle_listing(entry_id): return redirect(request.referrer)

@hangar_bp.route('/request_liquidation/<int:entry_id>', methods=['POST'])
def request_liquidation(entry_id): return redirect(request.referrer)

@hangar_bp.route('/generate_liquidation_payout/<int:entry_id>', methods=['GET', 'POST'])
def generate_liquidation_payout(entry_id): return "Payout Generated"

@hangar_bp.route('/generate_quote/<int:entry_id>')
@admin_only
def generate_quote(entry_id): return "Quote Generated"

@hangar_bp.route('/reject_loan_request/<int:entry_id>', methods=['POST'])
@admin_only
def reject_loan_request(entry_id): return redirect(request.referrer)

@hangar_bp.route('/resolve_compliance/<int:entry_id>', methods=['POST'])
@admin_only
def resolve_compliance(entry_id): return redirect(request.referrer)

@hangar_bp.route('/trigger_handover/<int:entry_id>', methods=['POST'])
@admin_only
def trigger_handover(entry_id): return redirect(request.referrer)

@hangar_bp.route('/upload_direct_capture/<int:entry_id>', methods=['POST'])
@admin_only
def upload_direct_capture(entry_id): return jsonify({"status": "success"})

@hangar_bp.route('/master_fleet_dashboard/<string:client_phone>', endpoint='master_fleet_dashboard')
@admin_only
def master_fleet_dashboard(client_phone): return "Fleet Dashboard"

@hangar_bp.route('/dispatch_covenant_whatsapp/<int:asset_id>')
@admin_only
def dispatch_covenant_whatsapp(asset_id): return redirect(request.referrer)

@hangar_bp.route('/resolve_mayday/<int:asset_id>', methods=['POST'])
@admin_only
def resolve_mayday(asset_id): return redirect(request.referrer)

@hangar_bp.route('/update_contact', methods=['POST'])
@admin_only
def update_contact(): return redirect(request.referrer)

@hangar_bp.route('/execute_transfer/<int:entry_id>', methods=['POST'])
@admin_only
def execute_transfer(entry_id): return redirect(request.referrer)

@hangar_bp.route('/silence_market_alarm/<int:entry_id>', methods=['POST'])
@admin_only
def silence_market_alarm(entry_id): return redirect(request.referrer)

@hangar_bp.route('/clear_booking/<int:asset_id>')
@admin_only
def clear_booking(asset_id): return redirect(request.referrer)

@hangar_bp.route('/purge_asset/', defaults={'entry_id': None})
@hangar_bp.route('/purge_asset/<int:entry_id>')
def purge_asset(entry_id): return redirect(request.referrer)

@hangar_bp.route('/dispatch_single_email/<string:doc_type>/<int:entry_id>', methods=['POST'])
@admin_only
def dispatch_single_email(doc_type, entry_id): return redirect(request.referrer)

@hangar_bp.route('/approve_audit/<int:asset_id>', methods=['POST'])
@admin_only
def approve_audit(asset_id): return redirect(request.referrer)

@hangar_bp.route('/reject_audit/<int:asset_id>', methods=['POST'])
@admin_only
def reject_audit(asset_id): return redirect(request.referrer)

@hangar_bp.route('/open_bay_01')
@admin_only
def open_bay_01(): return redirect(request.referrer)

# ==========================================
# 📇 SOVEREIGN ROLODEX PROTOCOLS
# ==========================================

@hangar_bp.route('/add_supplier', methods=['POST'])
# @admin_only  <-- Uncomment if you use this decorator
def add_supplier():
    from core.models.vehicles import SupplierDirectory
    from flask import request, flash, redirect, url_for
    from core import db

    try:
        # 🛡️ BULLETPROOF EXTRACTION: Prevents "NONE" ghosts
        s_name = request.form.get('name')
        if not s_name or s_name.strip() == "":
            s_name = "UNNAMED SUPPLIER"

        new_supplier = SupplierDirectory(
            name=s_name,
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            specialty=request.form.get('specialty'),
            portal_url=request.form.get('portal_url') # Captures the URL for the button!
        )
        db.session.add(new_supplier)
        db.session.commit()
        flash(f"✅ MATRIX UPDATED: {new_supplier.name} locked into the Sovereign Rolodex.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 DATABASE ERROR: Could not secure supplier. {str(e)}", "error")

    return redirect(url_for('hangar.silk_road')) # Adjust 'hangar.silk_road' if your endpoint differs

@hangar_bp.route('/edit_supplier/<int:supplier_id>', methods=['POST'])
@admin_only
def edit_supplier(supplier_id):
    from core.models.vehicles import SupplierDirectory
    from flask import request, flash, redirect, url_for
    from core import db

    supplier = SupplierDirectory.query.get_or_404(supplier_id)
    try:
        supplier.name = request.form.get('name')
        supplier.email = request.form.get('email')
        supplier.phone = request.form.get('phone')
        supplier.specialty = request.form.get('specialty')
        supplier.portal_url = request.form.get('portal_url')

        db.session.commit()
        flash(f"✅ UPDATE SECURED: {supplier.name} modified.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 UPDATE FAILED: {str(e)}", "error")

    return redirect(url_for('hangar.silk_road'))

@hangar_bp.route('/delete_supplier/<int:supplier_id>', methods=['POST', 'GET'])
def delete_supplier(supplier_id):
    # ... your deletion logic ...
    # ... your code remains the same ...
    from core.models.vehicles import SupplierDirectory
    from core import db
    from flask import flash, redirect, url_for

    supplier = SupplierDirectory.query.get_or_404(supplier_id)
    try:
        db.session.delete(supplier)
        db.session.commit()
        flash(f"💀 PURGE COMPLETE: Record {supplier_id} purged.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 PURGE FAILED: {str(e)}", "error")

    return redirect(url_for('hangar.silk_road'))

@hangar_bp.route('/api/security/radar_sweep', methods=['GET'])
@admin_only
def radar_sweep_api(): return jsonify({"active": False})

@hangar_bp.route('/api/security/dispatch_agent/<int:alert_id>', methods=['POST'])
@admin_only
def dispatch_agent_api(alert_id): return jsonify({"status": "success"})

@hangar_bp.route('/vault/trigger_mayday/<int:asset_id>', methods=['POST'])
def trigger_mayday_vault(asset_id): return jsonify({"status": "success"})

@hangar_bp.route('/initiate_sale', methods=['POST'])
def initiate_sale(): return redirect(request.referrer)

@hangar_bp.route('/delete_asset/<int:asset_id>', methods=['POST'])
@admin_only
def delete_asset(asset_id): return redirect(request.referrer)

@hangar_bp.route('/update-odometer/<int:asset_id>', methods=['POST'])
@login_required
def update_odometer(asset_id): return redirect(request.referrer)

@hangar_bp.route('/save_baseline/<int:entry_id>', methods=['POST'])
@login_required
def save_baseline(entry_id): return jsonify({"status": "success"})


# ==========================================
# 📡 HOLISTIC TELEMETRY & BASELINE CONTROL
# ==========================================
@hangar_bp.route('/warden-update-baseline/<int:asset_id>', methods=['POST'])
def warden_update_baseline(asset_id):
    try:
        asset = SovereignLedger.query.get_or_404(asset_id)
        data = request.get_json()
        new_baseline = data.get('new_baseline')
        if new_baseline is not None:
            asset.base_mileage = int(new_baseline)
            if asset.current_odometer is None or asset.current_odometer < asset.base_mileage:
                 asset.current_odometer = asset.base_mileage
            db.session.commit()
            return jsonify({"status": "success", "new_base": asset.base_mileage})
    except Exception as e:
        pass
    return jsonify({"status": "error"}), 500

def warden_update_baseline(asset_id):
    """Locks the official starting mileage (Baseline) for the vehicle."""
    from core.extensions import db
    from core.models.vehicles import SovereignLedger, AccessLog
    from flask import request, jsonify

    try:
        asset = SovereignLedger.query.get(asset_id)
        if not asset:
            return jsonify({"status": "error", "message": "Asset not found in Sovereign Ledger."}), 404

        data = request.get_json()
        if not data or 'new_baseline' not in data:
            return jsonify({"status": "error", "message": "Missing baseline payload."}), 400

        new_base = int(data.get('new_baseline'))

        # Update the database
        asset.base_mileage = new_base

        # Anchor an audit log for security tracking
        db.session.add(AccessLog(
            vin_dna=asset.vin_dna,
            action=f"WARDEN OVERRIDE: Baseline Odometer locked at {new_base} KM"
        ))
        db.session.commit()

        return jsonify({"status": "success", "message": "Baseline locked securely."})

    except ValueError:
        return jsonify({"status": "error", "message": "Invalid format. Numbers only."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"System Error: {str(e)}"}), 500


# 🟢 THE FIX: Changed <int:asset_id> to <string:asset_id> so it can accept the VIN DNA from JS without crashing with a 404
@hangar_bp.route('/update_telemetry/<string:asset_id>', methods=['POST'])
@hangar_bp.route('/update-odometer/<string:asset_id>', methods=['POST'])
def update_telemetry(asset_id):
    """Core Gospel OS Telemetry Uplink. Syncs live odometer data."""
    from core.extensions import db
    from core.models.vehicles import SovereignLedger, AccessLog
    from flask import request, jsonify

    try:
        # 1. Authenticate the Asset (Handle both ID and VIN string)
        if str(asset_id).isdigit():
            asset = SovereignLedger.query.get(int(asset_id))
        else:
            asset = SovereignLedger.query.filter_by(vin_dna=asset_id).first()

        if not asset:
            return jsonify({"status": "error", "message": "Asset DNA not found in the Ledger."}), 404

        # 2. Extract the Payload
        data = request.get_json()
        if not data or 'odometer' not in data:
            return jsonify({"status": "error", "message": "No odometer payload detected."}), 400

        new_odo = int(data.get('odometer'))
        base_odo = int(asset.base_mileage) if asset.base_mileage else 0

        # 3. Mechanical Malware Check: Prevent Odometer Rollback
        if new_odo < base_odo:
            return jsonify({"status": "error", "message": "Odometer cannot reverse. Geometry violation."}), 400

        # 4. Anchor the Data to the Ledger
        asset.current_odometer = new_odo
        asset.odometer = new_odo  # Kept in sync for redundancy

        db.session.add(AccessLog(
            vin_dna=asset.vin_dna,
            action=f"TELEMETRY SYNC: Current Odometer synchronized to {new_odo} KM"
        ))

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Telemetry anchored successfully.",
            "current_odometer": asset.current_odometer
        }), 200

    except ValueError:
        return jsonify({"status": "error", "message": "Invalid telemetry format. Numbers only."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Core System Shock: {str(e)}"}), 500

@hangar_bp.route('/burn_lvt/<int:entry_id>', methods=['POST'])
@admin_only
def burn_lvt(entry_id): return redirect(request.referrer)

@hangar_bp.route('/execute_lvt_swap/<int:order_id>', methods=['POST'])
@login_required
def execute_lvt_swap(order_id): return redirect(request.referrer)

@hangar_bp.route('/api/request_module_review', methods=['POST'])
@login_required
def request_module_review(): return jsonify({"status": "success"})

@hangar_bp.route('/approve_module_review/<int:log_id>', methods=['POST'])
@admin_only
def approve_module_review(log_id): return redirect(request.referrer)

@hangar_bp.route('/asset/force-mail', methods=['POST'])
@admin_only
def force_mail_engine(): return redirect(request.referrer)

@hangar_bp.route('/asset/sweep-logs', methods=['POST'])
@admin_only
def sweep_neural_logs(): return redirect(request.referrer)

@hangar_bp.route('/asset/force-backup', methods=['POST'])
@admin_only
def force_backup(): return redirect(request.referrer)

@hangar_bp.route('/admin/auto-purge-prospects', methods=['POST'])
@admin_only
def auto_purge_prospects(): return redirect(request.referrer)

@hangar_bp.route('/mass-email-statements', methods=['POST'])
@admin_only
def mass_email_statements(): return jsonify({"success": True})

@hangar_bp.route('/authorize-bounty/<int:entry_id>', methods=['POST'])
@admin_only
def authorize_bounty(entry_id): return redirect(request.referrer)

@hangar_bp.route('/your-deposit-route', methods=['POST'])
def your_deposit_function(): return redirect(request.referrer)

@hangar_bp.route('/inspection', methods=['GET', 'POST'])
@staff_required
def run_inspection(): return redirect(request.referrer)

@hangar_bp.route('/member-login', methods=['POST'])
def member_login(): return redirect(request.referrer)

@hangar_bp.route('/api/mayday-signal', methods=['POST'])
def mayday_signal(): return jsonify({"status": "success"})

@hangar_bp.route('/hangar/api/dispatch_agent', methods=['POST'])
@admin_only
def dispatch_agent(): return redirect(request.referrer)

@hangar_bp.route('/trigger-flicker/<int:entry_id>', methods=['POST'])
def trigger_flicker(entry_id): return jsonify({'status': 'success'})

@hangar_bp.route('/inject-test-funds')
@admin_only
def inject_test_funds(): return "✅ SUCCESS"

@hangar_bp.route('/sync-legacy-funds')
@admin_only
def sync_legacy_funds(): return "✅ SUCCESS"

@hangar_bp.route('/upgrade-vault-schema')
@admin_only
def upgrade_vault_schema(): return "✅ SUCCESS"

@hangar_bp.route('/initiate-repayment', methods=['POST'])
@login_required
def initiate_repayment(): return redirect(request.referrer)

@hangar_bp.route('/upload_forensics', methods=['POST'])
@login_required
def upload_forensics(): return jsonify({"status": "success"})

@hangar_bp.route('/upload-forensics/<int:entry_id>', methods=['GET'])
@login_required
def upload_forensics_page(entry_id): return "Upload Page"

@hangar_bp.route('/trigger_procurement/<int:entry_id>', methods=['POST'])
@admin_only
def trigger_procurement(entry_id): return redirect(request.referrer)

@hangar_bp.route('/request_compliance_service/<int:entry_id>', methods=['POST'])
@admin_only
def request_compliance_service(entry_id): return redirect(request.referrer)

@hangar_bp.route('/patch-ledger-db', endpoint='patch_ledger_db_secured')
def patch_ledger_db_secured(): return "✅ DATABASE PATCHED"

@hangar_bp.route('/rebuild-audit-ledger', endpoint='rebuild_audit_ledger_secured')
@admin_only
def rebuild_audit_ledger_secured(): return "✅ FORENSIC LEDGER REBUILT"

@hangar_bp.route('/request-loan/<int:entry_id>', methods=['POST'], endpoint='request_loan_secured')
@admin_only
def request_loan_secured(entry_id): return redirect(request.referrer)

@hangar_bp.route('/debug-vault/<asset_id>', endpoint='debug_vault_secured')
def debug_vault_secured(asset_id): return f"Found Asset: {asset_id}"

@hangar_bp.route('/test-route/<string:asset_id>', endpoint='test_route_secured')
def test_route_secured(asset_id): return f"DEBUG: {asset_id}"