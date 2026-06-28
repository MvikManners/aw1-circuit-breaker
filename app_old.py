# ==========================================
# 🏛️ LAVETO GOSPEL OS - MASTER CORE
# ==========================================

import os
import uuid
import urllib.parse
from datetime import datetime
from flask import Flask
from dotenv import load_dotenv
from flask_login import UserMixin
from sqlalchemy import func

# --- CORE ARCHITECTURAL IMPORTS ---
from core.extensions import db, migrate, mail, login_manager, csrf
from core.models.vehicles import SovereignLedger, PayrollMandate, VaultTransaction
from core.utils import send_laveto_email
from core.routes.auth import auth_bp
from core.routes.hangar import hangar_bp

# Standard Library Imports
import requests
from PIL import Image
from twilio.rest import Client as TwilioClient
import google.generativeai as genai

# --- INITIALIZATION ---
load_dotenv()
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# --- CONFIGURATION ---
app.config.update(
    SECRET_KEY='Laveto_Sovereign_OS_Master_Key_2026',
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    WTF_CSRF_SSL_STRICT=False,
    WTF_CSRF_TIME_LIMIT=86400,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_POOL_RECYCLE=280,
    SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True}
)

# Database Setup
db_user = os.getenv('DB_USER')
raw_pass = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
encoded_pass = urllib.parse.quote_plus(raw_pass) if raw_pass else ""
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{encoded_pass}@LavetoLab.mysql.pythonanywhere-services.com/{db_name}'

# Extensions
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

# Blueprint Registration
app.register_blueprint(auth_bp)
app.register_blueprint(hangar_bp, url_prefix='/hangar')

# --- MODELS FOR HANGAR PAYROLL ---
class PayrollCohort(db.Model):
    __tablename__ = 'payroll_cohorts'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    employee_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    signature_data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='PENDING_FORGE')

# --- IDENTITY PROTOCOL WELD ---
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='AGENT')
    payable_balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True) # Essential for UserMixin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AccessLog(db.Model):
    __tablename__ = 'access_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=func.now())
    vin_dna = db.Column(db.String(100), nullable=False, default='UNKNOWN')
    action = db.Column(db.String(255), nullable=False)

# AI & SECURITY PROTOCOLS
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
laveto_persona = (
    "You are the Laveto Gospel OS, the digital gateway to Hangar 01. "
    "Your mission is System Restoration. You treat vehicle issues as 'mechanical malware'."
)
ai_model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=laveto_persona)

vision_persona = (
    "You are the Laveto Forensic Vision System ('The Mirror'). "
    "Analyze the provided vehicle component image. Look strictly for 'mechanical malware'."
)
vision_model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=vision_persona)

# ☁️ GOOGLE DRIVE CORE ENGINE
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = '0AO4NRDoHSKuxUk9PVA'

# -------------------------------------------------------------------
# ☁️ GOOGLE DRIVE CORE ENGINE
# -------------------------------------------------------------------
def print_all_routes(app):
    print(f"{'Endpoint':<30} {'Methods':<20} {'Rule'}")
    print("-" * 80)
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.endpoint:<30} {methods:<20} {rule.rule}")


def get_drive_service():
    # Placeholder for actual google-auth and google-api-python-client logic
    return None

def upload_to_drive(file_path, filename, vin, member_name):
    try:
        service = get_drive_service()
        if not service: return None
        clean_name = member_name if member_name else "PENDING_FOUNDER"
        subfolder_name = f"[{vin}] - {clean_name}"
        return "https://drive.google.com/placeholder"
    except Exception as e:
        print(f"🚨 SHARED DRIVE UPLOAD ERROR: {e}")
        return None

def archive_drive_folder(vin, member_name):
    pass

def calculate_logistics_eta(routing_method):
    routing_map = {"Local Supplier (Gaborone)": 1, "Local Courier": 2, "Cross-Border Runner (RSA)": 4, "DHL Priority": 5, "FedEx Express": 7, "Sea Freight (Durban Port)": 35}
    return datetime.utcnow() + timedelta(days=routing_map.get(routing_method, 7))

def verify_image_integrity(file_path):
    try:
        img = Image.open(file_path)
        if b'Photoshop' in img.info.get('exif', b'') or b'Lightroom' in img.info.get('exif', b''): return False
    except Exception: pass
    return True

def get_laveto_vision_response(image_path):
    try: return vision_model.generate_content([Image.open(image_path), "Analyze this part."]).text
    except Exception as e: return "[FAIL] System Error: AI Vision Offline."

def get_laveto_ai_response(user_input):
    try: return ai_model.generate_content(user_input).text
    except Exception as e: return f"LAVETO DIAGNOSTICS OFFLINE // System Error: {str(e)}"

# 📡 TELEGRAM INTERCEPT PROTOCOL
TELEGRAM_TOKEN = "8635200479:AAGCIeRa_doRyHVH_tpj5WsKJZJsc-IZAqg"
TELEGRAM_CHAT_ID = "1054436202"

def fire_telegram_alert(message):
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}, timeout=5)
    except Exception: pass

def send_telegram_alert(message):
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception: pass

# 🔐 MYSQL CORE ENGINE CONFIGURATION
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

UPLOAD_FOLDER = os.path.join(base_dir, 'static')
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Laveto Admin', os.environ.get('MAIL_USERNAME'))

# --- INITIALIZATION & IDENTITY WELDS ---
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "🚨 UPLINK REQUIRED: Please authenticate to access the Hangar."

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='AGENT')
    payable_balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AccessLog(db.Model):
    __tablename__ = 'access_log'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    vin_dna = db.Column(db.String(100), nullable=False, default='UNKNOWN')
    action = db.Column(db.String(255), nullable=False)

class PriorityAlert(db.Model):
    __tablename__ = 'priority_alert'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    vin_dna = db.Column(db.String(100), nullable=False, default='UNKNOWN')
    contact_info = db.Column(db.String(255), nullable=False, default='UNKNOWN')
    status = db.Column(db.String(50), default='PENDING_ARCHITECT_REVIEW')

class Prospect(db.Model):
    __tablename__ = 'prospect'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    name = db.Column(db.String(100), nullable=False, default='UNKNOWN')
    contact_info = db.Column(db.String(255), nullable=False, default='UNKNOWN')
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='NEW_LEAD')

class SystemUpdate(db.Model):
    __tablename__ = 'system_update'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    version = db.Column(db.String(50), nullable=False, default='CORE-UPGRADE')
    description = db.Column(db.Text, nullable=False, default='Architecture synchronized.')
    author = db.Column(db.String(100), default='ARCHITECT')

class CorporateTreasury(db.Model):
    __tablename__ = 'corporate_treasury'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    description = db.Column(db.String(255), nullable=False, default='System Transaction')
    amount = db.Column(db.Float, nullable=False, default=0.0)
    transaction_type = db.Column(db.String(50), nullable=False, default='CREDIT')
    agent_id = db.Column(db.String(100), nullable=True, default='SYSTEM')

# 🚀 THE ANTI-WHALE ENGINE
def mint_lvt(ledger_id, amount):
    r = SovereignLedger.query.get(ledger_id)
    if not r:
        return False

    if (r.lvt_balance + amount) > 5000:
        excess = (r.lvt_balance + amount) - 5000
        r.lvt_balance = 5000
        db.session.add(AccessLog(
            vin_dna=r.vin_dna,
            action=f"🔥 AUTO-BURN: Velocity Limit hit. {excess:.2f} LVT burned."
        ))
    else:
        r.lvt_balance += amount

    db.session.commit()
    return True

def calculate_dynamic_yield_rate(treasury_reserve, total_active_supply):
    if total_active_supply <= 0:
        return 0.04
    ratio = treasury_reserve / total_active_supply
    if ratio > 0.5:
        return 0.12
    elif ratio > 0.2:
        return 0.08
    else:
        return 0.04

def get_daily_cipher():
    raw_string = f"{datetime.utcnow().strftime('%Y-%m-%d')}-{app.config['SECRET_KEY']}"
    return f"LVT-{hashlib.sha256(raw_string.encode()).hexdigest()[:8].upper()}"

def compress_and_save_evidence(file_obj, vin, component_name, member_name):
    if not file_obj or file_obj.filename == '':
        return None

    target_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'forensics')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{vin}_{secure_filename(component_name)}_{timestamp}.jpg"
    filepath = os.path.join(target_dir, filename)

    img = Image.open(file_obj)
    img = ImageOps.exif_transpose(img)
    img.thumbnail((1200, 1200), Image.LANCZOS)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(filepath, format="JPEG", quality=85)

    drive_link = upload_to_drive(filepath, filename, vin, member_name)
    if os.path.exists(filepath):
        os.remove(filepath)
    return drive_link if drive_link else None

def check_maturity_status(ledger_id):
    record = SovereignLedger.query.get(ledger_id)
    if not record:
        return "Error: Asset not found"

    thresholds = {'A': 5000.0, 'B': 3000.0, 'C': 1500.0}
    v_class = (record.vehicle_class or 'B').upper()
    target_threshold = thresholds.get(v_class, 3000.0)

    total_equity = (record.savings_balance or 0) + (record.shield_reservoir or 0)

    if total_equity < target_threshold:
        record.months_in_green = 0
        db.session.add(AccessLog(
            vin_dna=record.vin_dna,
            action=f"🚨 MATURITY LOST: Equity dropped to P{total_equity:,.2f}. System Hardening Re-Entry triggered."
        ))
        db.session.commit()
        return "Maturity Lost: System Hardening Initiated"

    return "Status Maintained"

