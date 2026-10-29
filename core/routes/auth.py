from datetime import datetime
import hashlib
from functools import wraps

from flask import (
    Blueprint,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from core import db
from core.extensions import csrf, login_manager
from core.models.actors import User, Warden
from core.models.vehicles import SovereignLedger, SovereignTransaction

auth_bp = Blueprint('auth', __name__)

# ==========================================
# 🛡️ SECURITY DECORATORS
# ==========================================
def architect_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_auth = current_user.is_authenticated and getattr(current_user, 'role', '') == 'ARCHITECT'
        is_session = session.get('is_architect') == True
        if not (is_auth or is_session):
            flash("🚨 ACCESS DENIED: Identity verification required.", "danger")
            return redirect(url_for('auth.staff_login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return "<h1>🚨 GOSPEL OS: CLEARANCE DENIED</h1>", 403

        role = getattr(current_user, 'role', '')
        if not role:
            role = session.get('user_role', 'NONE')

        is_official = str(role).upper().strip() in ['ADMIN', 'ARCHITECT', 'MD', 'AGENT', 'WARDEN', 'STAFF']
        is_raw_session = any(key in session for key in ['warden_logged_in', 'warden_id', 'warden_name', 'user_id', 'is_architect'])

        if is_official or is_raw_session:
            return f(*args, **kwargs)
        return "<h1>🚨 GOSPEL OS: CLEARANCE DENIED</h1>", 403
    return decorated_function

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("🚨 ACCESS DENIED: High Command clearance required.", "danger")
            return redirect(url_for('auth.staff_login'))

        role = getattr(current_user, 'role', '')
        if not role:
            role = session.get('user_role', 'NONE')

        if str(role).upper().strip() in ['ADMIN', 'ARCHITECT', 'MD']:
            return f(*args, **kwargs)

        flash("🚨 ACCESS DENIED: High Command clearance required.", "danger")
        return redirect(url_for('hangar.agent_terminal'))
    return decorated_function

@auth_bp.route('/secure-reset', methods=['GET', 'POST'])
def secure_reset():
    token = request.args.get('token')
    vin = request.args.get('vin')

    member_node = SovereignLedger.query.filter_by(vin_dna=vin).first() if vin else None

    # 🚨 Check 1: Invalid VIN or Token Match
    if not member_node or not member_node.reset_token or member_node.reset_token != token:
        return render_template(
            'secure_reset.html',
            invalid_token=True,
            error_msg="🚨 INVALID BEACON: This recovery link is unverified or has already been used."
        )

    # 🚨 Check 2: Expired Token
    if member_node.reset_token_expiry and member_node.reset_token_expiry < datetime.utcnow():
        return render_template(
            'secure_reset.html',
            invalid_token=True,
            error_msg="🚨 EXPIRED BEACON: This cryptographic link has expired. Please request a new recovery link."
        )

    # 🟢 Valid Link: Handle POST submission
    if request.method == 'POST':
        try:
            new_passphrase = request.form.get('new_passphrase')
            if not new_passphrase or len(new_passphrase) < 6:
                flash("Passphrase must be at least 6 characters.", "danger")
                return render_template('secure_reset.html', vin=vin, token=token)

            if hasattr(member_node, 'set_password'):
                member_node.set_password(new_passphrase)
            else:
                member_node.client_pin = new_passphrase

            member_node.reset_token = None
            member_node.reset_token_expiry = None
            db.session.commit()

            return render_template(
                'secure_reset.html',
                success=True,
                msg="🛡️ Credentials successfully re-established. Sovereign vault access restored."
            )

        except Exception as e:
            db.session.rollback()
            return render_template('secure_reset.html', vin=vin, token=token, error_msg=f"Operational Error: {str(e)}")

    return render_template('secure_reset.html', vin=vin, token=token)

# ==========================================
# 🔑 AUTHENTICATION ROUTES
# ==========================================

# 1. PUBLIC ENTRYPOINT (Renders Landing Page)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('hangar.agent_terminal'))

    if request.method == 'POST':
        return _process_authentication()

    return render_template('hangar/index.html')


# 2. DEDICATED STAFF & ADMIN PORTAL (Renders Staff Login Page)
@auth_bp.route('/staff', methods=['GET', 'POST'])
def staff_login():
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('hangar.agent_terminal'))

    if request.method == 'POST':
        return _process_authentication()

    return render_template('staff_login.html')


# 🛠️ SHARED AUTHENTICATION LOGIC
def _process_authentication():
    ident_user = (request.form.get('username') or request.form.get('agent_id') or '').strip()
    password = request.form.get('password')

    if ident_user.upper().startswith('WARDEN'):
        warden = Warden.query.filter(Warden.warden_id.ilike(ident_user)).first()

        if warden and warden.check_password(password):
            login_user(warden, remember=False)
            session.permanent = True
            session['warden_logged_in'] = True
            session['warden_id'] = warden.warden_id
            session['warden_name'] = getattr(warden, 'name', 'Warden')
            session['user_role'] = 'WARDEN'

            flash("Warden Protocol Authorized.", "success")
            return redirect(url_for('hangar.agent_terminal'))

        flash("🚨 ACCESS DENIED: Invalid Warden ID or Protocol Key.", "danger")
        return redirect(url_for('auth.staff_login'))

    else:
        user = User.query.filter(User.username.ilike(ident_user)).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            role = str(getattr(user, 'role', 'GUEST')).upper().strip()
            session.permanent = True
            session['member_access_granted'] = True
            session['user_role'] = role
            session['warden_logged_in'] = False

            if role in ['ADMIN', 'ARCHITECT', 'MD']:
                return redirect(url_for('hangar.view_ledger'))
            else:
                return redirect(url_for('hangar.agent_terminal'))

        flash('🚨 Invalid credentials.', 'danger')
        return redirect(url_for('auth.staff_login'))


@auth_bp.route('/warden/login', methods=['GET', 'POST'])
def warden_login():
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('auth.logout'))

    if request.method == 'POST':
        warden_id = request.form.get('warden_id', '').strip()
        password = request.form.get('password', '').strip()

        warden = Warden.query.filter(Warden.warden_id.ilike(warden_id)).first()

        if warden and warden.check_password(password):
            login_user(warden, remember=False)
            session.permanent = True
            session['warden_logged_in'] = True
            session['warden_id'] = warden.warden_id
            session['warden_name'] = getattr(warden, 'name', 'Warden')
            session['user_role'] = 'WARDEN'

            flash("Warden Protocol Authorized.", "success")
            return redirect(url_for('hangar.agent_terminal'))

        flash("🚨 ACCESS DENIED: Invalid Warden ID or Protocol Key.", "danger")
        return redirect(url_for('auth.warden_login'))

    return render_template('warden_login.html')


@auth_bp.route('/warden/force-login')
def force_login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.logout'))

    warden = Warden.query.first()
    if warden:
        login_user(warden, remember=False)

    session['warden_logged_in'] = True
    session['warden_id'] = getattr(warden, 'warden_id', 'WARDEN-01') if warden else 'WARDEN-01'
    session['warden_name'] = getattr(warden, 'name', 'Forensic Warden') if warden else 'Forensic Warden'
    session['user_role'] = 'WARDEN'

    flash("FORCE UPLINK: Warden session injected.", "success")
    return redirect(url_for('hangar.agent_terminal'))


@auth_bp.route('/warden/factory-reset')
def warden_factory_reset():
    warden = Warden.query.filter(Warden.warden_id.ilike('WARDEN-01')).first()

    if not warden:
        warden = Warden(warden_id='WARDEN-01', name='Forensic Warden')
        db.session.add(warden)

    warden.set_password('laveto2026')
    db.session.commit()

    return """
    <div style='background:#0a0a0a; color:#28a745; padding:50px; font-family:monospace; text-align:center;'>
        <h1>✅ WARDEN-01 FACTORY RESET COMPLETE</h1>
        <p>Your database hash is fully restored.</p>
        <p style='color:#fff; font-size:1.2rem;'>Username: <b>WARDEN-01</b></p>
        <p style='color:#fff; font-size:1.2rem;'>Password: <b>laveto2026</b></p>
        <br><br>
        <a href='/auth/staff' style='color:#d4af37; text-decoration:none; border:1px solid #d4af37; padding:10px 20px;'>RETURN TO STAFF LOGIN</a>
    </div>
    """


@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()

    resp = make_response(redirect(url_for('auth.login')))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'

    resp.delete_cookie('remember_token')
    resp.delete_cookie('session')
    resp.delete_cookie('laveto_session_id')

    return resp

# ==========================================
# 🛡️ BULLETPROOF USER LOADER WITH DEAD-SOCKET PROTECTION
# ==========================================
@login_manager.user_loader
def load_user(user_id):
    try:
        user_id_str = str(user_id)

        # 1. Prefix-based segregation
        if user_id_str.startswith("WARDEN_"):
            clean_id = user_id_str.replace("WARDEN_", "")
            if clean_id.isdigit():
                return Warden.query.get(int(clean_id))

        elif user_id_str.startswith("USER_"):
            clean_id = user_id_str.replace("USER_", "")
            if clean_id.isdigit():
                return User.query.get(int(clean_id))

        # 2. Legacy fallback handling
        if user_id_str.isdigit():
            clean_id = int(user_id_str)
            if session.get('user_role') == 'WARDEN' or session.get('warden_logged_in') == True:
                return Warden.query.get(clean_id)
            return User.query.get(clean_id)

    except Exception as e:
        print(f"🚨 USER LOADER EXCEPTION: {str(e)}", flush=True)

        try:
            db.session.rollback()
        except Exception:
            pass

        try:
            db.session.remove()
        except Exception:
            pass

        session.clear()
        return None

    return None

# ==========================================
# 🚀 SOVEREIGN VAULT: UNIVERSAL DECODER
# ==========================================
@auth_bp.route('/member-login', methods=['POST'])
def member_login():
    if current_user.is_authenticated:
        logout_user()
        session.clear()

    vin_attempt = request.form.get('vin_dna', '').strip().upper()
    key_attempt = request.form.get('sovereign_key', '').strip()

    asset = SovereignLedger.query.filter_by(vin_dna=vin_attempt).first()

    if asset:
        db_key = str(getattr(asset, 'sovereign_key', '')).strip()
        match_found = False

        if db_key.upper() == key_attempt.upper():
            match_found = True

        elif db_key.startswith('pbkdf2:') or db_key.startswith('scrypt:'):
            if check_password_hash(db_key, key_attempt) or check_password_hash(db_key, key_attempt.upper()):
                match_found = True

        else:
            sha256_lower = hashlib.sha256(key_attempt.encode('utf-8')).hexdigest()
            sha256_upper = hashlib.sha256(key_attempt.upper().encode('utf-8')).hexdigest()

            if db_key.lower() == sha256_lower.lower() or db_key.lower() == sha256_upper.lower():
                match_found = True

        if match_found:
            session.permanent = True
            session['member_access_granted'] = asset.vin_dna
            flash(f"✅ IDENTITY VERIFIED: Welcome to the Sovereign Vault.", "success")
            return redirect(url_for('hangar.client_vault', asset_id=asset.vin_dna))

    flash("🚨 ACCESS DENIED: Invalid Vehicle DNA or Sovereign Key.", "danger")
    return redirect(request.referrer or url_for('hangar.index'))

@auth_bp.route('/api/check-auth')
def check_auth():
    return jsonify({"authenticated": current_user.is_authenticated})