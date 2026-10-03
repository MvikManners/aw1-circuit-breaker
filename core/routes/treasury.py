from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from functools import wraps
from core import db
from core.models.access import AccessLog
from core.models.vehicles import SovereignLedger, SovereignTransaction, VaultTransaction, CorporateTreasury
from datetime import datetime

treasury_bp = Blueprint('treasury', __name__)

# 🛡️ THE ARCHITECT & HIGH COMMAND SECURITY DECORATOR
def architect_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = str(getattr(current_user, 'role', 'GUEST')).upper().strip()
        if role not in ['ADMIN', 'ARCHITECT']:
            flash("🚨 SECURITY BREACH DETECTED: Treasury perimeter breach attempted.", "error")
            return redirect(url_for('hangar.agent_terminal'))
        return f(*args, **kwargs)
    return decorated_function

@treasury_bp.route('/corporate-treasury', methods=['GET'])
@login_required
@architect_only
def view_treasury():
    # Only High Command (Architect / Admin) can cross this threshold
    treasury_data = CorporateTreasury.query.first()
    return render_template('treasury.html', treasury=treasury_data)

@treasury_bp.route('/process-vault-pulse/<int:asset_id>', methods=['POST'])
@login_required
@architect_only
def process_vault_pulse(asset_id):
    try:
        # 1. Capture and Normalize Payment Data
        raw_amount = request.form.get('deposit_amount') or request.form.get('payment_amount', 0)

        if isinstance(raw_amount, str):
            raw_amount = raw_amount.replace(',', '').strip()
            if not raw_amount:
                raw_amount = 0

        amount = float(raw_amount)
        payment_type = request.form.get('payment_type', 'DEPOSIT').upper()

        if amount <= 0:
            flash(f"SYSTEM REJECTED: Invalid deposit amount (Value received: {amount}).", "error")
            return redirect(request.referrer or url_for('hangar.index'))

        # 2. Locate Asset
        asset = SovereignLedger.query.get_or_404(asset_id)

        # Standardize VIN DNA to prevent lookup mismatches
        clean_vin = str(asset.vin_dna).strip().upper()
        asset.vin_dna = clean_vin

        # --- 🛡️ THE COVENANT LOCK (TREASURY FIREWALL) ---
        if asset.admin_status in ['ONBOARDING', 'PENDING', 'UNVERIFIED']:
            flash(f"⛔ TREASURY LOCK: Member node is still in {asset.admin_status}. MD Approval required before funding.", "error")
            return redirect(request.referrer or url_for('hangar.index'))
        # ------------------------------------------------

        # Calculate current deficit status
        current_repair_cost = float(asset.target_repair_cost or 0)
        current_funds = float(asset.shield_reservoir or 0)
        current_deficit = current_repair_cost - current_funds

        # 3. Dynamic Fee Calculation (Zero-Skim Shortfall Rule)
        # If an active repair shortfall deficit exists OR it's an emergency pulse, fee is 0%
        if current_deficit > 0.01 or "EMERGENCY" in payment_type or "SHORTFALL" in payment_type:
            fee = 0.0
            net_credit = amount
        else:
            # Standard voluntary monthly Motshelo deposits get the 5% network fee
            fee = amount * 0.05
            net_credit = amount * 0.95

        # 4. Update Ledger
        asset.shield_reservoir = current_funds + net_credit
        asset.lvt_balance = float(asset.lvt_balance or 0.0) + net_credit

        # --- STATUS SYNC: THE LOGIC BRIDGE ---
        if asset.admin_status == 'APPROVED':
            asset.admin_status = 'VERIFIED'
            asset.deposit_status = 'ACTIVE_DEPOSITOR'
        # -------------------------------------

        db.session.add(asset)

        # 5. Record Vault Transaction (Linked strictly to clean VIN)
        new_tx = VaultTransaction(
            vin_dna=clean_vin,
            intent=f"PULSE: {payment_type} | NET: P{net_credit:,.2f} | FEE: P{fee:,.2f}",
            amount=amount,
            timestamp=datetime.utcnow(),
            status="CLEARED"
        )
        db.session.add(new_tx)

        # 6. Record Sovereign Ledger Telemetry (Ensures it appears in master transaction feeds)
        from core.models.vehicles import SovereignTransaction
        master_tx = SovereignTransaction(
            ledger_id=asset.id,
            intent=f"PULSE INJECTION: P{amount:,.2f} (Net: P{net_credit:,.2f})",
            amount=net_credit,
            timestamp=datetime.utcnow()
        )
        db.session.add(master_tx)

        # 7. Log Admin Pulse
        new_log = AccessLog(action=f"Vault pulse processed for asset {clean_vin}. Net credit applied: P{net_credit:,.2f}.")
        db.session.add(new_log)

        db.session.commit()

        flash(f"Pulse processed successfully. P{net_credit:,.2f} credited to node.", "success")
        return redirect(request.referrer or url_for('hangar.index'))

    except ValueError:
        flash("SYSTEM REJECTED: Input is not a valid decimal number.", "error")
        return redirect(request.referrer or url_for('hangar.index'))
    except Exception as e:
        db.session.rollback()
        flash(f"Transaction failed: {str(e)}", "error")
        return redirect(request.referrer or url_for('hangar.index'))

@treasury_bp.route('/clear-onboarding/<int:asset_id>')
@login_required
@architect_only
def clear_onboarding(asset_id):
    try:
        asset = SovereignLedger.query.get_or_404(asset_id)
        asset.admin_status = 'APPROVED'
        db.session.commit()
        flash(f"✅ Member node has been cleared from onboarding. Treasury unlocked.", "success")
        return redirect(url_for('hangar.view_ledger'))
    except Exception as e:
        db.session.rollback()
        flash(f"Clear onboarding failed: {str(e)}", "error")
        return redirect(url_for('hangar.view_ledger'))

@treasury_bp.route('/<string:client_id>', methods=['GET', 'POST'])
@login_required
@architect_only
def client_vault_detail(client_id):
    if request.method == 'POST':
        pass
    return f"Accessing secure vault partition for authorized node."

@treasury_bp.route('/deposit', methods=['POST'])
@login_required
def process_deposit():
    # ... your existing deposit amount extraction and wallet update logic ...
    deposit_amount = float(request.form.get('amount', 650.0))

    # 1. Update the user/asset balance
    # current_user.wallet_balance += deposit_amount
    # (Keep your existing balance update code here)

    try:
        # 🟢 CRITICAL: Force-write the deposit event to SovereignTransaction so Audit Log sees it live
        from core.models import SovereignTransaction

        savings_part = deposit_amount * 0.60
        maintenance_part = deposit_amount * 0.40

        audit_entry = SovereignTransaction(
            ledger_id=getattr(current_user, 'id', 1), # Replace with your active asset/user ledger ID reference
            type="DEPOSIT",
            intent=f"DEPOSIT PROCESSED: P{deposit_amount} | LVT MINTED",
            status="ACTIVE",
            amount=deposit_amount,
            balance_after=getattr(current_user, 'wallet_balance', deposit_amount),
            timestamp=datetime.utcnow(),
            auth_by=getattr(current_user, 'username', 'SYSTEM')
        )
        db.session.add(audit_entry)
        db.session.commit()

        flash(f"✅ P{deposit_amount} Deposit processed. Audit log synchronized.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"🚨 DEPOSIT AUDIT SYNC FAULT: {str(e)}", flush=True)

    return redirect(url_for('treasury.treasury_portal')) # Or your redirect route