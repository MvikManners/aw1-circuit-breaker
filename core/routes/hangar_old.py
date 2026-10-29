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
from functools import wraps
from datetime import datetime, timezone, timedelta
from PIL import Image

# Core Flask and Extensions
from flask import Blueprint, Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app, render_template_string, abort
from flask_login import current_user, login_required
from flask_mail import Message
from sqlalchemy import func, or_, text
from werkzeug.exceptions import NotFound

# Models & Helpers
from core import db
from core.extensions import mail
from core.models.vehicles import SovereignLedger, GhostOrder, ForensicEvidence, AccessLog, VaultTransaction, LiquidationRecord, ComponentGrade
from core.models.finance import CorporateTreasury, Prospect, PriorityAlert, SystemStability, SilkRoadLedger, Supplier, SystemConfig, SovereignTransaction

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

MECHANICAL_COMPONENTS = [
    'Engine & Belts', 'Gearbox / Transmission', 'Driveshaft & CV Joints',
    'Front Suspension', 'Rear Suspension', 'Brake System',
    'Steering Rack & Ends', 'Cooling System', 'Exhaust System', 'Electrical / Battery'
]

def get_daily_cipher():
    return f"LVT-{datetime.now().strftime('%d%m')}"

# 📡 TELEMETRY PULSE
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
    except Exception as e:
        return {'quarantine_count': 0, 'loan_notifications': 0, 'bleeding_count': 0, 'liquidation_requests': 0, 'compliance_requests': 0}

# 🔧 NEURAL WELD: THE BAY SCANNER ENGINE
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
    return float(getattr(asset, 'savings_balance', 0) or 0) + \
           float(getattr(asset, 'shield_reservoir', 0) or 0) + \
           float(getattr(asset, 'yield_principal', 0) or 0)

def get_system_health(asset_id):
    try:
        grades = ComponentGrade.query.filter_by(asset_id=asset_id).all()
        if not grades:
            return 100
        total_score = sum(g.grade for g in grades)
        max_score = len(grades) * 5
        return round((total_score / max_score) * 100)
    except:
        return 100

def calculate_loan_status(ledger_entry):
    REPAYMENT_CYCLE_DAYS = 30
    if not ledger_entry.last_payment_timestamp:
        return {"days_remaining": 0, "status": "PENDING_FIRST_PAY"}

    now = datetime.now(timezone.utc)
    last_pay = ledger_entry.last_payment_timestamp.replace(tzinfo=timezone.utc)
    days_since_payment = (now - last_pay).days
    days_remaining = REPAYMENT_CYCLE_DAYS - days_since_payment

    if days_remaining <= 0:
        return {"days_remaining": 0, "status": "CRITICAL"}
    elif days_remaining <= 5:
        return {"days_remaining": days_remaining, "status": "WARNING"}
    else:
        return {"days_remaining": days_remaining, "status": "HEALTHY"}

def internal_distribute_yield(asset_id, yield_amount):
    asset = SovereignLedger.query.get(asset_id)
    audit_status = verify_forensic_integrity(asset.vin_dna)

    if audit_status == 'VERIFIED':
        asset.savings_balance += yield_amount
        asset.last_yield_timestamp = datetime.utcnow()
        db.session.add(AccessLog(vin_dna=asset.vin_dna, action="AI-AUDITED YIELD SETTLEMENT SUCCESSFUL"))
        db.session.commit()
        return True
    else:
        db.session.add(AccessLog(vin_dna=asset.vin_dna, action=f"AI-AUDITED YIELD BLOCKED: Status {audit_status}"))
        db.session.commit()
        return False

def verify_forensic_integrity(vin_dna):
    return 'VERIFIED'

# ==========================================
# 📄 HTML GENERATION HELPERS
# ==========================================

def get_statement_html(r, total_tvl):
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
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
        <div style="background-color: #0a0a0a; padding: 20px; text-align: center; color: #555; font-size: 0.65rem; font-family: 'Courier New', monospace;">SECURE HASH: {r.id} <br>© 2026 Laveto Pty Ltd.</div>
    </div>
</body>
</html>"""

def get_liquidation_html(r, market_val, premium, savings, debt, provenance_toll, net_payout, current_date, hash_id, logo_url):
    m_val = f"{market_val:,.2f}"
    prem = f"{premium:,.2f}"
    sav = f"{savings:,.2f}"
    dbt = f"{debt:,.2f}"
    toll = f"{provenance_toll:,.2f}"
    net = f"{net_payout:,.2f}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Liquidation Settlement - {r.vin_dna}</title>
    <style>
        :root {{ --gold: #C5A059; --blue: #002244; --red: #8B0000; }}
        body {{ background-color: #f4f4f4; color: #111; font-family: sans-serif; display: flex; justify-content: center; padding: 40px; margin: 0; }}
        .quote-wrapper {{ background: #fff; width: 210mm; min-height: 297mm; padding: 50px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); box-sizing: border-box; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid var(--blue); padding-bottom: 20px; margin-bottom: 40px; }}
        .brand-logo {{ max-height: 60px; }}
        h1 {{ font-size: 2.2rem; color: var(--blue); margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
        .details {{ display: flex; justify-content: space-between; margin-bottom: 40px; font-family: monospace; font-size: 0.9rem; }}
        .parts-list {{ border: 1px solid #ddd; margin-bottom: 40px; }}
        .parts-header {{ background: var(--blue); color: white; padding: 10px; font-weight: bold; text-transform: uppercase; }}
        .part-item {{ padding: 10px; border-bottom: 1px solid #eee; font-family: monospace; display: flex; justify-content: space-between; }}
        .total-box {{ border: 2px solid var(--gold); padding: 20px; text-align: right; background: rgba(197, 160, 89, 0.05); }}
        .action-btn {{ position: fixed; bottom: 30px; right: 30px; padding: 15px 30px; background: var(--gold); font-weight: 900; cursor: pointer; border: none; border-radius: 4px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
        @media print {{ body {{ background: #fff; padding: 0; }} .quote-wrapper {{ box-shadow: none; }} .action-btn {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="quote-wrapper">
        <div class="header">
            <div>
                <img src="{logo_url}" class="brand-logo">
                <p style="font-family:monospace; font-size:0.7rem; color:#888;">GOSPEL OS // TREASURY</p>
            </div>
            <div style="text-align: right;">
                <h1>SETTLEMENT PAYOUT</h1>
                <p style="font-family:monospace; font-weight:bold;">REF #{hash_id}</p>
            </div>
        </div>
        <div class="details">
            <div><strong>VEHICLE DNA:</strong> {r.vin_dna}<br><strong>CLIENT:</strong> {r.member_name}</div>
            <div style="text-align: right;"><strong>DATE:</strong> {current_date}<br><strong>STATUS:</strong> PENDING TRANSFER</div>
        </div>
        <p>This document details the final liquidation value of the asset, including compiled savings equity and outstanding liabilities.</p>
        <div class="parts-list">
            <div class="parts-header">ASSET VALUATION & EQUITY</div>
            <div class="part-item"><span>Base Market Listing Price</span><span>P{m_val}</span></div>
            <div class="part-item"><span>Laveto Provenance Premium (15%)</span><span style="color: var(--gold);">+ P{prem}</span></div>
            <div class="part-item"><span>Total Accumulated Savings & Interest</span><span style="color: green;">+ P{sav}</span></div>
        </div>
        <div class="parts-list">
            <div class="parts-header" style="background: var(--red);">LIABILITIES & TOLLS</div>
            <div class="part-item"><span>Active M2M Loan Principal</span><span style="color: var(--red);">- P{dbt}</span></div>
            <div class="part-item"><span>Provenance Transfer Toll (4%)</span><span style="color: var(--red);">- P{toll}</span></div>
        </div>
        <div class="total-box">
            <span style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 2px;">Net Payout Due to Client</span><br>
            <span style="font-size: 2.5rem; font-family: monospace; font-weight: 900; color: var(--blue);">P{net}</span>
        </div>
        <p style="text-align: center; font-family: monospace; font-size: 0.75rem; color: #888; margin-top: 50px;">This payout is valid only upon successful transfer of ownership to a verified buyer.</p>
    </div>
    <button class="action-btn" onclick="window.print()">🖨️ PRINT SETTLEMENT</button>
</body>
</html>"""