# --- 🧱 CALCULATORS ---
def calculate_wallet_tier(current_balance, target_repair_cost):
    balance = current_balance or 0.0
    target = target_repair_cost if target_repair_cost and target_repair_cost > 0 else 5000.0
    progress_pct = min((balance / target) * 100, 100.0)
    if progress_pct < 30: return {'name': '🔴 IMMATURE', 'progress': progress_pct, 'color': 'var(--critical-red)', 'perk': 'Emergency Safety Repairs Only. Shield Building.', 'next_milestone': f"P{target * 0.30:,.2f} (Unlock Triage)"}
    elif progress_pct < 100: return {'name': '🟡 RIPENING', 'progress': progress_pct, 'color': 'var(--integrity-gold)', 'perk': 'Forensic Audit Unlocked. Big 10 Sourcing Active.', 'next_milestone': f"P{target:,.2f} (Full Sanctification)"}
    else: return {'name': '🟢 SANCTIFIED', 'progress': 100.0, 'color': 'var(--integrity-green)', 'perk': '100% Fully Funded. Ready for Hangar Intake.', 'next_milestone': 'MAINTAIN YIELD BALANCE'}

# --- 🧱 HARDENED ROLE-BASED ACCESS CONTROL (RBAC) ---
def architect_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("🚨 ACCESS DENIED: Identity verification required.", "error")
            return redirect(url_for('auth.login'))
        if current_user.role != 'ARCHITECT':
            db.session.add(AccessLog(vin_dna="SYSTEM", action=f"SECURITY BREACH: {current_user.username} attempted to access restricted Architect sector."))
            db.session.commit()
            flash("🚨 ACCESS DENIED: Architect clearance required.", "error")
            return redirect(url_for('view_ledger'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['ARCHITECT', 'AGENT']:
            flash("🚨 STAFF ACCESS REQUIRED.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_vault_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="LAVETO VAULT AUDIT RECORD", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    transactions = VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).all()

    for tx in transactions:
        line = f"{tx.timestamp} | Intent: {tx.intent} | Amount: {tx.amount} | Balance: {tx.running_balance}"
        pdf.cell(200, 10, txt=line, ln=True)

    report_path = "static/reports/latest_audit.pdf"
    pdf.output(report_path)
    return report_path

@app.route('/pulse-dry-run', methods=['GET'])
@login_required
def pulse_dry_run():
    if current_user.role != 'admin':
        abort(403)
    results = simulate_payroll_pulse()
    return "<pre>" + "\n".join(results) + "</pre>"

@app.route('/pulse-control', methods=['POST'])
@login_required
def pulse_control():
    try:
        msg = process_payroll_pulse()
        return jsonify({'status': 'success', 'message': msg})
    except Exception as e:
        error_details = traceback.format_exc()
        return jsonify({
            'status': 'error',
            'message': f"Pulse Crashed: {str(e)} \n\n Traceback: {error_details[:200]}"
        }), 500

@app.before_request
def make_session_permanent():
    session.permanent = True
    if 'member_access_granted' in session or current_user.is_authenticated:
        try: custom_timeout = int(session.get('vault_timeout', 15))
        except (ValueError, TypeError): custom_timeout = 15
        app.permanent_session_lifetime = timedelta(minutes=custom_timeout)
    else:
        app.permanent_session_lifetime = timedelta(hours=24)

@app.context_processor
def inject_global_badges():
    p, q, l, liq, c = 0, 0, 0, 0, 0
    try:
        if current_user.is_authenticated and current_user.role == 'ARCHITECT':
            p = GhostOrder.query.filter_by(status='PENDING ORDER').count()
            q = SovereignLedger.query.filter_by(current_status='AUDIT FAILED').count()
            l = SovereignLedger.query.filter(SovereignLedger.pending_loan_amount > 0).count()
            liq = SovereignLedger.query.filter_by(current_status='⚠️ SALE REQUESTED').count()
            c = SovereignLedger.query.filter_by(current_status='COMPLIANCE REQUESTED').count()
    except Exception: pass
    return dict(pending_silk_road=p, quarantine_count=q, loan_notifications=l, liquidation_requests=liq, compliance_requests=c)

# --- 📚 TRAINING SYLLABUS REGISTRY ---
TRAINING_MODULES = {
    "Philosophy": {
        "title": "WARDEN PHILOSOPHY",
        "content": "The Warden is the shield. This module covers the foundational ethics, strict adherence to protocol, and the psychological fortitude required to operate the Command Wall without bias or breach. A Warden must maintain complete detachment from personal interests when verifying assets."
    },
    "Forensic Auditing": {
        "title": "FORENSIC AUDITING",
        "content": "Trust nothing. Verify everything. This module covers advanced VIN tracing, receipt validation, mechanical discrepancy hunting, and protocols for spotting falsified ledger entries. Remember: If the metadata does not match the physical asset, the asset is compromised."
    },
    "Treasury Operations": {
        "title": "TREASURY OPERATIONS",
        "content": "Protect the capital. This module covers strict USDT transfer verification, payout escrow timelines, and balancing the payable ledger without bleeding operational funds. Ensure all disbursements are cross-referenced against the Sovereign Ledger before release."
    }
}
# --- 🛠 HANGAR OPERATIONS ---
@app.route('/api/get-module/<name>')
@login_required
def get_module(name):
    module_data = TRAINING_MODULES.get(name)
    if module_data:
        return {"title": module_data["title"], "content": module_data["content"]}
    return {"title": "ERROR", "content": "Module content not found in registry."}, 404

def get_bay_status():
    bays = {"BAY 01 (LIFT A)": {"status": "OPEN", "eta": None, "eta_date": datetime.min, "color": "var(--integrity-green)", "vin": None},
            "BAY 02 (LIFT B)": {"status": "OPEN", "eta": None, "eta_date": datetime.min, "color": "var(--integrity-green)", "vin": None},
            "BAY 03 (DIAGNOSTIC)": {"status": "OPEN", "eta": None, "eta_date": datetime.min, "color": "var(--integrity-green)", "vin": None}}

    try:
        active_assets = SovereignLedger.query.filter(SovereignLedger.bay_assignment.in_(bays.keys())).all()
        for asset in active_assets:
            bays[asset.bay_assignment]["status"] = "OCCUPIED (IN PROGRESS)"
            bays[asset.bay_assignment]["color"] = "var(--sanctified-blue)"
            bays[asset.bay_assignment]["vin"] = asset.vin_dna
            bays[asset.bay_assignment]["eta"] = "AWAITING TRIAGE"

        active_orders = GhostOrder.query.filter(GhostOrder.status != "DELIVERED TO BAY").all()
        for order in active_orders:
            bay_name = order.ledger.bay_assignment
            if bay_name in bays:
                eta_date = order.estimated_arrival or datetime.min
                if bays[bay_name]["status"] in ["OPEN", "OCCUPIED (IN PROGRESS)"] or eta_date > bays[bay_name].get('eta_date', datetime.min):
                    bays[bay_name]["status"] = "LOCKED (WAITING PARTS)"
                    if order.estimated_arrival:
                        days_left = (order.estimated_arrival - datetime.utcnow()).days
                        bays[bay_name]["eta"] = f"ETA {days_left} DAYS" if days_left > 0 else "LANDING TODAY"
                    else: bays[bay_name]["eta"] = "PENDING ORDER"
                    bays[bay_name]["eta_date"] = eta_date
                    bays[bay_name]["color"] = "var(--critical-red)"
                    bays[bay_name]["vin"] = order.ledger.vin_dna
    except Exception:
        pass
    return bays

# --- 📦 PROCUREMENT & SILK ROAD ---
def generate_laveto_po(order_id, vin, part_name, supplier_name, quantity=1):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, "LAVETO SYSTEM RESTORATION", ln=True, align='L')
    pdf.set_font("Courier", 'B', 10)
    pdf.set_text_color(156, 128, 82)
    pdf.cell(0, 10, "ZERO-TRUST VEHICLE SANCTUARY // GABORONE HUB", ln=True, align='L')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "OFFICIAL PURCHASE ORDER", ln=True, border='B')
    pdf.set_font("Courier", '', 11)
    pdf.ln(5)
    pdf.cell(50, 8, f"PO NUMBER:    LAV-SR-{order_id:04d}", ln=True)
    pdf.cell(50, 8, f"DATE ISSUED:  {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(50, 8, f"SUPPLIER:     {supplier_name.upper()}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "  SOVEREIGN ASSET DATA (TARGET VEHICLE)", ln=True, fill=True)
    pdf.set_font("Courier", 'B', 12)
    pdf.cell(0, 10, f"  VIN DNA: {vin}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(20, 10, "QTY", border=1, fill=True, align='C')
    pdf.cell(170, 10, "COMPONENT DESCRIPTION / OEM REQUIREMENT", border=1, fill=True, ln=True, align='C')
    pdf.set_font("Courier", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(20, 15, str(quantity), border=1, align='C')
    pdf.cell(170, 15, f" {part_name.upper()}", border=1, ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(156, 128, 82)
    pdf.cell(0, 6, "LAVETO PROCUREMENT PROTOCOLS:", ln=True)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "1. All components must be OEM or strictly equivalent Tier-1 quality.\n2. Invoice must reference PO Number: LAV-SR-{0:04d}.\n3. Unauthorized aftermarket substitutions will be rejected at Quarantine Check.\n4. Please reply to this transmission with confirmed wholesale pricing and ETA.".format(order_id))

    filename = f"LAVETO_PO_{order_id:04d}.pdf"
    pdf.output(filename)
    return filename

def dispatch_po_email(supplier_email, pdf_filename, order_id, vin):
    sender_email = "mvik1982@gmail.com"
    sender_password = "iiahomuauinmudiq"
    msg = EmailMessage()
    msg['Subject'] = f"LAVETO PRIORITY ORDER - VIN [{vin[-6:]}]"
    msg['From'] = f"Laveto Command <{sender_email}>"
    msg['To'] = supplier_email
    msg.set_content(f"System connected.\n\nAttention {supplier_email},\n\nAttached is an authorized Laveto System Restoration Purchase Order (PO: LAV-SR-{order_id:04d}).\nTarget Asset DNA: {vin}\n\nPlease review the attached manifest and reply to this secure transmission with your confirmed wholesale price and estimated time of delivery to the Gaborone Hub.\n\nRegards,\nVela\nManaging Director\nLaveto System Restoration")

    with open(pdf_filename, 'rb') as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=pdf_filename)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
    os.remove(pdf_filename)

def fetch_supplier_emails():
    try:
        mail_client = imaplib.IMAP4_SSL("imap.gmail.com")
        mail_client.login("laveto.parts@gmail.com", "your_16char_app_password")
        mail_client.select("inbox")
        status, messages = mail_client.search(None, "UNREAD")
        if not messages[0]: return []
        email_ids = messages[0].split()
        extracted_quotes = []
        for e_id in email_ids:
            res, msg_data = mail_client.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = msg.get("From")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                break
                            elif part.get_content_type() == "text/html" and not body:
                                body = part.get_payload(decode=True).decode(errors='ignore')
                    else: body = msg.get_payload(decode=True).decode(errors='ignore')
                    if body: extracted_quotes.append({"sender": sender, "body": body})
        return extracted_quotes
    except Exception as e:
        print(f"Silk Road Fetch Error: {e}")
        return []

def parse_quote_with_ai(raw_email_text):
    prompt = f"""You are the Laveto Silk Road AI Sentinel.
Extract data from this supplier email. Return ONLY a valid JSON object without any markdown formatting.
Keys required: "part_name", "part_number", "price_pula" (number only), "supplier_name", "lead_time_days" (number only).
If a value is missing, use null.

RAW EMAIL TEXT:
{raw_email_text}"""

    try:
        response = ai_model.generate_content(prompt)
        raw_text = response.text
        clean_text = raw_text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"🚨 AI Parsing Failure (API/Network): {e}")
        return None

def check_api_latency(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=3)
        latency = int((time.time() - start) * 1000)
        if response.status_code < 500: return "ONLINE", f"{latency}ms"
        else: return "DEGRADED", f"{latency}ms"
    except requests.exceptions.Timeout: return "TIMEOUT", ">3000ms"
    except requests.exceptions.RequestException: return "OFFLINE", "ERR"

# --- 💳 SOVEREIGN COVENANT ---
def dispatch_covenant_email(client_email, client_name, vin_dna, pdf_bytes):
    SENDER_EMAIL = "your.laveto.email@gmail.com"
    SENDER_PASSWORD = "your_app_password_here"
    if not client_email: return False
    msg = MIMEMultipart()
    msg['From'] = f"Laveto System Restoration <{SENDER_EMAIL}>"
    msg['To'] = client_email
    msg['Subject'] = f"LAVETO SOVEREIGN COVENANT - {vin_dna}"
    body = (
        f"Greetings {client_name},\n\n"
        f"Your Sovereign Covenant for asset [{vin_dna}] has been mathematically locked and formalized.\n\n"
        f"Please find your legally binding protocol attached to this encrypted transmission."
    )
    msg.attach(MIMEText(body, 'plain'))
    payload = MIMEBase('application', 'pdf')
    payload.set_payload(pdf_bytes)
    encoders.encode_base64(payload)
    payload.add_header('Content-Disposition', f'attachment; filename="Laveto_Covenant_{vin_dna}.pdf"')
    msg.attach(payload)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"🚨 SMTP TRANSMISSION FAULT: {e}")
        return False

