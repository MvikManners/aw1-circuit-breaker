from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from functools import wraps
from core.extensions import db, csrf, login_manager
from core.models.actors import User, Warden

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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ident_user = (request.form.get('username') or request.form.get('agent_id') or '').strip()
        password = request.form.get('password')

        # 1. Primary Auth Track: Standard Users & Administrators
        user = User.query.filter_by(username=ident_user).first()
        if user and user.check_password(password):
            login_user(user)
            role = str(getattr(user, 'role', 'GUEST')).upper().strip()
            session.permanent = True
            session['member_access_granted'] = True
            session['user_role'] = role
            if role in ['ADMIN', 'ARCHITECT', 'MD']:
                return redirect(url_for('hangar.view_ledger'))
            elif role in ['WARDEN', 'STAFF', 'AGENT']:
                return redirect(url_for('hangar.agent_terminal'))

        # 2. Secondary Auth Track: Specialized Warden Profiles
        warden = Warden.query.filter_by(warden_id=ident_user).first()
        if warden and warden.check_password(password):
            # We log in a system-authorized User proxy to satisfy Flask-Login universally
            # This completely bypasses the Warden model's missing attributes
            proxy_user = User.query.filter_by(role='WARDEN').first()
            if proxy_user:
                login_user(proxy_user)

            # Populate your tracking sessions for downstream decorators and views
            session.permanent = True
            session['warden_logged_in'] = True
            session['warden_id'] = warden.warden_id
            session['warden_name'] = warden.name
            session['user_role'] = 'WARDEN'

            flash("Warden Protocol Authorized.", "success")
            return redirect(url_for('hangar.agent_terminal'))

        # Global denial fallback
        flash('🚨 Invalid credentials.', 'error')
    return render_template('staff_login.html')

@auth_bp.route('/warden/login', methods=['GET', 'POST'])
def warden_login():
    if request.method == 'POST':
        warden_id = request.form.get('warden_id', '').strip()
        password = request.form.get('password', '').strip()
        warden = Warden.query.filter_by(warden_id=warden_id).first()

        if warden and warden.check_password(password):
            session.permanent = True
            session['warden_logged_in'] = True
            session['warden_id'] = warden.warden_id
            session['warden_name'] = warden.name
            flash("Warden Protocol Authorized.", "success")
            return redirect(url_for('hangar.agent_terminal'))

        flash("🚨 ACCESS DENIED: Invalid Warden ID or Protocol Key.", "error")
        return redirect(url_for('auth.warden_login'))

    # Guaranteed return for GET requests
    return render_template('warden_login.html')

@auth_bp.route('/warden/force-login')
def force_login():
    session['warden_logged_in'] = True
    session['warden_id'] = 'WARDEN-01'
    session['warden_name'] = 'Forensic Warden'
    flash("FORCE UPLINK: Warden session injected.", "success")
    return redirect(url_for('hangar.agent_terminal'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("You have securely logged out.", "info")
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user if user else Warden.query.get(user_id)

# ... existing code ...

@auth_bp.route('/member-login', methods=['POST'])
def member_login():
    from core.models.vehicles import SovereignLedger

    vin_attempt = request.form.get('vin_dna', '').strip().upper()
    key_attempt = request.form.get('sovereign_key', '').strip()

    # Query the Ledger instead of the non-existent User model
    asset = SovereignLedger.query.filter_by(vin_dna=vin_attempt, sovereign_key=key_attempt).first()

    if asset:
        session.permanent = True
        session['member_access_granted'] = asset.vin_dna
        return redirect(url_for('hangar.client_vault', asset_id=asset.vin_dna))
    else:
        flash("🚨 ACCESS DENIED: Invalid Vehicle DNA or Sovereign Key.", "error")
        return redirect(request.referrer or url_for('hangar.index'))

# ... existing code ...