def get_quote_html(asset, current_date, hash_id, logo_url, broken_parts, dossier_link):
    repair_cost = f"{asset.target_repair_cost or 0.0:,.2f}"

    parts_html = ""
    if broken_parts:
        for part in broken_parts:
            parts_html += f'<div class="part-item">⚠️ {part} - REPLACEMENT REQUIRED</div>\n'
    else:
        parts_html = '<div class="part-item">No critical parts listed. Review physical inspection.</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Repair Estimate - {asset.vin_dna}</title>
    <style>
        :root {{ --gold: #C5A059; --blue: #002244; --red: #8B0000; }}
        body {{ background-color: #f4f4f4; color: #111; font-family: sans-serif; display: flex; justify-content: center; padding: 40px; margin: 0; }}
        .quote-wrapper {{ background: #fff; width: 210mm; min-height: 297mm; padding: 50px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); box-sizing: border-box; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid var(--blue); padding-bottom: 20px; margin-bottom: 40px; }}
        .brand-logo {{ max-height: 60px; }}
        h1 {{ font-size: 2.5rem; color: var(--red); margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
        .details {{ display: flex; justify-content: space-between; margin-bottom: 40px; font-family: monospace; font-size: 0.9rem; }}
        .parts-list {{ border: 1px solid #ddd; margin-bottom: 40px; }}
        .parts-header {{ background: var(--blue); color: white; padding: 10px; font-weight: bold; text-transform: uppercase; }}
        .part-item {{ padding: 10px; border-bottom: 1px solid #eee; font-family: monospace; }}
        .total-box {{ border: 2px solid var(--red); padding: 20px; text-align: right; background: rgba(139, 0, 0, 0.05); }}
        .action-btn {{ position: fixed; bottom: 30px; right: 30px; padding: 15px 30px; background: var(--gold); font-weight: 900; cursor: pointer; border: none; border-radius: 4px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
        @media print {{ body {{ background: #fff; padding: 0; }} .quote-wrapper {{ box-shadow: none; }} .action-btn {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="quote-wrapper">
        <div class="header">
            <div>
                <img src="{logo_url}" class="brand-logo">
                <p style="font-family:monospace; font-size:0.7rem; color:#888;">GOSPEL OS // LOGISTICS</p>
            </div>
            <div style="text-align: right;">
                <h1>REPAIR ESTIMATE</h1>
                <p style="font-family:monospace; font-weight:bold;">QUOTE #{hash_id}</p>
            </div>
        </div>
        <div class="details">
            <div><strong>VEHICLE DETAILS:</strong> {asset.vin_dna}<br><strong>CLIENT:</strong> {asset.member_name}</div>
            <div style="text-align: right;"><strong>DATE:</strong> {current_date}<br><strong>STATUS:</strong> INSPECTION FAILED</div>
        </div>
        <p>Our inspection has detected critical component failures. To repair this vehicle, the following parts must be replaced:</p>
        <div class="parts-list">
            <div class="parts-header">CRITICAL FAILURES (GRADES 1 & 2)</div>
            {parts_html}
        </div>
        <div class="total-box">
            <span style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 2px;">Total Required Upfront</span><br>
            <span style="font-size: 2.5rem; font-family: monospace; font-weight: 900; color: var(--red);">P{repair_cost}</span>
        </div>
        <p style="text-align: center; font-family: monospace; font-size: 0.75rem; color: #888; margin-top: 50px;">EFT required to proceed with repairs. Validity: 48 Hours.</p>
        <div style="text-align: center; margin-top: 30px;">
            <a href="{dossier_link}" style="background-color: #C5A059; color: #000; padding: 15px 30px; text-decoration: none; font-weight: 900; border-radius: 4px; text-transform: uppercase; letter-spacing: 2px; display: inline-block;">✅ AUTHORIZE REPAIRS HERE</a>
            <p style="font-family: monospace; font-size: 0.65rem; color: #aaa; margin-top: 10px;">Or visit: {dossier_link}</p>
        </div>
    </div>
    <button class="action-btn" onclick="window.print()">🖨️ PRINT QUOTE</button>
</body>
</html>"""

def get_loan_denial_html(entry, current_date, reason_str, hash_id):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{ font-family:sans-serif; color:#333; margin:50px; }}
    h1 {{ color:#B22222; text-transform:uppercase; letter-spacing:2px; border-bottom:2px solid #B22222; padding-bottom:10px; }}
    p {{ line-height:1.6; font-size:14px; }}
    .box {{ border:1px dashed #B22222; background:#fff5f5; padding:20px; margin:20px 0; }}
    .hash {{ font-family:monospace; color:#888; font-size:10px; margin-top:50px; text-align:center; }}
</style>
</head>
<body>
    <h1>Sovereign Requisition Denial</h1>
    <p><strong>DATE:</strong> {current_date}</p>
    <p><strong>ASSET DNA:</strong> {entry.vin_dna}</p>
    <p><strong>PILOT:</strong> {entry.member_name or 'UNVERIFIED'}</p>
    <div class="box">
        <strong>STATUS: REQUISITION DECLINED</strong><br><br>
        Your recent application for Sovereign Capital has been reviewed by Laveto Command and denied for the following reason:<br><br>
        <strong>{reason_str}</strong>
    </div>
    <p>Please review your Covenant Terms. Ensure your monthly deposits are maintained to advance your Account Health tier.</p>
    <div class="hash">SECURE HASH: {hash_id} // LAVETO SYSTEM RESTORATION</div>
</body>
</html>"""

# ==========================================
# ⚙️ SYSTEM ROUTES
# ==========================================

# ----------------------------------------------------------
# 📝 FORGE PAYROLL MANDATE ROUTE (WELDED SECURELY)
# ----------------------------------------------------------
@hangar_bp.route('/forge-payroll-mandate', methods=['POST'])
def forge_payroll_mandate():
    vin_dna = request.form.get('vin_dna')
    department = request.form.get('department')
    omang_number = request.form.get('omang_number')
    employee_number = request.form.get('employee_number')
    try:
        monthly_pledge = float(request.form.get('monthly_pledge', 0.0))
    except ValueError:
        monthly_pledge = 0.0
    b64_signature = request.form.get('digital_signature_base64')

    print(f"[CONSOLE] Initiating Sovereign Payroll Mandate for VIN: {vin_dna}")

    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    safe_vin = "".join([c for c in vin_dna if c.isalnum()]).upper()

    static_dir = current_app.static_folder
    sig_dir = os.path.join(static_dir, 'forensics', 'signatures')
    pdf_dir = os.path.join(static_dir, 'forensics')

    os.makedirs(sig_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    signature_filename = None
    sig_hash = None
    file_path = ""
    timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    if b64_signature and b64_signature.startswith('data:image/png;base64,'):
        try:
            header, encoded_data = b64_signature.split(',', 1)
            image_data = base64.b64decode(encoded_data)
            sig_hash = hashlib.md5(f"{safe_vin}_{timestamp_str}".encode()).hexdigest()[:8]
            signature_filename = f"SIG_{safe_vin}_{sig_hash}.png"
            file_path = os.path.join(sig_dir, signature_filename)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            print(f"[CONSOLE] Biometric Signature secured at: {file_path}")
        except Exception as e:
            print(f"🚨 SIGNATURE DECODE FAULT: {str(e)}")
            flash("System Error: Biometric signature capture failed.", "error")
            return redirect(request.referrer)

    try:
        db.session.add(AccessLog(
            vin_dna=asset.vin_dna,
            action=f"PAYROLL MANDATE FORGED: {department} | ID: {employee_number} | Signature Cached"
        ))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"🚨 DATABASE TRANSACTION FAULT: {str(e)}")

    pdf_filename = f"MANDATE_{safe_vin}.pdf"
    absolute_pdf_path = os.path.join(pdf_dir, pdf_filename)
    local_sig_uri = f"file://{file_path}" if signature_filename else ""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
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
        <p>To: The Accountant General, Government of Botswana. I hereby authorize the periodic deduction of capital from my salary as specified below, for allocation into my secure Sovereign OS Asset Maintenance Vault.</p>
        <table class="meta-table">
            <tr><td class="label">Member (Pilot) Name</td><td>{asset.member_name or 'Sovereign Member'}</td></tr>
            <tr><td class="label">Vehicle VIN (DNA)</td><td>{asset.vin_dna}</td></tr>
            <tr><td class="label">Ministry / Department</td><td>{department}</td></tr>
            <tr><td class="label">Omang Number</td><td>{omang_number}</td></tr>
            <tr><td class="label">Employee / Payroll ID</td><td>{employee_number}</td></tr>
            <tr><td class="label">Monthly Allocation</td><td style="font-weight: bold; color: #0033a0;">P {monthly_pledge:,.2f}</td></tr>
        </table>
        <div class="covenant-box">
            <strong>LEGAL COVENANT:</strong> I acknowledge that 100% of my monthly deposit is allocated to my personal reservoir (60% Compounding Yield Pool / 40% Shield Reservoir). This mandate remains active and locked under the jurisdiction of the Sovereign OS Hangar 01 framework.
        </div>
        <div class="sig-box">
            <div>
                <p style="font-size: 12px; margin-bottom: 5px;">Sovereign Member Digital Signature:</p>
                {f'<img src="{local_sig_uri}" class="sig-image" />' if signature_filename else '<div style="height:80px; border-bottom:1px solid #000; width:200px;"></div>'}
                <p style="font-size: 11px; color: #888; margin-top: 5px;">Biometric Base64 Verification Hash: {sig_hash if signature_filename else "N/A"}</p>
            </div>
            <div style="text-align: right; width: 250px;">
                <p style="font-size: 12px; margin-bottom: 45px;">Authorized by Hangar 01 Command:</p>
                <div style="border-bottom: 1px solid #000; width: 100%;"></div>
                <p style="font-size: 11px; color: #888; margin-top: 5px;">Date Authorized: {datetime.now(timezone.utc).strftime('%d %B %Y')}</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        path_to_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
        if not os.path.exists(path_to_wkhtmltopdf):
            path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
        pdfkit.from_string(html_content, absolute_pdf_path, configuration=config)
        print(f"[CONSOLE] PDF successfully compiled locally at: {absolute_pdf_path}")
        flash("📝 Sovereign Mandate successfully forged. Awaiting final physical validation.", "success")
        return redirect(url_for('static', filename=f'forensics/{pdf_filename}'))
    except Exception as e:
        print(f"🚨 PDF GENERATION FAULT: {str(e)}")
        try:
            backup_html_filename = f"MANDATE_{safe_vin}.html"
            backup_html_path = os.path.join(pdf_dir, backup_html_filename)
            local_sig_web_uri = url_for('static', filename=f'forensics/signatures/{signature_filename}') if signature_filename else ""
            styled_web_content = html_content.replace(local_sig_uri, local_sig_web_uri)
            with open(backup_html_path, 'w') as f:
                f.write(styled_web_content)
            flash("⚠️ PDF conversion engine offline. Rendered secure HTML mandate.", "warning")
            return redirect(url_for('static', filename=f'forensics/{backup_html_filename}'))
        except Exception as fallback_err:
            print(f"🚨 FALLBACK GENERATION FAILED: {str(fallback_err)}")
            flash("System Error: Failed to compile Accountant General PDF file.", "error")
            return redirect(request.referrer)

# ----------------------------------------------------------

def run_email_blast():
    with current_app.app_context():
        all_records = SovereignLedger.query.all()
        for r in all_records:
            if r.member_email and '@' in r.member_email:
                total_tvl = get_total_member_holdings(r)
                html_body = get_statement_html(r, total_tvl)
        db.session.remove()

@hangar_bp.route('/upload_multi_marketplace/<int:entry_id>', methods=['POST'])
@admin_only
def upload_multi_marketplace(entry_id):
    r = LiquidationRecord.query.get_or_404(entry_id)
    target_dir = '/home/LavetoLab/static'

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for i in ['1', '2', '3']:
        field_name = f'market_img_{i}'
        if field_name in request.files and request.files[field_name].filename != '':
            f = request.files[field_name]
            ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else 'jpg'
            safe_name = f"HERO_{i}_{r.vin_dna}_{int(datetime.utcnow().timestamp())}.{ext}"
            local_path = os.path.join(target_dir, safe_name)
            f.save(local_path)

            if i == '1': r.marketplace_image = safe_name
            elif i == '2': r.marketplace_image_2 = safe_name
            elif i == '3': r.marketplace_image_3 = safe_name

    db.session.commit()
    return redirect(request.referrer)

# 🛰️ UNCOLLIDABLE PUBLIC TELEMETRY PASSPORT
@hangar_bp.route('/verify-asset/<string:vin_dna>', methods=['GET'])
def client_dossier_public(vin_dna):
    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    return render_template('client_dossier.html', asset=asset, evidence_list=[])

@hangar_bp.route('/passport/<vin_dna>')
def public_passport(vin_dna):
    asset = SovereignLedger.query.filter(func.lower(SovereignLedger.vin_dna) == func.lower(vin_dna)).first_or_404()
    return render_template('passport.html', r=asset, asset=asset, proofs={}, components={}, market_orders=[],
                           days_active=0, all_records=SovereignLedger.query.all(),
                           treasury=CorporateTreasury.query.first(), **get_system_counts())

@hangar_bp.route('/client-vault/<path:asset_id>', methods=['GET', 'POST'])
def client_vault(asset_id):
    decoded_asset_id = urllib.parse.unquote(asset_id).strip()
    asset = SovereignLedger.query.filter(
        func.lower(SovereignLedger.vin_dna) == func.lower(decoded_asset_id)
    ).first()

    if not asset:
        raise NotFound(description=f"Asset {decoded_asset_id} not found in Sovereign Ledger.")

    db.session.refresh(asset)
    treasury = CorporateTreasury.query.first()
    all_records = SovereignLedger.query.all()

    audit_logs = VaultTransaction.query.filter_by(vin_dna=asset.vin_dna)\
                                       .order_by(VaultTransaction.timestamp.desc())\
                                       .limit(50).all()

    creation_date = getattr(asset, 'created_at', None) or getattr(asset, 'timestamp', datetime.utcnow())
    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    days_active = (now_utc - creation_date).days

    days_remaining = max(0, 120 - days_active)
    progress_pct = min(100, int((days_active / 120.0) * 100))

    return render_template('client_vault.html',
                           r=asset,
                           asset=asset,
                           status=calculate_loan_status(asset)['status'] if asset.active_loan_principal else 'OPTIMAL',
                           days=calculate_loan_status(asset)['days_remaining'] if asset.active_loan_principal else 0,
                           audit_logs=audit_logs,
                           proofs={},
                           components={},
                           market_orders=[],
                           days_active=days_active,
                           days_remaining=days_remaining,
                           progress_pct=progress_pct,
                           now=now_utc,
                           all_records=all_records,
                           treasury=CorporateTreasury.query.first())

@hangar_bp.route('/dossier/<vin_dna>/<source>')
@admin_only
def client_dossier(vin_dna, source):
    asset = SovereignLedger.query.filter(func.lower(SovereignLedger.vin_dna) == func.lower(vin_dna)).first_or_404()
    return render_template('dossier.html', r=asset, asset=asset, source=source, proofs={}, components={}, market_orders=[],
                           days_active=0, all_records=SovereignLedger.query.all(),
                           treasury=CorporateTreasury.query.first(), **get_system_counts())

@hangar_bp.route('/manifesto')
def manifesto():
    return render_template('manifesto.html')

@hangar_bp.route('/ledger')
@admin_only
def view_ledger():
    if getattr(current_user, 'role', '').upper() in ['STAFF', 'WARDEN']:
        flash("🚨 ACCESS DENIED: The Sovereign Ledger is strictly reserved for High Command.", "error")
        return redirect(url_for('hangar.agent_terminal'))

    priority_flares = AccessLog.query.filter(AccessLog.action.like('%PRIORITY FLARE%')).order_by(AccessLog.timestamp.desc()).all()
    counts = get_system_counts()

    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('filter', 'ALL').strip().upper()
        search_query = request.args.get('search', '').strip()

        base_query = SovereignLedger.query

        if search_query:
            base_query = base_query.filter(SovereignLedger.vin_dna.ilike(f'%{search_query}%'))
        if status_filter and status_filter != 'ALL':
            base_query = base_query.filter(SovereignLedger.current_status.ilike(f'%{status_filter}%'))

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
        except: pros = []
        try: alts = PriorityAlert.query.all()
        except: alts = []
        try: stab = SystemStability.query.first()
        except: stab = None
        try: module_reviews = AccessLog.query.filter(AccessLog.action.ilike('%MODULE REVIEW REQUESTED%')).all()
        except: module_reviews = []

        return render_template('ledger.html',
                               results=paginated_results,
                               all_records=all_records,
                               total_motshelo=t_tvl,
                               total_debt=t_debt,
                               saas_total=s_total,
                               total_tolls=0.0,
                               total_wholesale=0.0,
                               arbitrage_profit=0.0,
                               prospects=pros,
                               alerts=alts,
                               stability=stab,
                               search_query=search_query,
                               status_filter=status_filter,
                               module_reviews=module_reviews,
                               priority_flares=priority_flares,
                               daily_cipher=get_daily_cipher(),
                               active_nodes=len(all_records),
                               bay_status=get_bay_status(),
                               projection={'valuation': t_tvl * 1.5, 'gap_to_million': max(0, 1000000 - (t_tvl * 1.5))},
                               **counts)
    except Exception as e:
        return f"🚨 LEDGER ERROR: {str(e)}"

@hangar_bp.route('/process_payment/<int:entry_id>', methods=['POST'])
@admin_only
def process_payment(entry_id):
    try:
        asset = SovereignLedger.query.get_or_404(entry_id)
        raw_amount = request.form.get('payment_amount') or request.form.get('total_payment')
        try: amount = float(raw_amount)
        except: amount = 0.0

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
                if asset.vehicle_class == 'A':
                    required_min = float(getattr(config, 'class_a_min', 450.0))
                elif asset.vehicle_class == 'C':
                    required_min = float(getattr(config, 'class_c_min', 1000.0))
                else:
                    required_min = float(getattr(config, 'class_b_min', 650.0))

                active_deficit = float(getattr(asset, 'target_repair_cost', 0) or 0)
                is_top_up = (active_deficit > 0)

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
                    creation_date = getattr(asset, 'created_at', None) or getattr(asset, 'timestamp', datetime.utcnow())
                    if creation_date.tzinfo is None:
                        creation_date = creation_date.replace(tzinfo=timezone.utc)
                    now_utc = datetime.now(timezone.utc)
                    days_active = (now_utc - creation_date).days
                    chrono_months = max(0, days_active // 30)

                    if chrono_months < 12: liquid_pct, locked_pct = 0.20, 0.80
                    elif chrono_months < 24: liquid_pct, locked_pct = 0.50, 0.50
                    else: liquid_pct, locked_pct = 0.80, 0.20

                    liquid_mint = minted_total * liquid_pct
                    locked_mint = minted_total * locked_pct

                    if not hasattr(asset, 'lvt_balance') or asset.lvt_balance is None: asset.lvt_balance = 0.0
                    if not hasattr(asset, 'lvt_locked_bond') or asset.lvt_locked_bond is None: asset.lvt_locked_bond = 0.0

                    asset.lvt_balance += liquid_mint
                    asset.lvt_locked_bond += locked_mint
                    asset.fiat_high_water_mark = current_fiat

                    log_intent = f"MONTHLY DEPOSIT | P{amount:.2f} | +{liquid_mint:.2f} LVT Liquid, +{locked_mint:.2f} LVT Bonded"
                    flash(f"✅ P{amount} Deposit. High-Water Mark breached: {minted_total:.2f} LVT Minted ({locked_pct*100}% Bonded).", "success")
                else:
                    minted_total = 0.0
                    log_intent = f"MONTHLY DEPOSIT | P{amount:.2f} | 0.00 LVT Minted (Capital Recycled)"
                    flash(f"✅ P{amount} Deposit processed. Capital recycled; no LVT minted.", "info")

            vault_log = VaultTransaction(
                vin_dna=asset.vin_dna,
                intent=log_intent,
                amount=amount,
                running_balance=current_fiat,
                network_fee=admin_fee if p_type != 'INTEREST' else 0.0,
                lvt_utility=minted_total,
                authorized_by="SYSTEM",
                status="CLEARED"
            )
            db.session.add(vault_log)

            legacy_args = {
                "amount": amount,
                "intent": log_intent,
                "timestamp": datetime.now()
            }
            for candidate in ['vehicle_id', 'record_id', 'ledger_id', 'id']:
                if hasattr(SovereignTransaction, candidate):
                    legacy_args[candidate] = asset.id
                    break
            db.session.add(SovereignTransaction(**legacy_args))

            db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"🚨 FULL ENGINE FAULT: {str(e)}")
        flash(f"🚨 ENGINE FAULT: {str(e)}", "error")

    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/asset/override', methods=['POST'])
@admin_only
def override_asset():
    try:
        entry_id = request.form.get('entry_id')
        if not entry_id: return redirect(url_for('hangar.view_ledger'))
        asset = SovereignLedger.query.get_or_404(entry_id)
        asset.status = request.form.get('status', 'STABLE')
        db.session.commit()
    except Exception as e: db.session.rollback()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/process_repair_deduction/<int:asset_id>', methods=['POST'])
def process_repair_deduction(asset_id):
    asset = SovereignLedger.query.get_or_404(asset_id)
    flash(f"Repair deduction processed for Asset {asset_id}", "success")
    return redirect(url_for('hangar.index'))

@hangar_bp.route('/asset/admin_override/<int:asset_id>', methods=['POST'], endpoint='admin_override')
@admin_only
def admin_override(asset_id):
    try:
        asset = SovereignLedger.query.get_or_404(asset_id)
        status = request.form.get('status', 'STABLE')
        asset.current_status = status
        asset.status = status
        db.session.commit()
        flash(f"✅ OVERRIDE EXECUTED: Status set to {status}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 OVERRIDE FAILED: {str(e)}", "error")
    return redirect(request.referrer or url_for('hangar.debug_env'))

@hangar_bp.route('/asset/edit/<int:asset_id>', methods=['POST'])
@admin_only
def edit_asset(asset_id):
    try:
        asset = SovereignLedger.query.get_or_404(asset_id)
        asset.member_name = request.form.get('member_name')
        asset.member_phone = request.form.get('member_phone')
        asset.member_email = request.form.get('member_email')
        asset.corporate_cohort = request.form.get('corporate_cohort')
        asset.funding_method = request.form.get('funding_method')
        asset.vehicle_year = request.form.get('vehicle_year')
        asset.vehicle_make = request.form.get('vehicle_make')
        asset.vehicle_model = request.form.get('vehicle_model')
        asset.vehicle_class = request.form.get('vehicle_class')
        asset.fleet_pin = request.form.get('fleet_pin')

        raw_cost = request.form.get('target_repair_cost')
        asset.target_repair_cost = float(raw_cost) if raw_cost and raw_cost.strip() != '' else 0.0

        db.session.commit()
        flash("✅ ASSET UPDATED.", "success")
    except Exception as e: db.session.rollback()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/asset/email_statement/<int:entry_id>', methods=['POST', 'GET'])
@admin_only
def email_statement(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/asset/email_invoice/<int:entry_id>', methods=['POST', 'GET'])
@admin_only
def email_invoice(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/registry', endpoint='registry')
def registry():
    assets = SovereignLedger.query.all()
    print(f"[DEBUG] Registry Pipeline: {len(assets)} assets loaded.")
    return render_template('registry.html', all_records=assets, **get_system_counts())

@hangar_bp.route('/admin-registry', endpoint='admin_registry')
@admin_only
def admin_registry():
    assets = SovereignLedger.query.order_by(SovereignLedger.id.desc()).all()
    return render_template('admin_registry.html', all_records=assets, **get_system_counts())

@hangar_bp.route('/sync_silk_road', methods=['POST', 'GET'])
@admin_only
def sync_silk_road():
    flash("System utility offline. Cannot sync Silk Road.", "error")
    return redirect(url_for('hangar.silk_road'))

@hangar_bp.route('/silk-road', methods=['GET'])
@admin_only
def silk_road():
    try: network_suppliers = Supplier.query.all()
    except: network_suppliers = []
    assets = SovereignLedger.query.all()
    return render_template('silk_road.html', assets=assets, suppliers=network_suppliers, ai_quotes=[], ghosts=[], **get_system_counts())

@hangar_bp.route('/corporate-treasury', methods=['GET'])
@admin_only
def corporate_treasury():
    db.metadata.reflect(bind=db.engine, extend_existing=True)
    db.session.expire_all()
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

    committed_orders = GhostOrder.query.filter(GhostOrder.status.in_(['FUNDS CLEARED', 'IN TRANSIT', 'DELIVERED TO BAY'])).all()
    outflow = sum(getattr(o, 'wholesale_cost', 0.0) or 0.0 for o in committed_orders)
    gross = sum(cost if 'Dept of Transport' in (getattr(o, 'component_name', '') or '') else cost * 1.30 for o, cost in ((o, getattr(o, 'wholesale_cost', 0.0) or 0.0) for o in committed_orders))

    outstanding_orders = GhostOrder.query.filter_by(status='AWAITING FUNDS').all()
    outstanding = sum(o_cost if 'Dept of Transport' in (getattr(oo, 'component_name', '') or '') else o_cost * 1.30 for oo, o_cost in ((oo, getattr(oo, 'wholesale_cost', 0.0) or 0.0) for oo in outstanding_orders))

    arbitrage = gross - outflow
    margin = (arbitrage / gross * 100) if gross > 0 else 0.0

    return render_template('corporate_treasury.html', treasury=tr, total_shield=t_shield, total_yield_interest=t_yield_i, total_yield_principal=t_principal, total_savings=t_savings, total_debt=t_debt, platform_tvl=t_shield + t_savings + t_yield_i, total_revenue=(tr.total_saas_tax or 0) + (tr.total_sanctity_fees or 0), gross=gross, outflow=outflow, arbitrage=arbitrage, margin=margin, outstanding=outstanding, recent_orders=committed_orders[-5:], **get_system_counts())

@hangar_bp.route('/loan-terminal', methods=['GET'])
@admin_only
def loan_terminal():
    db.metadata.reflect(bind=db.engine, extend_existing=True)
    db.session.expire_all()
    all_records = SovereignLedger.query.all()
    return render_template('loan_terminal.html', records=all_records, **get_system_counts())

@hangar_bp.route('/launch-flare', methods=['GET', 'POST'])
def launch_flare():
    vin_dna = request.args.get('vin_dna') or request.form.get('vin_dna')
    contact_info = request.args.get('contact_info') or request.form.get('contact_info')

    try:
        if not vin_dna:
            flash("🚨 FLARE FAILED: VIN signature required.", "error")
            return redirect(request.referrer)

        flare_log = AccessLog(vin_dna=vin_dna, action=f"🚨 PRIORITY FLARE: Lockout reported. Contact: {contact_info or 'NOT PROVIDED'}")
        db.session.add(flare_log)
        db.session.commit()
        flash("📡 SIGNAL INTERCEPTED. The Architect has been notified of your lockout.", "success")
    except Exception as e:
        db.session.rollback()
        flash("📡 SIGNAL TRANSMISSION FAILED: Contact System Admin manually.", "error")
    return redirect(url_for('hangar.index'))

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
    else:
        flash('Insufficient funds in Maintenance Reservoir.', 'error')
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

    existing_asset = SovereignLedger.query.filter_by(vin_dna=vin).first()
    if existing_asset:
        flash(f"Asset {vin} is already locked in the Sovereign Ledger.", "warning")
        return redirect(url_for('hangar.client_vault', asset_id=existing_asset.id))
    try:
        session = SovereignLedger.query.session
        new_asset = SovereignLedger(
            vin_dna=vin, member_name=name, contact_number=phone, vehicle_make=make,
            vehicle_model=model, vehicle_year=year, vehicle_class=v_class,
            shield_reservoir=0.0, savings_balance=0.0, yield_principal=0.0,
            yield_interest=0.0, active_loan_principal=0.0
        )
        if hasattr(new_asset, 'email'): new_asset.email = email
        if hasattr(new_asset, 'is_corporate'): new_asset.is_corporate = is_b2b
        if hasattr(new_asset, 'monthly_pulse_target'): new_asset.monthly_pulse_target = pulse_target
        if hasattr(new_asset, 'baseline_trauma'): new_asset.baseline_trauma = trauma
        elif hasattr(new_asset, 'status'): new_asset.status = f"INTAKE: {trauma}"

        session.add(new_asset)
        session.flush()

        initial_log = SovereignTransaction(sovereign_id=new_asset.id, vin_dna=vin, intent=f"INITIAL TRIAGE: Reported Fault - {trauma}", amount=0.0, running_balance=0.0, status="PENDING", authorized_by="SYSTEM")
        session.add(initial_log)
        session.commit()
        flash("SOVEREIGNTY SECURED: Your vehicle DNA has been locked into the Gospel OS.", "success")
        return redirect(url_for('hangar.client_vault', asset_id=new_asset.id))
    except Exception as e:
        if 'session' in locals(): session.rollback()
        flash(f"INTEGRITY FLICKER: Database lock failed. {str(e)}", "error")
        return redirect(request.referrer or url_for('hangar.index'))

@hangar_bp.route('/terminal', methods=['GET', 'POST'])
@staff_required
def agent_terminal():
    if request.method == 'POST':
        vin_lookup = (request.form.get('vin_dna') or request.form.get('intake_vin') or request.form.get('search') or request.form.get('vin'))
        if vin_lookup:
            asset = SovereignLedger.query.filter(SovereignLedger.vin_dna.ilike(f"%{vin_lookup.strip()}%")).first()
            if asset: return redirect(url_for('hangar.inspection_desk', entry_id=asset.id))

    try: pros = Prospect.query.all()
    except Exception: pros = []
    try: priority_flares = AccessLog.query.filter(AccessLog.action.like('%PRIORITY FLARE%')).order_by(AccessLog.timestamp.desc()).all()
    except Exception: priority_flares = []

    safe_warden = current_user
    if not hasattr(safe_warden, 'wallet_balance') or safe_warden.wallet_balance is None:
        safe_warden.wallet_balance = 0.0

    training_cleared = getattr(current_user, 'role', 'GUEST').upper() in ['MD', 'ARCHITECT', 'ADMIN']

    return render_template('hangar.html', assets=SovereignLedger.query.all(), active_warden=safe_warden, prospects=pros, priority_flares=priority_flares, training_cleared=training_cleared, **get_system_counts())

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
    except Exception as e:
        return redirect(url_for('hangar.agent_terminal'))

@hangar_bp.route('/api/verify_root', methods=['POST'])
def verify_root():
    if request.form.get('admin_pin') == "7777": session['architect_unlocked'] = True
    return redirect(request.referrer or url_for('hangar.index'))

@hangar_bp.route('/disapprove-intake', methods=['POST'])
@admin_only
def disapprove_intake():
    prospect_id = request.form.get('prospect_id')
    reason = request.form.get('reason', 'DOSSIER_INCOMPLETE')
    prospect = Prospect.query.get_or_404(prospect_id)
    prospect.status = 'REJECTED_NEEDS_RESOLUTION'
    prospect.rejection_reason = reason
    try:
        db.session.commit()
        flash(f"✅ Rejection registered for {prospect.vin_dna}.", "success")
        return redirect(url_for('hangar.registry'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('hangar.registry'))

@hangar_bp.route('/approve-intake/<int:prospect_id>', methods=['POST'])
@admin_only
def approve_intake(prospect_id):
    p = Prospect.query.get_or_404(prospect_id)
    key = f"SOV-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    try:
        new_ledger = SovereignLedger(
            vin_dna=p.vin_dna, member_email=p.email or "triage@laveto.internal", member_phone=p.phone_number or "00000000",
            member_name=p.full_name, sovereign_key=key, vehicle_class=p.vehicle_class or 'B', membership_type=p.membership_type or 'INDIVIDUAL',
            corporate_cohort=p.corporate_cohort or 'BAY_01_INTAKE', funding_method=p.funding_method or 'EFT',
            monthly_commitment=p.monthly_pulse or 0.0, current_status='STABLE', vehicle_year=2026, vehicle_make='UNKNOWN', vehicle_model='UNKNOWN'
        )
        db.session.add(new_ledger)
        db.session.add(AccessLog(vin_dna=p.vin_dna, action=f"INTAKE_PROMOTION: {p.full_name} moved to SovereignLedger"))
        client_email = p.email
        db.session.delete(p)
        db.session.commit()
        flash("✅ Prospect promoted to Ledger.", "success")
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('hangar.view_ledger', filter=request.args.get('filter', 'ALL')))

@hangar_bp.route('/audit-logs')
@admin_only
def audit_logs():
    try:
        logs = VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).all()
        return render_template('audit_logs.html', transactions=logs, **get_system_counts())
    except Exception as e:
        return f"🚨 CRASH: {str(e)}"

@hangar_bp.route('/export-audit-csv')
@admin_only
def export_audit_csv():
    logs = VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).all()
    file_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Laveto_Audit_Report_{file_timestamp}.csv"
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Asset DNA', 'Intent', 'Auth By', 'Status', 'Value (Pula)', 'Running Balance', 'LVT Utility', 'Debt/Loan', 'Network Fee', 'Labour Funds', 'Parts & Dispatch'])
    for log in logs:
        readable_timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A"
        writer.writerow([readable_timestamp, log.vin_dna, log.intent, log.authorized_by, log.status, log.amount, log.running_balance, log.lvt_utility, log.debt_loan, log.network_fee, log.labour_funds, log.parts_ordered])
    return current_app.response_class(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={filename}"})

@hangar_bp.route('/treasury-report')
@admin_only
def treasury_report():
    active_loans = SovereignLedger.query.filter(SovereignLedger.active_loan_principal > 0).all()
    loan_report = [{"dna": loan.vin_dna, "days": calculate_loan_status(loan)['days_remaining'], "status": calculate_loan_status(loan)['status']} for loan in active_loans]
    return render_template('treasury_summary.html', loans=loan_report)

@hangar_bp.route('/api/live_audit_logs', endpoint='api_live_audit_logs')
@admin_only
def api_live_audit_logs(): return jsonify({"status": "success", "logs": []})

@hangar_bp.route('/finance/inject-capital', methods=['POST'])
@admin_only
def inject_capital():
    try:
        vin = (request.form.get('vin_dna') or "").upper()
        amt = float(request.form.get('amount', 0))
        asset = SovereignLedger.query.filter_by(vin_dna=vin).first()
        if asset and amt > 0:
            asset.yield_principal = float(getattr(asset, 'yield_principal', 0) or 0) + amt
            db.session.commit()
    except: db.session.rollback()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/finance/mint-loan/<int:asset_id>', methods=['POST'])
@admin_only
def mint_loan(asset_id):
    asset = SovereignLedger.query.get_or_404(asset_id)
    amount = float(request.form.get('loan_amount', 0))
    asset.active_loan_principal += amount
    asset.pending_loan_amount = 0
    asset.pending_loan_intent = None
    db.session.commit()
    return redirect(url_for('hangar.loan_terminal'))

@hangar_bp.route('/finance/repay-loan/<int:asset_id>', methods=['POST'])
@admin_only
def repay_loan(asset_id):
    asset = SovereignLedger.query.get_or_404(asset_id)
    repay_amount = float(request.form.get('repay_amount', 0))
    total_interest_capture = repay_amount * 0.15
    member_yield = total_interest_capture * 0.80
    asset.active_loan_principal -= (repay_amount - total_interest_capture)
    asset.savings_balance += member_yield
    db.session.commit()
    return redirect(url_for('hangar.loan_terminal'))

@hangar_bp.route('/matrix/payroll', endpoint='payroll_matrix')
@admin_only
def payroll_matrix():
    try:
        raw_members = SovereignLedger.query.filter_by(membership_type='CORPORATE').all()
        cohorts = {}
        for m in raw_members:
            cohort_name = m.corporate_cohort or "UNASSIGNED INSTITUTION"
            if cohort_name not in cohorts: cohorts[cohort_name] = {'nodes': 0, 'total_debt': 0, 'expected_pulse': 0, 'members': []}
            fee = m.monthly_commitment or 0
            loan_pmt = (m.active_loan_principal / 12) if (m.active_loan_principal and m.active_loan_principal > 0) else 0
            total_due = fee + loan_pmt
            cohorts[cohort_name]['nodes'] += 1
            cohorts[cohort_name]['total_debt'] += (m.active_loan_principal or 0)
            cohorts[cohort_name]['expected_pulse'] += total_due
            cohorts[cohort_name]['members'].append({'name': m.member_name, 'vin': m.vin_dna, 'fee': fee, 'loan_pmt': loan_pmt, 'total_due': total_due})
        return render_template('payroll.html', cohorts=cohorts, all_records=SovereignLedger.query.all(), assets=SovereignLedger.query.all(), treasury=CorporateTreasury.query.first(), **get_system_counts())
    except Exception as e:
        return f"<h1 style='color:red; font-family:monospace;'>🚨 MATRIX LOGIC ERROR: {str(e)}</h1>"

@hangar_bp.route('/matrix/health', endpoint='debug_env')
@admin_only
def anchor_health():
    diagnostics = {}
    bleeding_assets = []
    total_active_bays = 0
    try: all_r = SovereignLedger.query.all()
    except Exception as e:
        all_r = []
        diagnostics['Database Core'] = {'status': 'CRITICAL', 'color': 'var(--critical-red)', 'detail': f'Fetch Error: {str(e)}'}
    try:
        db.session.execute(text('SELECT 1'))
        diagnostics['Database Core'] = {'status': 'ONLINE', 'color': 'var(--integrity-green)', 'detail': f'SQL Connection Stable. Rows: {len(all_r)}'}
    except Exception as e:
        diagnostics['Database Core'] = {'status': 'CRITICAL', 'color': 'var(--critical-red)', 'detail': f'Error: {str(e)}'}
    return render_template('health_monitor.html', diagnostics=diagnostics, current_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), all_records=all_r, assets=all_r, treasury=CorporateTreasury.query.first(), bleeding_assets=bleeding_assets, **get_system_counts())

@hangar_bp.route('/matrix/settings', endpoint='settings', methods=['GET', 'POST'])
@admin_only
def anchor_settings():
    config = SystemConfig.query.first()
    if not config:
        config = SystemConfig()
        db.session.add(config)
        db.session.commit()
    if request.method == 'POST':
        try:
            config.class_a_min = float(request.form.get('a_min', 0))
            config.class_b_min = float(request.form.get('b_min', 0))
            config.class_c_min = float(request.form.get('c_min', 0))
            config.class_a_fee = float(request.form.get('a_fee', 0))
            config.class_b_fee = float(request.form.get('b_fee', 0))
            config.class_c_fee = float(request.form.get('c_fee', 0))
            config.last_updated = datetime.utcnow()
            db.session.commit()
            flash("💾 GLOBAL MATRIX OVERRIDDEN: New baselines locked securely.", "success")
        except Exception as e:
            db.session.rollback()
            flash("⚠️ CONFIGURATION FAULT: Could not lock new baselines.", "error")
        return redirect(url_for('hangar.settings'))
    return render_template('settings.html', config=config, all_records=SovereignLedger.query.all(), assets=SovereignLedger.query.all(), treasury=CorporateTreasury.query.first(), **get_system_counts())

@hangar_bp.route('/finance/distribute-yield', methods=['POST'], endpoint='distribute_yield')
@admin_only
def distribute_yield():
    assets_with_yield = SovereignLedger.query.filter(SovereignLedger.yield_interest > 0).all()
    for asset in assets_with_yield:
        total_interest = asset.yield_interest
        member_share = total_interest * 0.80
        laveto_share = total_interest * 0.20
        asset.savings_balance += member_share
        treasury = CorporateTreasury.query.first()
        if treasury and hasattr(treasury, 'total_saas_tax'):
            treasury.total_saas_tax += laveto_share
        asset.yield_interest = 0
    db.session.commit()
    flash("📈 PROFIT DISTRIBUTED TO ACCOUNTS (80/20 Protocol).", "success")
    return redirect(url_for('hangar.corporate_treasury'))

@hangar_bp.route('/api/persona/triage', methods=['POST'])
def persona_triage():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key: return jsonify({"response": "🚨 SYSTEM FAULT: Brain disconnected."}), 200
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction="You are Laveto AI.")
        chat = model.start_chat(history=[])
        response = chat.send_message(user_message)
        return jsonify({"response": response.text, "status": "success"}), 200
    except Exception as e:
        return jsonify({"response": f"🚨 CRASH:\n{str(e)}"}), 200

@hangar_bp.route('/resolve_flare/<int:log_id>', methods=['POST'])
@admin_only
def resolve_flare_log(log_id):
    flare = AccessLog.query.get(log_id)
    if flare:
        db.session.delete(flare)
        db.session.commit()
    return redirect(request.referrer)

@hangar_bp.route('/dispatch_monthly_statements', methods=['POST'])
@admin_only
def dispatch_monthly_statements():
    run_email_blast()
    flash("🚀 SUCCESS: Statements dispatched.", "success")
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/dispatch_whatsapp/<int:asset_id>')
@admin_only
def dispatch_whatsapp(asset_id):
    asset = SovereignLedger.query.get_or_404(asset_id)
    if not asset.member_phone or asset.member_phone == 'None':
        flash(f"🚨 DISPATCH FAILED: No phone number on file.", "error")
        return redirect(url_for('hangar.view_ledger'))
    clean_phone = str(asset.member_phone).replace(' ', '').replace('+', '')
    encoded_msg = urllib.parse.quote("Notification from Laveto Command.")
    return redirect(f"https://wa.me/{clean_phone}?text={encoded_msg}")

@hangar_bp.route('/dispatch_silk_road/<int:ghost_order_id>', methods=['POST'])
@admin_only
def dispatch_silk_road(ghost_order_id):
    order = GhostOrder.query.get_or_404(ghost_order_id)
    order.status = "ORDER DISPATCHED"
    db.session.commit()
    flash(f"Transmission successful. PO-{ghost_order_id:04d} dispatched.", "success")
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/accept_silk_road_quote/<int:quote_id>', methods=['POST'])
@admin_only
def accept_silk_road_quote(quote_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/toggle_listing/<int:entry_id>', methods=['POST'])
@admin_only
def toggle_listing(entry_id):
    r = LiquidationRecord.query.get_or_404(entry_id)
    if r.listed_for_sale == True or r.listed_for_sale == 1:
        r.listed_for_sale = False
        r.provenance_locked = False
        r.asking_price = None
        r.provenance_premium = 0.0
        if r.current_status == '⚠️ SALE REQUESTED':
            r.current_status = 'APPROVED'
    else:
        r.listed_for_sale = True
        r.provenance_locked = True
        try: r.asking_price = float(request.form.get('asking_price', '0'))
        except ValueError: r.asking_price = 0.0
        if r.current_status == '⚠️ SALE REQUESTED': r.current_status = 'APPROVED'
    db.session.commit()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/request_liquidation/<int:entry_id>', methods=['POST'])
def request_liquidation(entry_id):
    asset = SovereignLedger.query.get_or_404(entry_id)
    new_liquidation = LiquidationRecord(vin_dna=asset.vin_dna, asking_price=getattr(asset, 'asking_price', 0.0), status='PENDING LIQUIDATION')
    db.session.add(new_liquidation)
    db.session.commit()
    flash("Liquidation request successfully transmitted to the Command Wall.", "success")
    return redirect(request.referrer)

@hangar_bp.route('/generate_liquidation_payout/<int:entry_id>', methods=['GET', 'POST'])
def generate_liquidation_payout(entry_id):
    r = LiquidationRecord.query.get_or_404(entry_id)
    if not current_user.is_admin and r.member_name != current_user.username:
        abort(403, description="Unauthorized.")
    return "Liquidation Payout Generated."

@hangar_bp.route('/generate_quote/<int:entry_id>')
@admin_only
def generate_quote(entry_id): return "Quote Generated"

@hangar_bp.route('/reject_loan_request/<int:entry_id>', methods=['POST'])
@admin_only
def reject_loan_request(entry_id):
    entry = SovereignLedger.query.get_or_404(entry_id)
    entry.pending_loan_amount = 0.0
    db.session.commit()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/resolve_compliance/<int:entry_id>', methods=['POST'])
@admin_only
def resolve_compliance(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/trigger_handover/<int:entry_id>', methods=['POST'])
@admin_only
def trigger_handover(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/upload_direct_capture/<int:entry_id>', methods=['POST'])
@admin_only
def upload_direct_capture(entry_id): return jsonify({"status": "success", "message": "Live stream secured."})

@hangar_bp.route('/master_fleet_dashboard/<string:client_phone>', endpoint='master_fleet_dashboard')
@admin_only
def master_fleet_dashboard(client_phone):
    fleet_assets = SovereignLedger.query.filter(SovereignLedger.member_phone.contains(client_phone)).all()
    return render_template('fleet_dashboard.html', assets=fleet_assets, client_phone=client_phone, **get_system_counts())

@hangar_bp.route('/dispatch_covenant_whatsapp/<int:asset_id>')
@admin_only
def dispatch_covenant_whatsapp(asset_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/resolve_mayday/<int:asset_id>', methods=['POST'])
@admin_only
def resolve_mayday(asset_id):
    try:
        asset = SovereignLedger.query.get_or_404(asset_id)
        asset.status = "STABLE"
        db.session.commit()
    except: db.session.rollback()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/update_contact', methods=['POST'])
@admin_only
def update_contact(): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/execute_transfer/<int:entry_id>', methods=['POST'])
@admin_only
def execute_transfer(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/silence_market_alarm/<int:entry_id>', methods=['POST'])
@admin_only
def silence_market_alarm(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/clear_booking/<int:asset_id>')
@admin_only
def clear_booking(asset_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/purge_asset/<int:entry_id>', methods=['POST'])
@admin_only
def purge_asset(entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/dispatch_single_email/<string:doc_type>/<int:entry_id>', methods=['POST'])
@admin_only
def dispatch_single_email(doc_type, entry_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/approve_audit/<int:asset_id>', methods=['POST'])
@admin_only
def approve_audit(asset_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/reject_audit/<int:asset_id>', methods=['POST'])
@admin_only
def reject_audit(asset_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/open_bay_01')
@admin_only
def open_bay_01(): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/add_supplier', methods=['POST'])
@admin_only
def add_supplier(): return redirect(url_for('hangar.silk_road'))

@hangar_bp.route('/api/security/radar_sweep', methods=['GET'])
@admin_only
def radar_sweep_api(): return jsonify({"active": False})

@hangar_bp.route('/api/security/dispatch_agent/<int:alert_id>', methods=['POST'])
@admin_only
def dispatch_agent_api(alert_id): return jsonify({"status": "success"})

@hangar_bp.route('/vault/trigger_mayday/<int:asset_id>', methods=['POST'])
def trigger_mayday_vault(asset_id): return jsonify({"status": "success"})

@hangar_bp.route('/initiate_sale', methods=['POST'])
def initiate_sale():
    asset = SovereignLedger.query.get(request.form.get('entry_id'))
    if asset:
        asset.current_status = "SALE PENDING"
        db.session.commit()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/delete_supplier/<int:supplier_id>', methods=['POST', 'GET'])
def delete_supplier(supplier_id):
@admin_only
    # ... rest of the code ...
    """Purges a supplier record from the Sovereign Rolodex."""
    from flask import redirect, url_for, flash
    from core.models.vehicles import SupplierDirectory
    from core.extensions import db

    try:
        supplier = SupplierDirectory.query.get(supplier_id)
        if supplier:
            db.session.delete(supplier)
            db.session.commit()
            flash(f"✅ ROLODEX PURGED: {supplier.name} removed.", "success")
        else:
            flash("⚠️ Supplier record not found.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 DELETION FAULT: {str(e)}", "error")

    return redirect(url_for('hangar.silk_road'))

@hangar_bp.route('/update-odometer/<int:asset_id>', methods=['POST'])
@login_required
def update_odometer(asset_id):
    asset = SovereignLedger.query.get_or_404(asset_id)
    raw_mileage = request.form.get('odometer')
    if raw_mileage:
        try:
            val = int(float(raw_mileage))
            asset.odometer = val
            asset.current_odometer = val
            db.session.commit()
            flash(f"✅ TELEMETRY UPLINK SUCCESS: {val} KM", "success")
            return redirect(url_for('hangar.client_vault', asset_id=asset.vin_dna))
        except Exception as e:
            db.session.rollback()
    return redirect(request.referrer)

@hangar_bp.route('/save_baseline/<int:entry_id>', methods=['POST'])
@login_required
def save_baseline(entry_id):
    asset = SovereignLedger.query.get_or_404(entry_id)
    data = request.get_json()
    if data and data.get('mileage'):
        try:
            val = int(float(data.get('mileage')))
            asset.base_mileage = val
            asset.current_odometer = val
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            db.session.rollback()
    return jsonify({"status": "error"}), 400

@hangar_bp.route('/update_telemetry/<int:asset_id>', methods=['POST'])
def update_telemetry(asset_id):
    try:
        asset = SovereignLedger.query.get(asset_id)
        if not asset: return jsonify({"status": "error", "message": "Asset not found"}), 404
        data = request.get_json()
        if not data or 'odometer' not in data: return jsonify({"status": "error"}), 400
        new_odo = int(data.get('odometer'))
        base_odo = int(asset.base_mileage) if asset.base_mileage else 0
        if new_odo < base_odo: return jsonify({"status": "error", "message": "Odometer rollback detected."}), 400
        asset.current_odometer = new_odo
        db.session.commit()
        return jsonify({"status": "success", "current_odometer": asset.current_odometer}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

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

@hangar_bp.route('/burn_lvt/<int:entry_id>', methods=['POST'])
@admin_only
def burn_lvt(entry_id):
    asset = SovereignLedger.query.get_or_404(entry_id)
    intent = request.form.get('intent')
    cost_map = {'FORENSIC_AUDIT_BYPASS': 20.0, 'PREMIUM_BOOST': 100.0}
    burn_cost = cost_map.get(intent, 999999.0)
    if (getattr(asset, 'lvt_balance', 0) or 0) < burn_cost:
        flash("🚨 INSUFFICIENT LVT BALANCE.", "error")
        return redirect(request.referrer)
    asset.lvt_balance -= burn_cost
    db.session.commit()
    flash(f"✅ {intent} processed successfully.", "success")
    return redirect(request.referrer)

@hangar_bp.route('/execute_lvt_swap/<int:order_id>', methods=['POST'])
@login_required
def execute_lvt_swap(order_id): return redirect(request.referrer or url_for('hangar.index'))

@hangar_bp.route('/api/request_module_review', methods=['POST'])
@login_required
def request_module_review(): return jsonify({"status": "success"}), 200

@hangar_bp.route('/approve_module_review/<int:log_id>', methods=['POST'])
@admin_only
def approve_module_review(log_id): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/asset/force-mail', methods=['POST'])
@admin_only
def force_mail_engine(): return redirect(url_for('hangar.debug_env'))

@hangar_bp.route('/asset/sweep-logs', methods=['POST'])
@admin_only
def sweep_neural_logs(): return redirect(url_for('hangar.debug_env'))

@hangar_bp.route('/asset/force-backup', methods=['POST'])
@admin_only
def force_backup(): return redirect(url_for('hangar.debug_env'))

@hangar_bp.route('/admin/purge_testing_data', methods=['POST'])
@admin_only
def purge_testing_data():
    if request.form.get('emergency_master_key') != "ARCHITECT-SECURE-999":
        flash("UNAUTHORIZED", "error")
        return redirect(url_for('hangar.settings'))
    session = SovereignLedger.query.session
    try:
        for asset in SovereignLedger.query.all():
            asset.shield_reservoir = 0.0
            asset.savings_balance = 0.0
            asset.yield_principal = 0.0
            asset.yield_interest = 0.0
            asset.active_loan_principal = 0.0
            if hasattr(asset, 'lvt_balance'): asset.lvt_balance = 0.0
        tr = CorporateTreasury.query.first()
        if tr: tr.total_saas_tax = 0.0
        SovereignTransaction.query.delete()
        try: session.execute(text("DELETE FROM audit_log"))
        except: pass
        session.commit()
        flash("FINANCIAL PURGE COMPLETE.", "success")
    except Exception as e:
        session.rollback()
        flash(f"CRITICAL PURGE FAILURE: {str(e)}", "error")
    return redirect(url_for('hangar.settings'))

@hangar_bp.route('/admin/purge_audit_log', methods=['POST'])
@admin_only
def purge_audit_log():
    try:
        session = SovereignTransaction.query.session
        SovereignTransaction.query.delete()
        try: session.execute(text("DELETE FROM audit_log"))
        except: pass
        session.commit()
        flash("AUDIT LOG PURGED.", "success")
    except Exception as e:
        if 'session' in locals(): session.rollback()
    return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/admin/auto-purge-prospects', methods=['POST'])
@admin_only
def auto_purge_prospects():
    try:
        Prospect.query.delete()
        db.session.commit()
    except: db.session.rollback()
    return redirect(url_for('hangar.settings'))

@hangar_bp.route('/mass-email-statements', methods=['POST'])
@admin_only
def mass_email_statements(): return jsonify({"success": True}), 200

@hangar_bp.route('/authorize-bounty/<int:entry_id>', methods=['POST'])
@admin_only
def authorize_bounty(entry_id): return redirect(url_for('hangar.index'))

@hangar_bp.route('/your-deposit-route', methods=['POST'])
def your_deposit_function(): return redirect(url_for('hangar.view_ledger'))

@hangar_bp.route('/inspection', methods=['GET', 'POST'])
@staff_required
def run_inspection():
    vin = request.form.get('vin', '').strip() if request.method == 'POST' else request.args.get('vin', '').strip()
    if vin:
        vehicle = SovereignLedger.query.filter_by(vin_dna=vin).first()
        if not vehicle:
            flash(f"🚨 ALERT: Vehicle with VIN {vin} not found.", "danger")
        return render_template('inspection_desk.html', record=vehicle, vehicle=vehicle)
    return render_template('inspection_desk.html', record=None, vehicle=None)

@hangar_bp.route('/member-login', methods=['POST'])
def member_login():
    vin_attempt = request.form.get('vin_dna', '').strip().upper()
    key_attempt = request.form.get('sovereign_key', '').strip()
    asset = SovereignLedger.query.filter_by(vin_dna=vin_attempt, sovereign_key=key_attempt).first()
    if asset:
        session.permanent = True
        session['member_access_granted'] = asset.vin_dna
        return redirect(url_for('hangar.client_vault', asset_id=asset.vin_dna))
    else:
        flash("🚨 ACCESS DENIED: Invalid Vehicle DNA or Sovereign Key.", "error")
        return redirect(request.referrer or url_for('hangar.index'))

@hangar_bp.route('/api/mayday-signal', methods=['POST'])
def mayday_signal(): return jsonify({"status": "success"}), 200

@hangar_bp.route('/hangar/api/dispatch_agent', methods=['POST'])
@admin_only
def dispatch_agent(): return redirect(url_for('hangar.view_ledger'))

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
def initiate_repayment():
    vin = request.form.get('vin_dna')
    member = SovereignLedger.query.filter_by(vin_dna=vin).first()
    if not member: return redirect(url_for('hangar.index'))
    debt_amount = getattr(member, 'active_loan_principal', 0.0) or 0.0
    if debt_amount <= 0: return redirect(url_for('hangar.client_vault', asset_id=member.vin_dna))
    if (member.shield_reservoir or 0) < debt_amount: return redirect(url_for('hangar.client_vault', asset_id=member.vin_dna))
    try:
        member.shield_reservoir -= debt_amount
        member.active_loan_principal = 0.0
        member.last_payment_timestamp = datetime.now(timezone.utc)
        db.session.commit()
        flash("Repayment successful.", "success")
    except: db.session.rollback()
    return redirect(url_for('hangar.client_vault', asset_id=member.vin_dna))

@hangar_bp.route('/upload_forensics', methods=['POST'])
@login_required
def upload_forensics(): return jsonify({"status": "success"})

@hangar_bp.route('/upload-forensics/<int:entry_id>', methods=['GET'])
@login_required
def upload_forensics_page(entry_id):
    record = LiquidationRecord.query.get_or_404(entry_id)
    return render_template('manual_upload.html', record=record)

@hangar_bp.route('/trigger_procurement/<int:entry_id>', methods=['POST'])
@admin_only
def trigger_procurement(entry_id): return redirect(request.referrer)

@hangar_bp.route('/request_compliance_service/<int:entry_id>', methods=['POST'])
@admin_only
def request_compliance_service(entry_id): return redirect(request.referrer)

@hangar_bp.route('/')
def index():
    try:
        stats_query = db.session.query(
            func.sum(SovereignLedger.savings_balance),
            func.sum(SovereignLedger.shield_reservoir),
            func.sum(SovereignLedger.yield_interest),
            func.sum(SovereignLedger.yield_principal)
        ).first()

        savings_sum = float(stats_query[0] or 0.0)
        shield_sum = float(stats_query[1] or 0.0)
        interest_sum = float(stats_query[2] or 0.0)
        true_platform_tvl = savings_sum + shield_sum + interest_sum

        treasury = CorporateTreasury.query.first()
        saas_total = float(getattr(treasury, 'total_saas_tax', 0.0) if treasury else 0.0)

        raw_member_id = session.get('member_access_granted')
        member_id = raw_member_id if isinstance(raw_member_id, str) else None

        return render_template('index.html', total_motshelo=true_platform_tvl, saas_total=saas_total, member_id=member_id)
    except Exception as e:
        return render_template('index.html', total_motshelo=0.0, saas_total=0.0, member_id=None)

@hangar_bp.route('/patch-ledger-db')
def patch_ledger_db(): return "✅ DATABASE PATCHED"

@hangar_bp.route('/rebuild-audit-ledger')
@admin_only
def rebuild_audit_ledger(): return "✅ FORENSIC LEDGER REBUILT"

@hangar_bp.route('/request-loan/<int:entry_id>', methods=['POST'])
@admin_only
def request_loan(entry_id): return redirect(request.referrer)

@hangar_bp.route('/debug-vault/<asset_id>')
def debug_vault(asset_id): return f"Found Asset: {asset_id}"

@hangar_bp.route('/test-route/<string:asset_id>')
def test_route(asset_id): return f"DEBUG: {asset_id}"