# --- 🚀 PAYROLL PULSE ENGINE ---
def process_payroll_pulse():
    """Executes the 60/40 Split and updates tier progression."""
    active_mandates = PayrollMandate.query.filter_by(status="ACTIVE").all()
    processed_count = 0
    for mandate in active_mandates:
        sovereign = mandate.ledger
        amount = float(mandate.monthly_pledge or 0)
        sovereign.savings_balance = (sovereign.savings_balance or 0) + (amount * 0.60)
        sovereign.shield_reservoir = (sovereign.shield_reservoir or 0) + (amount * 0.40)
        sovereign.months_in_green = (sovereign.months_in_green or 0) + 1
        receipt = VaultTransaction(
            vin_dna=sovereign.vin_dna,
            intent="PAYROLL PULSE (60/40 SPLIT)",
            amount=amount,
            running_balance=(sovereign.savings_balance + sovereign.shield_reservoir),
            authorized_by="SYSTEM_PULSE_ENGINE"
        )
        db.session.add(receipt)
        mandate.last_pulsed_at = datetime.utcnow()
        processed_count += 1
    db.session.commit()
    return f"Pulse Reconciliation Complete: {processed_count} mandates processed."

def simulate_payroll_pulse():
    active_mandates = PayrollMandate.query.filter_by(status='ACTIVE').all()
    report = []
    for m in active_mandates:
        savings = m.monthly_pledge * 0.60
        shield = m.monthly_pledge * 0.40
        report.append(f"Member {m.employee_number}: Split {m.monthly_pledge} -> {savings} (Yield) / {shield} (Shield)")
    return report

def generate_vault_report():
    return VaultTransaction.query.order_by(VaultTransaction.timestamp.desc()).all()
def simulate_payroll_pulse():
    active_mandates = PayrollMandate.query.filter_by(status='ACTIVE').all()
    report = []

    for m in active_mandates:
        savings = m.monthly_pledge * 0.60
        shield = m.monthly_pledge * 0.40
        report.append(f"Member {m.employee_number}: Split {m.monthly_pledge} -> {savings} (Yield) / {shield} (Shield)")

    return report

@app.route('/admin/process_vault_pulse/<int:asset_id>', methods=['POST'])
@architect_required # Ensures strictly controlled admin access
def process_vault_pulse(asset_id):
    # 1. Get the asset and the amount the admin typed in
    asset = SovereignLedger.query.get_or_404(asset_id)
    amount_str = request.form.get('deposit_amount', 0)

    try:
        total_deposit = float(amount_str)
    except ValueError:
        flash("🚨 CRITICAL: Invalid deposit amount.", "error")
        return redirect(request.referrer)

    if total_deposit <= 0:
        flash("🚨 CRITICAL: Deposit must be greater than zero.", "error")
        return redirect(request.referrer)

    # 2. Execute the Gospel OS Math (5% Fee, then 60/40 Split of the Net)
    network_fee = total_deposit * 0.05
    net_capital = total_deposit - network_fee

    yield_allocation = net_capital * 0.60
    shield_allocation = net_capital * 0.40

    # 3. Inject the Capital into the Client's Vault Balances
    asset.savings_balance = (asset.savings_balance or 0) + yield_allocation
    asset.shield_reservoir = (asset.shield_reservoir or 0) + shield_allocation

    # 4. Generate the 4-Part Forensic Ledger Receipt
    receipts = [
        AccessLog(vin_dna=asset.vin_dna, action=f"📥 VAULT PULSE: Capital Injected (+P{total_deposit:,.2f})"),
        AccessLog(vin_dna=asset.vin_dna, action=f"⚙️ PROTOCOL: 5% Sanctification Fee Deducted (-P{network_fee:,.2f})"),
        AccessLog(vin_dna=asset.vin_dna, action=f"📈 YIELD ENGINE: 60% Routed to Active Equity (+P{yield_allocation:,.2f})"),
        AccessLog(vin_dna=asset.vin_dna, action=f"🛡️ SHIELD RESERVOIR: 40% Routed to Defensive Liquidity (+P{shield_allocation:,.2f})")
    ]
    try:
        db.session.add_all(receipts)
        db.session.commit()
        flash(f"✅ SYSTEM: P{total_deposit:,.2f} injected and Sovereign Split executed.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 DATABASE ERROR: {str(e)}", "error")

    # Warp the Admin straight back to the client's Vault
    return redirect(url_for('client_vault', asset_id=asset.id))

@app.route('/admin/process_repair_deduction/<int:asset_id>', methods=['POST'])
@architect_required # Ensures strictly controlled admin access
def process_repair_deduction(asset_id):
    # 1. Fetch the asset
    asset = SovereignLedger.query.get_or_404(asset_id)
    amount_str = request.form.get('deduct_amount', 0)
    repair_reason = request.form.get('repair_reason', 'Authorized Mechanical Intervention')

    try:
        deduction = float(amount_str)
    except ValueError:
        flash("🚨 CRITICAL: Invalid deduction amount.", "error")
        return redirect(request.referrer)

    if deduction <= 0:
        flash("🚨 CRITICAL: Amount must be greater than zero.", "error")
        return redirect(request.referrer)

    # 2. Check for Deficit
    if (asset.shield_reservoir or 0) < deduction:
        flash("⚠️ SHIELD DEFICIT: Deduction exceeds available Shield Capital. Account bridged.", "error")

    # 3. Deduct the capital from the Shield Reservoir
    asset.shield_reservoir = (asset.shield_reservoir or 0) - deduction

    # 4. Generate the Forensic Ledger Receipt
    receipt = AccessLog(
        vin_dna=asset.vin_dna,
        action=f"🛠️ SHIELD DEPLOYED: {repair_reason} (-P{deduction:,.2f})"
    )

    try:
        db.session.add(receipt)
        db.session.commit()
        flash(f"✅ SYSTEM: P{deduction:,.2f} Shield Capital deployed successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"🚨 DATABASE ERROR: {str(e)}", "error")

    return redirect(request.referrer)

@app.route('/admin/initialize-apprentice-table')
@architect_required
def initialize_apprentice_table():
    try:
        from core.models.finance import ApprenticeTraining
        ApprenticeTraining.__table__.create(db.engine)
        return "ApprenticeTraining table initialized!"
    except Exception as e:
        return f"Error: {e}"

@app.route('/approve_prospect_and_dispatch/<int:prospect_id>', methods=['POST'])
@architect_required
def approve_prospect_and_dispatch(prospect_id):
    prospect = Prospect.query.get_or_404(prospect_id)
    raw_hash = f"{prospect.vin_dna}-{prospect.full_name}-{datetime.utcnow()}-LAVETO"
    secure_hash = hashlib.sha256(raw_hash.encode()).hexdigest().upper()[:24]
    key = f"SOV-{secure_hash[:12]}"

    rendered_html = render_template('prospect_covenant_pdf.html',
                                    prospect=prospect,
                                    current_date=datetime.utcnow().strftime('%d %B %Y'),
                                    hash_id=secure_hash)
    try:
        options = {
            'page-size': 'A4', 'margin-top': '0mm', 'margin-right': '0mm', 'margin-bottom': '0mm', 'margin-left': '0mm',
            'encoding': "UTF-8", 'enable-local-file-access': None
        }
        pdf_bytes = pdfkit.from_string(rendered_html, False, options=options)
        target_email = getattr(prospect, 'email', None)
        if target_email: dispatch_covenant_email(target_email, prospect.full_name, prospect.vin_dna, pdf_bytes)

        existing_asset = SovereignLedger.query.filter_by(vin_dna=prospect.vin_dna).first()
        if not existing_asset:
            new_ledger = SovereignLedger(
                vin_dna=prospect.vin_dna,
                member_email=prospect.email or "triage@laveto.internal",
                member_phone=prospect.phone_number or "00000000",
                member_name=prospect.full_name,
                sovereign_key=key,
                vehicle_class=prospect.vehicle_class or 'B',
                membership_type=prospect.membership_type or 'INDIVIDUAL',
                corporate_cohort=prospect.corporate_cohort or 'BAY_01_INTAKE',
                funding_method=prospect.funding_method or 'EFT',
                monthly_commitment=prospect.monthly_pulse or 0.0,
                current_status='STABLE',
                vehicle_year=2026, vehicle_make='UNKNOWN', vehicle_model='UNKNOWN'
            )
            db.session.add(new_ledger)

        db.session.delete(prospect)
        db.session.add(AccessLog(vin_dna=prospect.vin_dna, action="COVENANT MINTED, COMMITTED TO LEDGER, QUEUE PURGED"))
        db.session.commit()

        flash("✅ Prospect Approved to Command Wall & Ledger Synchronized.", "success")
        current_filter = request.args.get('filter', 'ALL')
        return redirect(url_for('view_ledger', filter=current_filter))

    except Exception as e:
        db.session.rollback()
        return f"🚨 CRITICAL COVENANT SYSTEM FAULT: {str(e)}", 500
@app.route('/')
def index():
    try:
        results = SovereignLedger.query.all()
        t_m = sum((r.yield_principal or 0) + (r.yield_interest or 0) + (r.shield_reservoir or 0) for r in results)
        treasury = CorporateTreasury.query.first()
        saas_total = treasury.total_saas_tax if treasury else 0.0

        # FIX: Use the logged-in user's ID if available
        member_id = current_user.id if current_user.is_authenticated else None

        return render_template('index.html', total_motshelo=t_m, saas_total=saas_total, member_id=member_id)
    except Exception:
        return render_template('index.html', total_motshelo=0.0, saas_total=0.0)

@app.route('/your-endpoint-path')
def get_ledger_data():
    try:
        # Use .get() or manual checks to ensure no NoneTypes are passed to the template
        data = SovereignLedger.query.all()
        # Ensure you aren't passing raw None objects to your JSON response
        return jsonify([{'val': r.shield_reservoir or 0} for r in data])
    except Exception as e:
        # Instead of letting it crash, return a JSON error
        return jsonify({'error': 'Data processing failed', 'details': str(e)}), 500

@app.route('/manifesto')
def manifesto(): return render_template('manifesto.html')

@app.route('/registry')
def registry(): return render_template('registry.html', listings=SovereignLedger.query.order_by(SovereignLedger.date_created.desc()).all())

@app.route('/master_registry')
@architect_required
def master_registry(): return render_template('master_registry.html', assets=SovereignLedger.query.order_by(SovereignLedger.date_created.desc()).all())

@app.route('/silk-road')
def silk_road():
    user_vin = session.get('vin_dna', 'GUEST')
    is_architect = session.get('is_architect', False)

    # 1. Catch the target VIN from the URL (if the Admin clicked the red button)
    target_vin = request.args.get('vin', '')

    all_assets = SovereignLedger.query.all()
    rolodex_suppliers = SupplierDirectory.query.order_by(SupplierDirectory.date_added.desc()).all()

    return render_template('silk_road.html',
                           assets=all_assets,
                           user_vin=user_vin,
                           is_architect=is_architect,
                           total_tolls=0.0,
                           progress_pct=0,
                           suppliers=rolodex_suppliers,
                           target_vin=target_vin) # <-- We pass it to the template here

@app.route('/sync_silk_road')
@architect_required
def sync_silk_road():
    unread_emails = fetch_supplier_emails()
    if not unread_emails:
        flash("Silk Road: No new supplier transmissions detected in drop-zone.", "info")
        return redirect(url_for('silk_road'))
    success_count = 0
    for email_data in unread_emails:
        ai_data = parse_quote_with_ai(email_data['body'])
        if ai_data:
            try:
                new_entry = SilkRoadLedger(
                    supplier_name=ai_data.get('supplier_name') or email_data['sender'],
                    part_name=ai_data.get('part_name') or "UNKNOWN COMPONENT",
                    part_number=str(ai_data.get('part_number') or "N/A"),
                    price_pula=float(ai_data.get('price_pula') or 0.0),
                    lead_time_days=int(ai_data.get('lead_time_days') or 0)
                )
                db.session.add(new_entry)
                success_count += 1
            except Exception as e: print(f"🚨 Silk Road Ledger Write Error: {e}")
    db.session.commit()
    flash(f"🦾 SILK ROAD HARVEST COMPLETE: {success_count} quotes digitized by Gemini.", "success")
    return redirect(url_for('silk_road'))

@app.route('/notify_eft_transfer', methods=['POST'])
@login_required
def notify_eft_transfer():
    data = request.get_json()
    amount = data.get('amount')
    asset_id = data.get('asset_id')

    asset = SovereignLedger.query.get(asset_id)
    if not asset:
        return jsonify({'status': 'error', 'message': 'Asset not found'}), 404

    # Log the EFT claim to your AccessLog so you can see it on the Command Wall
    log_msg = f"💰 EFT CLAIM PENDING: {asset.member_name} claims to have sent P{amount}. Verify with bank."
    new_log = AccessLog(vin_dna=asset.vin_dna, action=log_msg)

    try:
        db.session.add(new_log)
        db.session.commit()

        # Optional: Add your WhatsApp sending logic here if you want an instant ping!

        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/dispatch_silk_road/<int:ghost_order_id>', methods=['POST'])
@architect_required
def dispatch_silk_road(ghost_order_id):
    order = GhostOrder.query.get_or_404(ghost_order_id)
    vin = order.ledger.vin_dna
    part_name = order.component_name
    supplier_email = request.form.get('supplier_email') or "supplier@example.com"
    supplier_name = request.form.get('supplier_name') or "Autozone RSA"
    try:
        pdf_file = generate_laveto_po(ghost_order_id, vin, part_name, supplier_name)
        dispatch_po_email(supplier_email, pdf_file, ghost_order_id, vin)
        order.status = "ORDER DISPATCHED"
        db.session.commit()
        flash(f"Transmission successful. PO-{ghost_order_id:04d} dispatched to {supplier_name}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"System Error during transmission: {str(e)}", "danger")
    return redirect(url_for('view_ledger'))

@app.route('/passport/<vin_dna>')
def public_passport(vin_dna):
    r = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    components = {c.name: c.grade for c in r.components}
    proofs = {p.category: p.photo_url for p in r.proofs}
    return render_template('passport.html', r=r, components=components, proofs=proofs)

@app.route('/bay-intake', methods=['GET', 'POST'])
def bay_intake():
    if request.method == 'POST':
        import random, string
        try:
            # 1. Generate a secure 6-character Sovereign Key for the member
            gen_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # 2. Extract and Map Form Data to the Database Model
            new_asset = SovereignLedger(
                vin_dna=request.form.get('vin_dna', '').upper(),
                sovereign_key=gen_key,
                member_name=request.form.get('member_name'),
                member_phone=request.form.get('member_phone'),
                member_email=request.form.get('member_email'),
                vehicle_year=request.form.get('vehicle_year'),
                vehicle_make=request.form.get('vehicle_make'),
                vehicle_model=request.form.get('vehicle_model'),
                vehicle_class=request.form.get('vehicle_class'),
                membership_type=request.form.get('membership_type', 'INDIVIDUAL'),
                corporate_cohort=request.form.get('corporate_cohort', ''),
                funding_method=request.form.get('funding_source', 'EFT'),
                monthly_commitment=float(request.form.get('monthly_pulse', 700.00)),
                current_status='AWAITING TRIAGE'
            )

            # 3. Commit to the Vault
            db.session.add(new_asset)
            db.session.commit()

            # 4. Flash Success with their generated Key
            flash(f"⚙️ ASSET DNA RECORDED. SOVEREIGN KEY: {gen_key}", "success")
            return redirect(url_for('view_ledger'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ DATABASE ERROR: {str(e)}", "error")
            return redirect(url_for('bay_intake'))

    return render_template('intake.html')
# --- Authentication & Dashboard Routes ---

@app.route('/fleet-login', methods=['POST'])
def fleet_login():
    clean_phone = request.form.get('fleet_phone', '').replace(' ', '').replace('+', '')
    clean_pin = request.form.get('fleet_pin', '').strip()
    if not clean_phone or not clean_pin:
        flash("🚨 ACCESS DENIED: Missing Phone or PIN.", "error"); return redirect(url_for('index'))
    matched_asset = SovereignLedger.query.filter(SovereignLedger.member_phone != None, SovereignLedger.member_phone.contains(clean_phone), SovereignLedger.fleet_pin == clean_pin).first()
    if matched_asset:
        db.session.add(AccessLog(vin_dna=matched_asset.vin_dna, action="FLEET_ACCOUNT_ACCESSED"))
        db.session.commit()
        return redirect(url_for('master_fleet_dashboard', client_phone=clean_phone))
    flash("🚨 ACCESS DENIED: Incorrect Phone Number or Fleet PIN.", "error")
    return redirect(url_for('index'))

@app.route('/fleet-dashboard/<string:client_phone>')
@login_required
def master_fleet_dashboard(client_phone):
    fleet_assets = SovereignLedger.query.filter(SovereignLedger.member_phone.contains(client_phone)).all()
    return render_template('fleet_dashboard.html', assets=fleet_assets, client_phone=client_phone)

@app.route('/payroll-matrix')
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
        return render_template('payroll.html', cohorts=cohorts)
    except Exception as e: return f"<h1 style='color:red; font-family:monospace;'>🚨 MATRIX LOGIC ERROR: {str(e)}</h1>"

# --- Operations & Telemetry ---

@app.route('/dispatch-single-email/<string:doc_type>/<int:entry_id>', methods=['POST'])
@login_required
def dispatch_single_email(doc_type, entry_id):
    if send_laveto_email(doc_type, entry_id, app.config, request.url_root):
        flash(f"✅ TRANSMISSION SUCCESSFUL.", "success")
    else:
        flash(f"🚨 EMAIL FAILURE: System could not reach the mail server.", "error")
    return redirect(url_for('view_ledger'))

@app.route('/member-check', methods=['GET', 'POST'])
def member_check():
    if request.method == 'POST':
        vin_input = re.sub(r'[^A-Z0-9\-_]', '', request.form.get('vin_dna', '').upper()).strip()
        key_input = re.sub(r'[^A-Z0-9\-_]', '', request.form.get('sovereign_key', '').upper()).strip()
        try: timeout_val = min(max(int(request.form.get('vault_timeout', 15)), 1), 15)
        except ValueError: timeout_val = 15

        matched_record = SovereignLedger.query.filter_by(vin_dna=vin_input, sovereign_key=key_input).first()
        if matched_record:
            session['member_access_granted'] = True
            session['vin_dna'] = matched_record.vin_dna
            session['vault_timeout'] = timeout_val
            db.session.add(AccessLog(vin_dna=matched_record.vin_dna, action=f"ACCOUNT_ACCESSED (Vault ID: {matched_record.id})"))
            db.session.commit()
            return redirect(url_for('client_vault', asset_id=matched_record.id))
        flash("ACCESS DENIED: Invalid VIN-DNA or Sovereign Key.", "error")
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/api/telemetry/sync/<int:entry_id>', methods=['POST'])
def sync_telemetry(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id)
    data = request.get_json()
    if not data or 'odometer' not in data: return jsonify({'status': 'error', 'message': 'No odometer data provided.'}), 400
    try:
        new_odo = int(data['odometer'])
        baseline = r.last_service_mileage or 0
        if new_odo < baseline: return jsonify({'status': 'error', 'message': f'Odometer cannot be lower than last service ({baseline} KM).'}), 400
        r.current_mileage = new_odo
        db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"TELEMETRY SYNC: {new_odo} KM"))
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Telemetry synchronized.'})
    except Exception as e: return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/trigger_procurement/<int:entry_id>', methods=['POST'])
def trigger_procurement(entry_id):
    asset = SovereignLedger.query.get(entry_id)
    if not asset: return jsonify({'status': 'error', 'message': 'Asset not found.'}), 404
    try:
        required_nodes = ["Dept of Transport: Annual Registration Disc", "Dept of Transport: Traffic Fine Clearance", "5W-30 Synthetic Grade Oil (5L)", "OEM Standard Oil Filter", "OEM Cabin Air Filter"]
        for node in required_nodes: db.session.add(GhostOrder(ledger_id=asset.id, component_name=node, grade=1, status="PENDING ORDER"))
        db.session.add(AccessLog(vin_dna=asset.vin_dna, action="ANNUAL COMPLIANCE & MAINTENANCE INITIATED"))
        db.session.commit()
        send_telegram_alert(f"📑 *PROCUREMENT INITIATED*\n\nVIN: {asset.vin_dna}\nClient: {asset.member_name or 'Unknown'}\n\nAnnual Maintenance orders sent to Procurement.")
        return jsonify({'status': 'success', 'message': 'Orders sent to Procurement.'})
    except Exception as e: db.session.rollback(); return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/trigger_flicker/<int:entry_id>', methods=['POST'])
def trigger_flicker(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id)
    gps_coords = request.get_json().get('gps_data', 'GPS UNAVAILABLE') if request.get_json() else 'GPS UNAVAILABLE'
    try:
        from core.models.vehicles import FlickerAlert
        db.session.add(FlickerAlert(ledger_id=r.id, gps_location=gps_coords))
    except Exception:
        pass

    db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"EMERGENCY ALERT | COORDS: {gps_coords}"))
    r.status = "EMERGENCY DISPATCH"
    db.session.commit()
    send_telegram_alert(f"🚨 *EMERGENCY ASSISTANCE REQUESTED*\n\nVIN: {r.vin_dna}\nLocation: {gps_coords}\n\n*Action Required:* Dispatch Agent immediately.")
    return jsonify({'status': 'success', 'message': "Alert received. Our team will contact you shortly."})

@app.route('/sentinel_upload/<int:entry_id>', methods=['POST'])
@staff_required
def sentinel_upload(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id)
    allowed_statuses = ['AWAITING PAYMENT', 'IN SERVICE', 'EMERGENCY DISPATCH', 'AUDIT FAILED', 'APPROVED', 'In Escrow', 'TRIAGE', 'AWAITING PROCUREMENT']
    if r.current_status not in allowed_statuses and not (r.current_status and str(r.current_status).startswith('BOOKED')):
        return jsonify({"status": "error", "message": f"🚨 ASSET LOCKED. Current: {r.current_status}"}), 403
    if r.provenance_locked: return jsonify({"status": "error", "message": "🚨 ACCOUNT LOCKED."})
    cat = request.form.get('category'); lat = request.form.get('lat'); lng = request.form.get('lng'); capture_time = request.form.get('capture_time')
    if 'file' not in request.files: return jsonify({"status": "error", "message": "🚨 NO IMAGE DETECTED."})
    f = request.files['file']
    try:
        if capture_time and capture_time != 'null':
            client_time = datetime.fromtimestamp(int(capture_time) / 1000)
            if (datetime.utcnow() - client_time) > timedelta(minutes=15): return jsonify({"status": "error", "message": "🚨 UPLOAD REJECTED: Photo is too old."})
        if not lat or not lng or lat == 'null': return jsonify({"status": "error", "message": "🚨 UPLOAD REJECTED: GPS location required."})
        ext = f.filename.rsplit('.', 1)[-1].lower(); safe_name = f"{r.vin_dna}_{cat.replace(' ', '')}_RAW_{int(datetime.utcnow().timestamp())}.{ext}"
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        f.save(local_path)
        if not verify_image_integrity(local_path):
            r.current_status = 'SPOOFED MALWARE'
            db.session.add(AccessLog(vin_dna=r.vin_dna, action="🚨 AI SENTINEL: PHOTOSHOP/TAMPER DETECTED"))
            db.session.commit()
            os.remove(local_path)
            return jsonify({"status": "error", "message": "🚨 SPOOFED MALWARE DETECTED. Image rejected."})
        vision_result = get_laveto_vision_response(local_path)
        db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"👁️ THE MIRROR [{cat}]: {vision_result}"))
        if "[FAIL]" in vision_result:
            r.current_status = 'AUDIT FAILED'
            db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"🚨 THE MIRROR REJECTED ASSET. Reason: {vision_result}"))
        if cat == 'The Swap':
            try:
                dx = (float(lng) - 25.9120) * 40000000 * math.cos((-24.6580 + float(lat)) * math.pi / 360) / 360
                dy = (float(lat) - -24.6580) * 40000000 / 360
                if math.sqrt(dx * dx + dy * dy) > 15000:
                    os.remove(local_path)
                    db.session.add(AccessLog(vin_dna=r.vin_dna, action="🚨 AI SENTINEL: GPS MISMATCH DETECTED (>15km)"))
                    db.session.commit()
                    return jsonify({"status": "error", "message": "🚨 GREEN LIGHT BLOCKED: GPS coordinates do not match the Hub (Distance > 15km)."})
            except Exception as e:
                db.session.add(AccessLog(vin_dna=r.vin_dna, action="🚨 AI SENTINEL: METADATA FLICKER - GPS CORRUPT"))
                db.session.commit()
                if os.path.exists(local_path): os.remove(local_path)
                return jsonify({"status": "error", "message": "🚨 METADATA FLICKER: Integrity check failed."})
        if getattr(r, 'agent_bounty_locked', 0) and r.agent_bounty_locked > 0 and getattr(r, 'agent_bounty_released', 0) == 0:
            release_amt = (r.agent_bounty_total or 0.0) * 0.50
            if release_amt > 0:
                r.agent_bounty_locked -= release_amt
                r.agent_bounty_released = (r.agent_bounty_released or 0.0) + release_amt
                if r.agent_assigned_id:
                    agent = User.query.get(r.agent_assigned_id)
                    if agent: agent.payable_balance = (agent.payable_balance or 0.0) + release_amt
                db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"💰 TRANCHE 1 UNLOCKED: P{release_amt:,.2f} released to Agent."))
        drive_link = upload_to_drive(local_path, safe_name, r.vin_dna, r.member_name)
        if drive_link and os.path.exists(local_path): os.remove(local_path)
        final_url = drive_link if drive_link else safe_name

        try:
            from core.models.vehicles import WorkOrderProof
            p = WorkOrderProof.query.filter_by(ledger_id=r.id, category=cat).first()
            if p: p.photo_url = final_url
            else: db.session.add(WorkOrderProof(ledger_id=r.id, photo_url=final_url, category=cat))
        except Exception:
            pass

        db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"PHOTO VERIFIED: {cat} | GPS: {lat},{lng}"))
        db.session.commit()
        all_cleared = {'Vehicle Profile', 'Identity', 'The Fault', 'The Swap', 'The Install', 'The Seating'}.issubset({proof.category for proof in r.proofs})
        return jsonify({"status": "success", "message": f"✅ {cat} SECURED IN CLOUD.", "all_cleared": all_cleared})
    except Exception as e: return jsonify({"status": "error", "message": f"🚨 UPLOAD ERROR: {str(e)}"})

@app.route('/trigger_handover/<int:entry_id>', methods=['POST'])
@staff_required
def trigger_handover(entry_id):
    rec = SovereignLedger.query.get_or_404(entry_id)
    if request.form.get('silence_test') == 'PASSED':
        rec.current_status = "COMPLETED"
        rec.is_locked = False
        if getattr(rec, 'agent_bounty_locked', 0) > 0:
            final_tranche = rec.agent_bounty_locked
            rec.agent_bounty_locked = 0.0
            rec.agent_bounty_released += final_tranche
            db.session.add(AccessLog(vin_dna=rec.vin_dna, action=f"BOUNTY RELEASED: Final 50% (P{final_tranche}) released to Agent. Silence Test Passed."))
        db.session.commit()
        flash(f"✅ SILENCE TEST PASSED. Asset {rec.vin_dna} Handed Over. Final Bounty Released.", "success")
    else: flash("🚨 HANDOVER FAILED. Asset requires further rectification.", "error")
    return redirect(url_for('view_ledger'))

@app.route('/release_funds/<int:entry_id>', methods=['POST'])
@staff_required
def release_funds(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id)
    if {'Vehicle Profile', 'Identity', 'The Fault', 'The Swap', 'The Install', 'The Seating'}.issubset({p.category for p in r.proofs}):
        r.current_status = "APPROVED"; released_amt = r.target_repair_cost; r.target_repair_cost = 0.0
        db.session.add(SovereignTransaction(ledger_id=r.id, type='PAYMENT_CLEARED', amount=released_amt, balance_after=0, intent='SERVICE COMPLETED'))
        db.session.commit()
        send_telegram_alert(f"✅ *APPROVED* — [{r.vin_dna}] — Payment & Escrow Cleared.")
        flash(f"✅ APPROVED — {r.vin_dna} — Payment Cleared", "success")
    else: flash("🚨 ERROR: Missing required photos.", "error")
    return redirect(url_for('view_ledger'))

@app.route('/management-login', methods=['GET', 'POST'])
@csrf.exempt
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('admin_id', '').strip()
        admin_key = request.form.get('admin_key', '').strip()
        if admin_id == "admin" and admin_key == "laveto2026":
            session.clear(); session['is_architect'] = True; session['member_access_granted'] = True; session['vin_dna'] = "ARCH-0000"; session.permanent = True
            return redirect(url_for('view_ledger'))
        else: flash("ACCESS DENIED: Unauthorized Signal.", "error")
    return render_template('management_login.html')

@app.route('/logout')
def logout():
    try:
        if current_user.is_authenticated: logout_user()
        session.pop('member_access_granted', None); session.pop('vault_timeout', None); session.pop('is_architect', None)
        flash("You have securely logged out of the Laveto OS.", "info")
    except Exception as e: print(f"Logout Error: {e}")
    return redirect(url_for('index'))

@app.route('/toggle_red_soil', methods=['POST'])
@architect_required
def toggle_red_soil():
    stability = SystemStability.query.first()
    if not stability:
        stability = SystemStability(red_soil_mode=True)
        db.session.add(stability)
    else: stability.red_soil_mode = not stability.red_soil_mode
    stability.last_toggled = datetime.utcnow()
    db.session.commit()
    flash(f"🔴 RED SOIL MODE {'ACTIVATED' if stability.red_soil_mode else 'DEACTIVATED'}.", "warning")
    return redirect(url_for('view_ledger'))

@app.route('/api/pulse')
@architect_required
def api_pulse():
    recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(10).all()
    logs_data = [{"time": log.timestamp.strftime('%H:%M:%S'), "vin": log.vin_dna, "action": log.action} for log in recent_logs]
    return jsonify({"pulse": logs_data})

@app.route('/api/emergency_halt', methods=['POST'])
def api_emergency_halt():
    try:
        db.session.add(SystemUpdate(version="CRITICAL ALERT", description="🛑 WARDEN TRIGGERED EMERGENCY HALT. Operations suspended."))
        db.session.add(AccessLog(vin_dna="SYSTEM", action="🛑 EMERGENCY HALT ACTIVATED BY AGENT"))
        db.session.commit()
        send_telegram_alert(f"🛑 *EMERGENCY HALT TRIGGERED*\n\nA Field Agent has pulled the Emergency Cord in Hangar 01.\n\n*Action:* Operations suspended. Admin intervention required immediately.")
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/verify-asset/<string:vin_dna>')
def client_dossier_public(vin_dna):
    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    return render_template('client_dossier.html', asset=asset, evidence_list=[])

@app.route('/view-ledger')
def view_ledger():
    from flask import redirect, url_for
    return redirect(url_for('hangar.view_ledger'))

@app.route('/api/resolve-flare/<int:flare_id>', methods=['POST'])
def resolve_flare(flare_id):
    flare = PriorityAlert.query.get_or_404(flare_id)
    flare.status = 'RESOLVED'
    db.session.add(AccessLog(vin_dna=flare.vin_dna, action="FLARE RESOLVED: Architect cleared the radar."))
    db.session.commit()
    flash(f"✔️ Flare for {flare.vin_dna} has been cleared from the radar.", "success")
    return redirect(url_for('view_ledger'))

@app.route('/upload_multi_marketplace/<int:entry_id>', methods=['POST'])
@architect_required
def upload_multi_marketplace(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id); files_uploaded = 0
    for i in ['1', '2', '3']:
        field_name = f'market_img_{i}'
        if field_name in request.files and request.files[field_name].filename != '':
            f = request.files[field_name]; ext = f.filename.rsplit('.', 1)[-1].lower()
            safe_name = f"HERO_{i}_{r.vin_dna}_{int(datetime.utcnow().timestamp())}.{ext}"
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
            f.save(local_path)
            vision_result = get_laveto_vision_response(local_path)
            db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"👁️ THE MIRROR [HERO {i}]: {vision_result}"))
            drive_link = upload_to_drive(local_path, safe_name, r.vin_dna, r.member_name)
            if drive_link and os.path.exists(local_path): os.remove(local_path)
            final_url = drive_link if drive_link else safe_name
            if i == '1': r.marketplace_image = final_url
            elif i == '2': r.marketplace_image_2 = final_url
            elif i == '3': r.marketplace_image_3 = final_url
            files_uploaded += 1
    db.session.commit(); flash(f"📸 {files_uploaded} PHOTOS SECURED & ANALYZED.", "success"); return redirect(url_for('view_ledger'))

@app.route('/admin/mass-yield', methods=['POST'])
@architect_required
def mass_yield_declaration():
    total_profit = float(request.form.get('total_profit', 0))
    if total_profit <= 0:
        flash("🚨 INVALID PROFIT AMOUNT.", "error")
        return redirect(url_for('view_ledger'))

    tr = CorporateTreasury.query.first()
    reserves = (tr.total_saas_tax + tr.total_sanctity_fees) if tr else 0
    total_lvt = db.session.query(func.sum(SovereignLedger.lvt_balance)).scalar() or 1

    dynamic_rate = calculate_dynamic_yield_rate(reserves, total_lvt)
    member_pool = total_profit * dynamic_rate
    architect_royalty = total_profit * 0.10

    all_nodes = SovereignLedger.query.all()
    if not all_nodes:
        flash("🚨 NO ACTIVE ACCOUNTS.", "warning")
        return redirect(url_for('view_ledger'))

    total_pool_stake = sum((node.yield_principal or 0) for node in all_nodes)
    if total_pool_stake <= 0:
        flash("🚨 TOTAL SAVINGS EMPTY.", "error")
        return redirect(url_for('view_ledger'))

    for node in all_nodes:
        if getattr(node, 'yield_interest', None) is None: node.yield_interest = 0.0
        payout = member_pool * ((node.yield_principal or 0) / total_pool_stake)
        if payout > 0:
            node.yield_interest += payout
            db.session.add(SovereignTransaction(
                ledger_id=node.id, type='INTEREST_ADDED', amount=payout,
                balance_after=node.yield_interest, intent=f'MONTHLY_PROFIT (RATE: {dynamic_rate*100}%)'
            ))

    if not tr:
        tr = CorporateTreasury(total_saas_tax=architect_royalty, total_sanctity_fees=0.0)
        db.session.add(tr)
    else: tr.total_saas_tax += architect_royalty

    db.session.commit()
    send_telegram_alert(f"📈 *PROFIT DISTRIBUTED*\n\nGross: P{total_profit:,.2f}\nRate Applied: {dynamic_rate*100}%")
    flash(f"📈 PROFIT DISTRIBUTED AT {dynamic_rate*100}% RATE.", "success")
    return redirect(url_for('view_ledger'))

@app.route('/api/system/stability-monitor')
@architect_required
def system_stability_monitor():
    try:
        tr = CorporateTreasury.query.first()
        reserves = (tr.total_saas_tax + tr.total_sanctity_fees) if tr else 0
        circulating_lvt = db.session.query(func.sum(SovereignLedger.lvt_balance)).scalar() or 1
        intrinsic_value = reserves / circulating_lvt
        state = "STABLE"
        if intrinsic_value < 0.5: state = "INFLATIONARY RISK"
        elif intrinsic_value > 2.0: state = "DEFLATIONARY PRESSURE"
        return jsonify({
            "spot_price_pula": round(intrinsic_value, 2), "total_reserves_pula": round(reserves, 2),
            "total_circulating_lvt": circulating_lvt, "system_state": state, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/corporate-treasury')
@architect_required
def corporate_treasury():
    results = SovereignLedger.query.all()
    tr = CorporateTreasury.query.first()
    if not tr:
        tr = CorporateTreasury(total_saas_tax=0.0, total_sanctity_fees=0.0)
        db.session.add(tr)
        db.session.commit()

    t_shield = sum(getattr(r, 'shield_reservoir', 0) or 0 for r in results)
    t_savings = sum(getattr(r, 'savings_balance', 0) or 0 for r in results)
    t_yield_i = sum(getattr(r, 'yield_interest', 0) or 0 for r in results)

    # 🟢 NEW: Calculation for the LVT Reserve
    t_lvt = sum(getattr(r, 'lvt_balance', 0.0) or 0.0 for r in results)

    committed_orders = GhostOrder.query.filter(GhostOrder.status.in_(['FUNDS CLEARED', 'IN TRANSIT', 'DELIVERED TO BAY'])).all()
    outflow = sum(getattr(o, 'wholesale_cost', 0.0) or 0.0 for o in committed_orders)
    gross = sum(cost if 'Dept of Transport' in (getattr(o, 'component_name', '') or '') else cost * 1.30 for o, cost in ((o, getattr(o, 'wholesale_cost', 0.0) or 0.0) for o in committed_orders))

    outstanding_orders = GhostOrder.query.filter_by(status='AWAITING FUNDS').all()
    outstanding = sum(o_cost if 'Dept of Transport' in (getattr(oo, 'component_name', '') or '') else o_cost * 1.30 for oo, o_cost in ((oo, getattr(oo, 'wholesale_cost', 0.0) or 0.0) for oo in outstanding_orders))

    arbitrage = gross - outflow
    margin = (arbitrage / gross * 100) if gross > 0 else 0.0

    return render_template(
        'corporate_treasury.html',
        treasury=tr,
        total_shield=t_shield,
        total_yield_interest=t_yield_i,
        total_yield_principal=t_savings,
        total_savings=t_savings,
        total_lvt=t_lvt,
        total_debt=sum(getattr(r, 'active_loan_principal', 0) or 0 for r in results),
        platform_tvl=t_shield + t_savings + t_yield_i,
        total_revenue=(tr.total_saas_tax or 0) + (tr.total_sanctity_fees or 0),
        gross=gross,
        outflow=outflow,
        arbitrage=arbitrage,
        margin=margin,
        outstanding=outstanding,
        recent_orders=committed_orders[-5:]
    )

@app.route('/command/dispatch-statement/<int:entry_id>')
@architect_required
def dispatch_statement(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id)
    orders = GhostOrder.query.filter_by(ledger_id=r.id).all()
    html_content = render_template('member_statement_pdf.html', r=r, orders=orders, now=datetime.now())
    try:
        options = {'page-size': 'A4', 'margin-top': '0in', 'margin-right': '0in', 'margin-bottom': '0in', 'margin-left': '0in', 'encoding': "UTF-8", 'no-outline': None}
        pdf = pdfkit.from_string(html_content, False, options=options)
        temp_filename = f"{r.vin_dna}_STATEMENT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        target_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'forensics')
        if not os.path.exists(target_dir): os.makedirs(target_dir)
        temp_path = os.path.join(target_dir, temp_filename)
        with open(temp_path, 'wb') as f: f.write(pdf)
        drive_link = upload_to_drive(temp_path, temp_filename, r.vin_dna, r.member_name)
        if os.path.exists(temp_path): os.remove(temp_path)
        if drive_link: db.session.add(AccessLog(vin_dna=r.vin_dna, action=f"PDF ARCHIVED: STATEMENT")); db.session.commit()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=Laveto_Statement_{r.vin_dna[-6:]}.pdf'
        return response
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path): os.remove(temp_path)
        flash("🚨 PDF ENGINE OFFLINE: Use 'Print to PDF' in your browser.", "warning")
        return html_content
# ==========================================
# ⚙️ THE MASS STATEMENT BATCH DISPATCH LOOPS (ALIGNED TO UNCOLLIDABLE PREFIX VECTORS)
# ==========================================
@app.route('/api/dispatch-statements', methods=['POST'])
@architect_required
def api_dispatch_statements():
    try:
        sender_email = "mvik1982@gmail.com"
        sender_password = "wmrkgdrdkosgfvhn"
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        active_clients = SovereignLedger.query.all()
        success_count = 0
        domain = request.url_root

        for client_asset in active_clients:
            if not client_asset.member_email or '@' not in str(client_asset.member_email): continue

            t_savings = float(getattr(client_asset, 'savings_balance', 0.0) or 0.0)
            t_shield = float(getattr(client_asset, 'shield_reservoir', 0.0) or 0.0)
            t_total_equity = t_savings + t_shield
            lvt_tokens = float(getattr(client_asset, 'lvt_balance', 0.0) or 0.0)

            orders = GhostOrder.query.filter_by(ledger_id=client_asset.id).all()
            html_content = render_template('member_statement_pdf.html', r=client_asset, orders=orders, now=datetime.now())
            options = {'page-size': 'A4', 'margin-top': '0in', 'margin-right': '0in', 'margin-bottom': '0in', 'margin-left': '0in', 'encoding': "UTF-8", 'no-outline': None}
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)

            msg = MIMEMultipart()
            msg['Subject'] = f"LAVETO // Official Account Statement - {client_asset.vin_dna}"
            msg['From'] = f"Laveto Command <{sender_email}>"
            msg['To'] = client_asset.member_email

            body_text = (
                f"Greetings {client_asset.member_name or 'Member'},\n\n"
                f"Your official Laveto Account Statement has been formalized and updated in the secure registry.\n\n"
                f"--- FINANCIAL PORTFOLIO SUMMARY ---\n"
                f"Account Health Standing : {client_asset.status}\n"
                f"Total Portfolio Equity  : P{t_total_equity:,.2f}\n"
                f" ├─ Savings Equity (60%): P{t_savings:,.2f}\n"
                f" └─ Maintenance Shield (40%): P{t_shield:,.2f}\n\n"
                f"Sovereign Asset Debt    : P{getattr(client_asset, 'active_loan_principal', 0.00) or 0.00:,.2f}\n"
                f"Ecosystem Utility (LVT) : {lvt_tokens:,.2f} LVT\n"
                f"------------------------------------\n\n"
                f"To review your real-time ledger diagnostics, Triple-Lock verifications, or visual telemetry feeds, access your secure live dashboard here:\n"
                f"{domain}verify-asset/{client_asset.vin_dna}\n\n"
                f"Securely Underwritten by,\n"
                f"Laveto Command\n"
                f"Gaborone Hub // Zero-Trust Vehicle Sanctuary"
            )
            msg.attach(MIMEText(body_text, 'plain'))

            pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"Laveto_Statement_{client_asset.vin_dna[-6:]}.pdf")
            msg.attach(pdf_attachment)

            server.send_message(msg)

            new_log = AccessLog(vin_dna=client_asset.vin_dna, action=f"EMAIL DISPATCHED: STATEMENT sent to {client_asset.member_email}")
            db.session.add(new_log)
            success_count += 1

        server.quit()
        db.session.commit()
        return jsonify({"status": "success", "message": f"Operation Successful. {success_count} Statements dispatched."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Critical Error: {str(e)}"}), 500

@app.route('/forge_payroll_mandate', methods=['POST'])
@login_required
def forge_payroll_mandate():
    try:
        config = SystemConfig.query.first()
        sovereign = current_user.sovereign_ledger

        raw_pledge = request.form.get('monthly_pledge')
        if not raw_pledge:
            flash("Error: Pledge amount is required.", "error")
            return redirect(url_for('client_vault'))

        pledge = float(raw_pledge)
        vehicle_class = sovereign.vehicle_class

        min_limit = config.class_a_min if vehicle_class == 'A' else config.class_c_min
        if pledge < min_limit:
            flash(f"Mandate Rejected: Pledge {pledge} is below class {vehicle_class} floor limit.", "error")
            return redirect(url_for('client_vault'))

        new_mandate = PayrollMandate(
            sovereign_id=sovereign.id,
            employer=request.form.get('employer', 'Government of Botswana'),
            department=request.form.get('department'),
            omang_number=request.form.get('omang_number'),
            employee_number=request.form.get('employee_number'),
            monthly_pledge=pledge,
            status="ACTIVE"
        )

        db.session.add(new_mandate)
        log = AccessLog(user_id=current_user.id, action=f"Forged Payroll Mandate: {pledge}")
        db.session.add(log)
        db.session.commit()
        flash("Payroll Mandate Forged Successfully.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Forge Failure: {str(e)}")
        flash("System error during mandate forgery. Check logs.", "error")
    return redirect(url_for('client_vault'))

@app.route('/mint-saas-tax', methods=['POST'])
@architect_required
def mint_saas_tax():
    amt = float(request.form.get('amount', 0)); action = request.form.get('action'); tr = CorporateTreasury.query.first()
    if not tr: tr = CorporateTreasury(total_saas_tax=0.0, total_sanctity_fees=0.0); db.session.add(tr)
    if action == 'ADD': tr.total_saas_tax += amt
    elif action == 'SUBTRACT': tr.total_saas_tax = max(0, tr.total_saas_tax - amt)
    tr.last_updated = datetime.utcnow(); db.session.commit(); flash(f"🏛️ TREASURY UPDATED.", "success"); return redirect(url_for('corporate_treasury'))

@app.route('/execute_transfer/<int:entry_id>', methods=['POST'])
@architect_required
def execute_transfer_ownership(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id); r.transfer_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)); r.provenance_locked = True
    db.session.commit(); return redirect(url_for('view_ledger'))

@app.route('/claim_sovereignty', methods=['POST'])
@architect_required
def claim_sovereignty_payout():
    vin_input = re.sub(r'[^A-Z0-9\-_]', '', request.form.get('vin_dna', '').upper()); key_input = re.sub(r'[^A-Z0-9\-_]', '', request.form.get('transfer_key', '').upper())
    r = SovereignLedger.query.filter_by(transfer_key=key_input).first()
    if r:
        r.member_email = request.form.get('new_email'); r.transfer_key = None
        db.session.commit()
    return redirect(url_for('view_ledger'))

@app.route('/toggle-listing/<int:entry_id>', methods=['POST'])
@architect_required
def toggle_listing_status(entry_id):
    r = SovereignLedger.query.get_or_404(entry_id)
    r.listed_for_sale = not getattr(r, 'listed_for_sale', False)
    db.session.commit()
    return redirect(url_for('view_ledger'))

@app.route('/generate_quote/<int:entry_id>')
@architect_required
def generate_quote(entry_id):
    asset = SovereignLedger.query.get_or_404(entry_id)
    return f"Estimate Engine Rendered for {asset.vin_dna}"

@app.route('/generate_decree/<int:entry_id>')
@architect_required
def generate_decree(entry_id):
    asset = SovereignLedger.query.get_or_404(entry_id)
    return f"Sovereign Decree Locked for {asset.vin_dna}"

@app.route('/generate_settlement_pdf/<string:vin_dna>')
def generate_settlement_pdf(vin_dna):
    return f"Settlement Pipeline Active for {vin_dna}"

@app.route('/generate_liquidation_payout/<int:entry_id>')
@architect_required
def generate_liquidation_payout(entry_id):
    return f"Liquidation Ledger Sealed for ID {entry_id}"

@app.route('/admin_dashboard')
@architect_required
def admin_dashboard():
    return render_template('admin_dashboard.html', telemetry={})

@app.route('/dossier/<string:vin_dna>')
@app.route('/client-dossier/<string:vin_dna>')
def client_dossier(vin_dna):
    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    return render_template('client_dossier.html', asset=asset, evidence_list=[])

@app.route('/authorize_restoration/<vin_dna>', methods=['POST'])
def authorize_restoration(vin_dna):
    asset = SovereignLedger.query.filter_by(vin_dna=vin_dna).first_or_404()
    asset.current_status = 'AWAITING PROCUREMENT'
    db.session.commit()
    return redirect(url_for('client_dossier', vin_dna=vin_dna))

@app.route('/client-vault/<string:asset_id>', methods=['GET', 'POST'])
@login_required
def client_vault(asset_id):
    from flask import abort
    asset = SovereignLedger.query.filter(func.lower(SovereignLedger.vin_dna) == func.lower(str(asset_id))).first()
    if not asset and str(asset_id).isdigit():
        asset = SovereignLedger.query.get(int(asset_id))
    if not asset: abort(404)
    db.session.refresh(asset)
    treasury = CorporateTreasury.query.first()
    all_records = SovereignLedger.query.all()
    creation_date = getattr(asset, 'created_at', None) or getattr(asset, 'timestamp', datetime.utcnow())
    if creation_date.tzinfo is None: creation_date = creation_date.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    days_active = (now_utc - creation_date).days
    return render_template('client_vault.html', r=asset, asset=asset, proofs={}, components={}, market_orders=[], days_active=days_active, now=now_utc, all_records=all_records, treasury=treasury)

@app.route('/process-stacked-pulse/<int:entry_id>', methods=['POST'])
def process_stacked_pulse(entry_id):
    record = SovereignLedger.query.get_or_404(entry_id)
    payment_amount = float(request.form.get('total_payment', 0))
    record.savings_balance = (record.savings_balance or 0) + (payment_amount * 0.6)
    record.shield_reservoir = (record.shield_reservoir or 0) + (payment_amount * 0.4)
    db.session.commit()
    return redirect(url_for('view_ledger'))

@app.route('/dispatch-whatsapp/<int:asset_id>')
@login_required
def dispatch_whatsapp(asset_id):
    asset = SovereignLedger.query.get_or_404(asset_id)
    return redirect(f"https://wa.me/{asset.member_phone}")

@app.route('/add-supplier', methods=['POST'])
@architect_required
def add_supplier():
    name = request.form.get('supplier_name', '').strip()
    if name:
        db.session.add(SupplierDirectory(name=name))
        db.session.commit()
    return redirect(url_for('silk_road'))

@app.route('/admin/forge-genesis-warden')
def forge_genesis_warden():
    try:
        if not User.query.filter_by(username="WARDEN-01").first():
            genesis_warden = User(username="WARDEN-01", role="WARDEN")
            genesis_warden.set_password("Alpha2026!")
            db.session.add(genesis_warden)
            db.session.commit()
        return "✅ Genesis Warden Forged."
    except Exception as e: return str(e)
# ==========================================
# ⚙️ ADMINISTRATIVE NUCLEAR FORGE & IDENTITY PROTOCOLS
# ==========================================

@app.route('/weld-db')
@architect_required
def weld_db():
    try:
        db.session.execute(db.text('ALTER TABLE sovereign_ledger ADD COLUMN interest_earned FLOAT DEFAULT 0.0'))
        db.session.commit()
        return "✅ DB WELD SUCCESS!"
    except Exception as e: return str(e)

@app.route('/launch_flare', methods=['POST'])
def launch_flare():
    try:
        vin_input = request.form.get('vin_dna', 'UNKNOWN').strip()
        contact_input = request.form.get('contact_info', 'UNKNOWN').strip()

        new_flare = PriorityAlert(vin_dna=vin_input, contact_info=contact_input)
        db.session.add(new_flare)
        db.session.add(AccessLog(vin_dna=vin_input, action="PRIORITY FLARE LAUNCHED FROM PUBLIC INDEX"))
        db.session.commit()

        send_telegram_alert(f"🚨 *PRIORITY FLARE*\n\nTarget VIN: {vin_input}\nContact: {contact_input}\n\n*Action:* Architect review required.")
        flash("🚨 Priority Flare Launched. Laveto Command has been notified.", "success")
    except Exception as e:
        flash("System Error while launching flare.", "error")

    return redirect(url_for('index'))

@app.route('/forge-admin')
def forge_admin():
    import os
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_pass = os.getenv('ADMIN_PASSWORD', 'laveto2026')
        new_admin = User(username='admin', role='ADMIN')
        new_admin.set_password(admin_pass)
        db.session.add(new_admin)
        db.session.commit()
        return "✅ COMMANDER OVERRIDE: 'admin' identity forged successfully. Return to /login and establish uplink."
    return "⚠️ IDENTITY EXISTS: 'admin' is already in the database. Return to /login."

# --- CLEARANCE ELEVATION PROTOCOL ---
@app.route('/upgrade-architect')
def upgrade_architect():
    try:
        user = User.query.filter_by(username='admin').first()
        if user:
            user.role = 'ARCHITECT'
            db.session.commit()
            return "✅ OVERRIDE ACCEPTED: Clearance elevated to ARCHITECT. The Ledger is unlocked."
        return "⚠️ Identity not found. Forge the identity first."
    except Exception as e:
        return f"Database error: {str(e)}"

# --- NUCLEAR DATABASE FORGES ---
@app.route('/nuclear-prospect')
def nuclear_prospect():
    try:
        db.session.execute(db.text("DROP TABLE IF EXISTS prospect"))
        db.session.commit()
        Prospect.__table__.create(db.engine)
        return "✅ NUCLEAR FORGE SUCCESS: Old prospect table obliterated. New blueprint forged. The Ledger is ready."
    except Exception as e:
        return f"🚨 NUCLEAR FORGE FAILED: {str(e)}"

@app.route('/nuclear-update')
def nuclear_update():
    try:
        db.session.execute(db.text("DROP TABLE IF EXISTS system_update"))
        db.session.commit()
        SystemUpdate.__table__.create(db.engine)
        return "✅ NUCLEAR FORGE SUCCESS: Old SystemUpdate table obliterated. New blueprint forged. The memory is secure."
    except Exception as e:
        return f"🚨 NUCLEAR FORGE FAILED: {str(e)}"

@app.route('/nuclear-treasury')
def nuclear_treasury():
    try:
        db.session.execute(db.text("DROP TABLE IF EXISTS corporate_treasury"))
        db.session.commit()
        CorporateTreasury.__table__.create(db.engine)
        return "✅ NUCLEAR FORGE SUCCESS: Old CorporateTreasury table obliterated. New blueprint forged. The vault is secure."
    except Exception as e:
        return f"🚨 NUCLEAR FORGE FAILED: {str(e)}"

@app.route('/nuclear-stability')
def nuclear_stability():
    try:
        db.session.execute(db.text("DROP TABLE IF EXISTS system_stability"))
        db.session.commit()
        SystemStability.__table__.create(db.engine)
        return "✅ NUCLEAR FORGE SUCCESS: Old SystemStability table obliterated. New blueprint forged. The core is stable."
    except Exception as e:
        return f"🚨 NUCLEAR FORGE FAILED: {str(e)}"

@app.route('/nuclear-ghost')
def nuclear_ghost():
    try:
        db.session.execute(db.text("DROP TABLE IF EXISTS ghost_order"))
        db.session.commit()
        GhostOrder.__table__.create(db.engine)
        return "✅ NUCLEAR FORGE SUCCESS: Old GhostOrder table obliterated. New blueprint forged. The shadows are secured."
    except Exception as e:
        return f"🚨 NUCLEAR FORGE FAILED: {str(e)}"

# --- OMEGA OVERRIDE: MASTER IDENTITY ---
@app.route('/omega-override')
def omega_override():
    from core.models.actors import User
    from core.extensions import db
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin', role='ARCHITECT')
            user.set_password('laveto2026')
            db.session.add(user)
            db.session.commit()
            return "✅ OMEGA FORGE SUCCESS: Identity created. UPLINK ID: admin | PASSPHRASE: laveto2026"

        user.role = 'ARCHITECT'
        user.set_password('laveto2026')
        db.session.commit()
        return "✅ OMEGA UPGRADE SUCCESS: Clearance elevated to ARCHITECT. Passphrase reset to: laveto2026"
    except Exception as e:
        return f"🚨 OMEGA FAILED: {str(e)}"

# 🏁 FLASK EXECUTION LAUNCHER
if __name__ == '__main__':
    app.run(debug=True)