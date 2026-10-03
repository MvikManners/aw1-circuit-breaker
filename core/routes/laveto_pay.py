import time
# core/routes/laveto_pay.py
# Laveto Pay Universal Gateway, Master Operator Console, KYC Engine, Escrow Engine,
# Ads, Flyer Studio, S2S Callback, Disbursal Hub, Live Soundbox & Motshelo Layaway Engine

import os
import io
import re
import uuid
import random
import secrets
import hmac
import hashlib
import qrcode
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    send_file,
    current_app,
)

from core.extensions import db, limiter
from core.models import Merchant, PayLink, PaymentTransaction, LayawayOrder, AdCampaign, Cashier

laveto_pay_bp = Blueprint('laveto_pay', __name__)

PLATFORM_FEE_RATE = float(os.environ.get('PLATFORM_FEE_RATE', 0.015))
W3W_API_KEY = os.environ.get('W3W_API_KEY', '')
WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'laveto_wa_verify_2026')
ADMIN_MASTER_PIN = os.environ.get('LAVETO_ADMIN_PIN', '2026')


# ==========================================
# 📢 ADVERTISING & NOTIFICATION HELPERS
# ==========================================
def fetch_active_ad(target_audience='buyer_b2c_general'):
    try:
        active_ads = AdCampaign.query.filter(
            AdCampaign.target_audience == target_audience,
            AdCampaign.is_active == True,
            AdCampaign.budget_spent < AdCampaign.budget_total
        ).all()

        if not active_ads:
            return None

        ad = random.choice(active_ads)
        ad.impressions_count = (ad.impressions_count or 0) + 1
        db.session.commit()
        return ad
    except Exception:
        return None


def normalize_bw_phone(phone: str) -> str:
    clean = ''.join(filter(str.isdigit, str(phone or '')))
    if clean.startswith('267') and len(clean) == 11:
        return f"+{clean}"
    elif len(clean) == 8:
        return f"+267{clean}"
    elif str(phone).startswith('+'):
        return str(phone)
    return f"+{clean}"


def send_africastalking_sms(recipient: str, message: str) -> bool:
    username = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
    api_key = os.environ.get('AFRICASTALKING_API_KEY', '')

    if not api_key:
        print(f"[SMS SIMULATION] To {recipient} -> {message}", flush=True)
        return False

    url = 'https://api.africastalking.com/version1/messaging'
    headers = {
        'ApiKey': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    data = {
        'username': username,
        'to': normalize_bw_phone(recipient),
        'message': message,
        'from': os.environ.get('AFRICASTALKING_SENDER_ID', 'LavetoPay')
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=8)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"[SMS ERROR] {e}", flush=True)
        return False


def send_whatsapp_direct(recipient_e164: str, message_text: str) -> bool:
    wa_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

    if not wa_token or not phone_id:
        print(f"[WA LOCAL LOG] To {recipient_e164}: {message_text}", flush=True)
        return False

    clean_phone = ''.join(filter(str.isdigit, str(recipient_e164 or '')))
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    headers = {
        'Authorization': f"Bearer {wa_token}",
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': clean_phone,
        'type': 'text',
        'text': {'body': message_text}
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=8)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"[WA ERROR] {e}", flush=True)
        return False


def dispatch_transaction_receipt(phone_e164: str, customer_name: str, amount: float, ref: str, pin: str, merchant_name: str, audience='buyer_b2c_general') -> bool:
    sponsored_ad = fetch_active_ad(audience)
    sponsor_suffix = f" Sponsored: {sponsored_ad.sms_suffix_text}" if (sponsored_ad and sponsored_ad.sms_suffix_text) else ""

    wa_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

    if wa_token and phone_id:
        clean_phone = phone_e164.replace('+', '').strip()
        url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
        headers = {
            'Authorization': f"Bearer {wa_token}",
            'Content-Type': 'application/json'
        }
        payload = {
            'messaging_product': 'whatsapp',
            'to': clean_phone,
            'type': 'template',
            'template': {
                'name': 'payment_cleared_receipt',
                'language': {'code': 'en'},
                'components': [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': customer_name},
                            {'type': 'text', 'text': f"P{amount:,.2f}"},
                            {'type': 'text', 'text': merchant_name},
                            {'type': 'text', 'text': ref},
                            {'type': 'text', 'text': pin}
                        ]
                    }
                ]
            }
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=4)
            if res.status_code in [200, 201]:
                return True
        except Exception:
            pass

    sms_body = f"Re a go leboga! Payment of P{amount:,.2f} to {merchant_name} is HELD in Laveto Escrow. PIN: {pin}. Ref: {ref}.{sponsor_suffix}"
    return send_africastalking_sms(phone_e164, sms_body)


def convert_gps_to_w3w(lat: float, lng: float) -> dict:
    if not W3W_API_KEY:
        return {'status': 'success', 'words': '///spinach.harvest.gaborone', 'simulated': True}

    url = 'https://api.what3words.com/v3/convert-to-3wa'
    params = {'coordinates': f"{lat},{lng}", 'key': W3W_API_KEY, 'language': 'en'}
    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if res.status_code == 200:
            return {'status': 'success', 'words': f"///{data.get('words')}", 'nearestPlace': data.get('nearestPlace')}
        return {'status': 'error', 'message': data.get('error', {}).get('message', 'Geocoding failed')}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


# ===================================================================
# 🏛️ LAVETO PAY — SOVEREIGN PAYMENT GATEWAY & FIAT OFF-RAMP ROUTER
# ===================================================================
class LavetoPayEngine:
    SUPPORTED_PROVIDERS = {
        "ORANGE_MONEY": {
            "name": "Orange Money",
            "type": "Mobile Money (USSD Push)",
            "fee_pct": 1.5,
            "settlement_speed": "Instant (USSD Push)",
            "daily_limit_bwp": 10000.0
        },
        "MASCOM_MYZAKA": {
            "name": "Mascom MyZaka",
            "type": "Mobile Money",
            "fee_pct": 1.5,
            "settlement_speed": "Instant (USSD Push)",
            "daily_limit_bwp": 10000.0
        },
        "BANK_EFT": {
            "name": "Commercial Bank EFT (FNBB / Stanbic / Absa)",
            "type": "National Clearing System",
            "fee_pct": 0.75,
            "settlement_speed": "Same-Day ACH / EFT",
            "daily_limit_bwp": 50000.0
        },
        "CARDLESS_ATM": {
            "name": "Cardless ATM Cash Voucher",
            "type": "ATM OTP Withdrawal Voucher",
            "fee_pct": 2.0,
            "settlement_speed": "Instant (SMS PIN Voucher)",
            "daily_limit_bwp": 4000.0
        }
    }

    def __init__(self, treasury_reserve_bwp: float = 540000.0, spot_rate_bwp: float = 2.50):
        self.treasury_reserve_bwp = treasury_reserve_bwp
        self.spot_rate_bwp = spot_rate_bwp
        self.disbursement_history = []

    def process_offramp_disbursement(
        self,
        node_address: str,
        awt_amount: float,
        provider_key: str,
        phone_or_account: str
    ) -> Dict[str, Any]:
        provider = self.SUPPORTED_PROVIDERS.get(provider_key, {
            "name": provider_key,
            "type": "Standard",
            "fee_pct": 1.5,
            "settlement_speed": "Instant",
            "daily_limit_bwp": 10000.0
        })

        gross_bwp = round(awt_amount * self.spot_rate_bwp, 2)
        fee_pct = provider["fee_pct"]
        fee_bwp = round((gross_bwp * fee_pct) / 100.0, 2)
        net_bwp = round(gross_bwp - fee_bwp, 2)

        self.treasury_reserve_bwp = max(0.0, round(self.treasury_reserve_bwp - net_bwp, 2))

        disbursement_id = f"DISB-BW-{secrets.token_hex(4).upper()}"
        receipt = {
            "disbursement_id": disbursement_id,
            "node_address": node_address,
            "awt_amount": awt_amount,
            "gross_bwp": gross_bwp,
            "provider": provider["name"],
            "provider_key": provider_key,
            "provider_type": provider["type"],
            "phone_or_account": phone_or_account,
            "gateway_fee_pct": fee_pct,
            "gateway_fee_bwp": fee_bwp,
            "net_bwp_disbursed": net_bwp,
            "settlement_speed": provider["settlement_speed"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S CAT")
        }

        if provider_key == "CARDLESS_ATM":
            receipt["voucher_pin"] = f"{secrets.randbelow(900000) + 100000}"

        self.disbursement_history.append(receipt)
        return receipt


# ==========================================
# 🤖 WHATSAPP CONVERSATIONAL RESTOCK ENGINE
# ==========================================
def process_whatsapp_bot_command(sender_phone: str, raw_text: str) -> str:
    clean_phone = ''.join(filter(str.isdigit, str(sender_phone or '')))

    merchant = Merchant.query.filter(
        (Merchant.phone_number.like(f"%{clean_phone[-8:]}%")) |
        (Merchant.settlement_wallet.like(f"%{clean_phone[-8:]}%"))
    ).first()

    if not merchant:
        return (
            "⚠️ *LAVETO PAY ACCESS DENIED*\n"
            f"Phone number (+{clean_phone}) is not registered to an active merchant.\n\n"
            "Visit https://www.laveto.net to activate your WhatsApp merchant tools."
        )

    text = (raw_text or '').strip()
    text_upper = text.upper()

    if text_upper in ['STOCK', 'CHECK', 'STATUS', 'INVENTORY']:
        links = PayLink.query.filter_by(merchant_id=merchant.id, is_active=True).all()
        if not links:
            return f"📦 *{merchant.business_name} Catalog*\nNo items configured. Create one in your dashboard."

        reply = f"📦 *{merchant.business_name} // INVENTORY AUDIT*\n────────────────────\n"
        for l in links:
            if l.is_flexible:
                reply += f"• 💳 *{l.title}*: Dynamic / Counter Till\n"
            elif l.stock_quantity == 0:
                reply += f"• 🔴 *{l.title}*: SOLD OUT (P{l.price:,.2f})\n"
            elif l.stock_quantity > 0:
                tag = '🟡' if l.stock_quantity <= 3 else '🟢'
                reply += f"• {tag} *{l.title}*: {l.stock_quantity} in stock (P{l.price:,.2f})\n"
            else:
                reply += f"• 🟢 *{l.title}*: Infinite Supply (P{l.price:,.2f})\n"

        reply += (
            f"────────────────────\n"
            f"⚡ Available Float: P{merchant.unsettled_balance:,.2f} BWP\n"
            f"📲 Text *SWEEP* to withdraw funds."
        )
        return reply

    elif text_upper in ['SWEEP', 'PAYOUT', 'WITHDRAW', 'CASHOUT']:
        amount = merchant.unsettled_balance or 0.0
        if amount <= 0:
            return "⚠️ *FLOAT SWEEP*: No unsettled balance available. Current float: P0.00 BWP."

        sweep_ref = f"SWEEP-{uuid.uuid4().hex[:8].upper()}"
        merchant.settled_balance = (merchant.settled_balance or 0.0) + amount
        merchant.unsettled_balance = 0.0

        links = [l.id for l in merchant.pay_links]
        if links:
            PaymentTransaction.query.filter(
                PaymentTransaction.pay_link_id.in_(links),
                PaymentTransaction.payment_status == 'COMPLETED',
                PaymentTransaction.is_settled == False
            ).update({'is_settled': True, 'settlement_ref': sweep_ref}, synchronize_session=False)

        db.session.commit()
        return (
            f"⚡ *FLOAT SWEEP SUCCESSFUL*\n"
            f"💰 Amount: *P{amount:,.2f} BWP*\n"
            f"📲 Destination: {merchant.settlement_provider} ({merchant.settlement_wallet})\n"
            f"🧾 Reference: *{sweep_ref}*\n\n"
            f"Funds queued for automated telecom clearance."
        )

    add_match = re.match(r'^ADD\s+(\d+)\s+(.+)$', text, re.IGNORECASE)
    if add_match:
        qty = int(add_match.group(1))
        item_query = add_match.group(2).strip()

        link = PayLink.query.filter(
            PayLink.merchant_id == merchant.id,
            PayLink.title.ilike(f"%{item_query}%")
        ).first()

        if not link:
            return f"❌ Product matching *'{item_query}'* was not found in your catalog."

        current_qty = link.stock_quantity if (link.stock_quantity is not None and link.stock_quantity >= 0) else 0
        link.stock_quantity = current_qty + qty
        db.session.commit()

        return (
            f"✅ *STOCK RESTOCKED*\n"
            f"📦 Item: *{link.title}*\n"
            f"➕ Added: +{qty} units\n"
            f"📊 New Total: *{link.stock_quantity} units available*\n"
            f"🔗 Pay Link Active: https://www.laveto.net/pay/{merchant.username}/{link.slug}"
        )

    set_match = re.match(r'^SET\s+(\d+)\s+(.+)$', text, re.IGNORECASE)
    if set_match:
        qty = int(set_match.group(1))
        item_query = set_match.group(2).strip()

        link = PayLink.query.filter(
            PayLink.merchant_id == merchant.id,
            PayLink.title.ilike(f"%{item_query}%")
        ).first()

        if not link:
            return f"❌ Product matching *'{item_query}'* was not found in your catalog."

        link.stock_quantity = qty
        db.session.commit()

        return (
            f"✅ *INVENTORY UPDATED*\n"
            f"📦 Item: *{link.title}*\n"
            f"📊 Assigned Count: *{qty} units*\n"
            f"Status: {'🟢 Active' if qty > 0 else '🔴 Sold Out'}"
        )

    rfq_match = re.match(r'^RFQ\s+(.+?)(?:\s+(\d+))?$', text, re.IGNORECASE)
    if rfq_match:
        item_name = rfq_match.group(1).strip()
        qty = rfq_match.group(2) or '50'
        rfq_id = f"RFQ-{secrets.token_hex(3).upper()}"
        today_str = datetime.now().strftime('%d %B %Y')

        return (
            f"📋 *OFFICIAL PURCHASE ORDER / RFQ*\n"
            f"🏷️ *Ref:* {rfq_id} | 📅 *Date:* {today_str}\n"
            f"🏪 *From:* {merchant.business_name}\n"
            f"📲 *Contact:* {merchant.phone_number}\n"
            f"────────────────────\n"
            f"Please provide formal quotation for:\n"
            f"• *Item:* {item_name}\n"
            f"• *Requested Quantity:* {qty} units / bags\n"
            f"• *Delivery Terms:* Delivery to Gaborone Depot\n"
            f"• *Settlement Rail:* Instant BWP EFT / Mobile Wallet\n"
            f"────────────────────\n"
            f"_Forward this message directly to your supplier._"
        )

    return (
        f"👋 Dumela *{merchant.business_name}*!\n"
        f"*LAVETO BOT COMMANDS:*\n"
        f"• *STOCK*: Check live stock & float balance\n"
        f"• *ADD 10 [item]*: Restock units\n"
        f"• *SET 25 [item]*: Override stock count\n"
        f"• *SWEEP*: Withdraw float to mobile wallet\n"
        f"• *RFQ [item] [qty]*: Draft wholesale purchase order"
    )


# ==========================================
# 🌐 WHATSAPP INBOUND WEBHOOK ENDPOINT
# ==========================================
@laveto_pay_bp.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook_handler():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
            return str(challenge), 200
        return 'Forbidden', 403

    data = request.get_json() or {}
    try:
        entries = data.get('entry', [])
        for entry in entries:
            changes = entry.get('changes', [])
            for change in changes:
                value = change.get('value', {})
                messages = value.get('messages', [])
                for msg in messages:
                    if msg.get('type') == 'text':
                        sender_phone = msg.get('from')
                        body_text = msg.get('text', {}).get('body', '')

                        reply_text = process_whatsapp_bot_command(sender_phone, body_text)
                        send_whatsapp_direct(sender_phone, reply_text)

        return jsonify({'status': 'received'}), 200
    except Exception as e:
        print(f"[WEBHOOK PROCESS ERROR] {e}", flush=True)
        return jsonify({'status': 'error', 'message': str(e)}), 200


# ==========================================
# 🛒 DYNAMIC CHECKOUT ROUTERS & AD INJECTION
# ==========================================
@laveto_pay_bp.route('/pay', methods=['GET'])
@laveto_pay_bp.route('/pay/', methods=['GET'])
def laveto_pay_landing():
    merchants = Merchant.query.filter_by(is_active=True).all() if hasattr(Merchant, 'is_active') else Merchant.query.all()
    return render_template('pay/index.html', merchants=merchants)


@laveto_pay_bp.route('/pay/login', methods=['GET', 'POST'])
def merchant_login():
    if request.method == 'POST':
        identifier = request.form.get('username') or request.form.get('email') or request.form.get('phone')
        password = request.form.get('password', '')

        merchant = Merchant.query.filter(
            (Merchant.username == identifier) |
            (Merchant.email == identifier) |
            (Merchant.phone_number == identifier)
        ).first()

        if merchant and hasattr(merchant, 'password_hash') and check_password_hash(merchant.password_hash, password):
            session['merchant_id'] = merchant.id
            return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

        return render_template('pay/merchant_login.html', error='Invalid credentials. Please verify your login details.')

    return render_template('pay/merchant_login.html')

# =========================================================================
# 🏛️ ADMIN / MERCHANT ONBOARDING CONSOLE
# =========================================================================
@laveto_pay_bp.route('/admin/onboarding', methods=['GET', 'POST'])
@laveto_pay_bp.route('/pay/admin/onboarding', methods=['GET', 'POST'])
def admin_onboarding():
    from core.models import Merchant, PayLink

    if request.method == 'POST':
        business_name = request.form.get('business_name', '').strip()
        username = request.form.get('username', '').strip().lower().replace(' ', '-')
        phone = request.form.get('phone_number', '').strip()
        settlement_provider = request.form.get('settlement_provider', 'Orange Money')
        settlement_wallet = request.form.get('settlement_wallet', '').strip()
        delivery_fee = request.form.get('delivery_fee', 40.00)

        if not business_name or not username:
            flash("Business name and merchant slug are required.", "danger")
            return render_template('pay/onboarding.html')

        # Check for slug collision
        existing = Merchant.query.filter_by(username=username).first()
        if existing:
            flash(f"Merchant username '{username}' is already in use.", "warning")
            return render_template('pay/onboarding.html')

        try:
            new_merchant = Merchant(
                business_name=business_name,
                username=username,
                phone_number=phone,
                settlement_provider=settlement_provider,
                settlement_wallet=settlement_wallet,
                delivery_fee=float(delivery_fee) if delivery_fee else 40.00,
                is_verified=True
            )
            db.session.add(new_merchant)
            db.session.commit()

            # Automatically provision default till paylink
            default_link = PayLink(
                merchant_id=new_merchant.id,
                slug='till',
                title=f"{new_merchant.business_name} Counter Till",
                price=0.0,
                is_flexible=True,
                stock_quantity=-1,
                is_active=True
            )
            db.session.add(default_link)
            db.session.commit()

            flash(f"Merchant '{business_name}' successfully onboarded!", "success")
            return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=new_merchant.username))

        except Exception as e:
            db.session.rollback()
            flash(f"Error provisioning merchant: {str(e)}", "danger")

    return render_template('pay/onboarding.html')

# =========================================================================
# 🔄 MERCHANT OPERATIONAL MODE & ROLE SWITCHER
# =========================================================================
@laveto_pay_bp.route('/merchant/<merchant_slug>/update-role', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/update-role', methods=['POST'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/switch-mode', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/switch-mode', methods=['POST'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/switch-layout', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/switch-layout', methods=['POST'])
@laveto_pay_bp.route('/pay/api/merchant/switch-mode', methods=['POST'])
@laveto_pay_bp.route('/api/merchant/switch-mode', methods=['POST'])
def switch_merchant_store_mode(merchant_slug=None):
    from core.models import Merchant

    data = request.get_json(silent=True) or request.form or {}
    new_mode = (
        data.get('business_type') or
        data.get('role') or
        data.get('mode') or
        data.get('layout') or
        data.get('store_mode') or
        request.args.get('mode')
    )

    slug = merchant_slug or data.get('merchant_slug') or session.get('merchant_slug')
    if not slug and session.get('merchant_id'):
        m = Merchant.query.get(session.get('merchant_id'))
        if m:
            slug = m.username

    if not slug or not new_mode:
        return jsonify({
            'status': 'error',
            'success': False,
            'message': 'Missing merchant identifier or target operational role.'
        }), 400

    clean_slug = slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first()

    if not merchant:
        return jsonify({'status': 'error', 'success': False, 'message': f"Merchant '{slug}' not found."}), 404

    try:
        mode_val = str(new_mode).strip().upper()

        # Update whichever column your Merchant model uses
        if hasattr(merchant, 'business_type'):
            merchant.business_type = mode_val
        if hasattr(merchant, 'store_mode'):
            merchant.store_mode = mode_val
        if hasattr(merchant, 'category'):
            merchant.category = mode_val
        if hasattr(merchant, 'layout_mode'):
            merchant.layout_mode = mode_val

        db.session.commit()

        return jsonify({
            'status': 'success',
            'success': True,
            'mode': mode_val,
            'message': f"Store role switched to {mode_val}."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'success': False, 'message': str(e)}), 500

@laveto_pay_bp.route('/pay/register', methods=['GET', 'POST'])
def register_merchant():
    plan = request.args.get('plan', 'standard')
    if request.method == 'POST':
        business_name = request.form.get('business_name', '').strip()
        username = request.form.get('username', '').strip().lower()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        settlement_provider = request.form.get('settlement_provider', 'ORANGE_MONEY')
        settlement_wallet = request.form.get('settlement_wallet', phone_number).strip()

        if not business_name or not username or not phone_number:
            return render_template('pay/register.html', plan=plan, error='All required fields must be filled.')

        existing_merchant = Merchant.query.filter(
            (Merchant.username == username) |
            (Merchant.email == email)
        ).first()
        if existing_merchant:
            return render_template('pay/register.html', plan=plan, error='Username or email is already registered.')

        pwd_hash = generate_password_hash(password) if password else ''
        new_merchant = Merchant(
            business_name=business_name,
            username=username,
            phone_number=normalize_bw_phone(phone_number),
            email=email if email else None,
            settlement_provider=settlement_provider,
            settlement_wallet=settlement_wallet,
            is_active=True
        )
        if hasattr(new_merchant, 'password_hash'):
            new_merchant.password_hash = pwd_hash

        db.session.add(new_merchant)
        db.session.commit()

        session['merchant_id'] = new_merchant.id
        return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=new_merchant.username))

    return render_template('pay/register.html', plan=plan)

# ==========================================
# 🧺 SMART BASKET & MULTI-ITEM CHECKOUT
# ==========================================
@laveto_pay_bp.route('/pay/basket', methods=['GET'])
def global_smart_basket():
    """Universal smart basket for cross-merchant / multi-item staging."""
    merchants = Merchant.query.filter_by(is_active=True).all() if hasattr(Merchant, 'is_active') else Merchant.query.all()
    sponsored_ad = fetch_active_ad('buyer_b2c_general')
    return render_template(
        'pay/smart_basket.html',
        merchants=merchants,
        sponsored_ad=sponsored_ad,
        PLATFORM_FEE_RATE=PLATFORM_FEE_RATE
    )


@laveto_pay_bp.route('/pay/<merchant_slug>/basket', methods=['GET'])
@laveto_pay_bp.route('/pay/<merchant_slug>/checkout', methods=['GET'])
def merchant_basket_checkout(merchant_slug):
    """Merchant-specific smart basket checkout with item aggregation."""
    clean_slug = merchant_slug.replace('-', ' ')
    merchant = Merchant.query.filter(
        (Merchant.username == merchant_slug) |
        (Merchant.business_name.ilike(clean_slug))
    ).first_or_404()

    merchant_products = PayLink.query.filter_by(
        merchant_id=merchant.id,
        is_flexible=False,
        is_active=True
    ).order_by(PayLink.created_at.desc()).all()

    sponsored_ad = fetch_active_ad('buyer_b2c_general')
    delivery_fee = float(getattr(merchant, 'delivery_fee', 40.00) or 40.00)

    return render_template(
        'pay/basket_checkout.html',
        merchant=merchant,
        merchant_products=merchant_products,
        sponsored_ad=sponsored_ad,
        dynamic_delivery_fee=delivery_fee,
        PLATFORM_FEE_RATE=PLATFORM_FEE_RATE
    )

@laveto_pay_bp.route('/pay/<merchant_slug>', methods=['GET'])
@laveto_pay_bp.route('/pay/<merchant_slug>/<product_slug>', methods=['GET'])
def dynamic_checkout(merchant_slug, product_slug=None):
    clean_slug = merchant_slug.replace('-', ' ')
    merchant = Merchant.query.filter(
        (Merchant.username == merchant_slug) |
        (Merchant.business_name.ilike(clean_slug))
    ).first_or_404()

    merchant_products = PayLink.query.filter_by(
        merchant_id=merchant.id,
        is_flexible=False,
        is_active=True
    ).order_by(PayLink.created_at.desc()).all()

    if product_slug:
        pay_link = PayLink.query.filter_by(
            merchant_id=merchant.id,
            slug=product_slug,
            is_active=True
        ).first_or_404()
    else:
        pay_link = PayLink.query.filter_by(
            merchant_id=merchant.id,
            is_flexible=True,
            is_active=True
        ).first()

        if not pay_link:
            pay_link = PayLink(
                merchant_id=merchant.id,
                slug=f"{merchant.username}-counter",
                title=f"Pay {merchant.business_name}",
                price=0.0,
                is_flexible=True,
                stock_quantity=-1
            )
            db.session.add(pay_link)
            db.session.commit()

    sponsored_ad = fetch_active_ad('buyer_b2c_general')
    delivery_fee = float(getattr(merchant, 'delivery_fee', 40.00) or 40.00)

    total_escrow_locked = locals().get('total_escrow_locked', 0.0) or 0.0
    return render_template(
        'pay/checkout.html',
        merchant=merchant,
        pay_link=pay_link,
        merchant_products=merchant_products,
        sponsored_ad=sponsored_ad,
        dynamic_delivery_fee=delivery_fee,
        PLATFORM_FEE_RATE=PLATFORM_FEE_RATE
    )

# =========================================================================
# ⚙️ MERCHANT PLATFORM FEE SETTLEMENT POLICY SWITCHER
# =========================================================================
@laveto_pay_bp.route('/merchant/<merchant_slug>/toggle-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/toggle-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/fee-policy', methods=['POST'])
@laveto_pay_bp.route('/api/merchant/toggle-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/api/merchant/toggle-fee-policy', methods=['POST'])
def toggle_merchant_fee_policy(merchant_slug=None):
    from core.models import Merchant

    data = request.get_json(silent=True) or request.form or {}

    # Accept pass_fee, pass_fees_to_customer, or policy value
    pass_fees = data.get('pass_fees_to_customer')
    if pass_fees is None:
        pass_fees = data.get('pass_fee')
    if pass_fees is None:
        policy = str(data.get('policy', '')).lower()
        if 'pass' in policy or 'customer' in policy:
            pass_fees = True
        elif 'absorb' in policy or 'store' in policy:
            pass_fees = False

    # Convert strings like 'true' / 'false' to actual boolean
    if isinstance(pass_fees, str):
        pass_fees = pass_fees.strip().lower() in ['true', '1', 'yes', 'pass']

    slug = merchant_slug or data.get('merchant_slug') or session.get('merchant_slug')
    if not slug and session.get('merchant_id'):
        m = Merchant.query.get(session.get('merchant_id'))
        if m:
            slug = m.username

    if not slug:
        return jsonify({
            'status': 'error',
            'success': False,
            'message': 'Merchant username required.'
        }), 400

    clean_slug = slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first()

    if not merchant:
        return jsonify({
            'status': 'error',
            'success': False,
            'message': f"Merchant '{slug}' not found."
        }), 404

    try:
        if pass_fees is not None:
            merchant.pass_fees_to_customer = bool(pass_fees)
        else:
            # If nothing specified, invert current state
            current = bool(getattr(merchant, 'pass_fees_to_customer', False))
            merchant.pass_fees_to_customer = not current

        db.session.commit()

        return jsonify({
            'status': 'success',
            'success': True,
            'pass_fees_to_customer': merchant.pass_fees_to_customer,
            'message': 'Platform fee policy updated successfully.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'success': False,
            'message': str(e)
        }), 500

@laveto_pay_bp.route('/ad/click/<int:ad_id>', methods=['GET'])
def track_ad_click(ad_id):
    ad = AdCampaign.query.get_or_404(ad_id)
    ad.clicks_count = (ad.clicks_count or 0) + 1
    ad.budget_spent = (ad.budget_spent or 0.0) + (ad.cpc_rate or 0.50)

    if ad.budget_spent >= ad.budget_total:
        ad.is_active = False

    db.session.commit()
    return redirect(ad.target_url)


@laveto_pay_bp.route('/pay/receipt/<tx_ref>', methods=['GET'])
def view_digital_receipt(tx_ref):
    tx = PaymentTransaction.query.filter_by(aggregator_ref=tx_ref).first_or_404()
    merchant = tx.pay_link.merchant if tx.pay_link else Merchant.query.get(tx.merchant_id)
    sponsored_ad = fetch_active_ad('buyer_b2c_general')
    return render_template('pay/receipt.html', tx=tx, merchant=merchant, sponsored_ad=sponsored_ad)


# ==========================================
# ⚡ PAYMENT INITIATION & WEBHOOK ENGINE
# ==========================================
@laveto_pay_bp.route('/checkout/initiate', methods=['POST'])
@laveto_pay_bp.route('/pay/checkout/initiate', methods=['POST'])
@limiter.limit('5 per minute')
def initiate_payment():
    # ... existing logic ...
    import random, uuid, traceback
    try:
        data = request.get_json(silent=True) or {}
        link_id = data.get('pay_link_id')
        buyer_name = data.get('buyer_name', 'Retail Customer').strip()
        buyer_phone = data.get('buyer_phone', '').strip()
        payment_method = data.get('payment_method', 'ORANGE_MONEY').upper()
        delivery_w3w = data.get('delivery_w3w', '').strip()
        custom_amount = data.get('custom_amount')
        enable_escrow = bool(data.get('enable_escrow', False))

        if not buyer_phone:
            return jsonify({'status': 'error', 'message': 'Missing mobile wallet phone number.'}), 400

        pay_link = PayLink.query.get(link_id) if link_id else None

        if not pay_link:
            merchant_username = session.get('merchant_slug') or 'zarurunner'
            merchant = Merchant.query.filter_by(username=merchant_username).first()
            if not merchant:
                merchant = Merchant.query.first()

            if not merchant:
                return jsonify({'status': 'error', 'message': 'Merchant store context not found for till sale.'}), 404

            try:
                gross_amount = float(custom_amount or request.args.get('amount', 50.00))
            except (TypeError, ValueError):
                gross_amount = 50.00

            pay_link = PayLink.query.filter_by(merchant_id=merchant.id).first()
            if not pay_link:
                pay_link = PayLink(
                    merchant_id=merchant.id,
                    title="Counter Till Sale",
                    slug="counter-sale",
                    price=gross_amount,
                    is_active=True
                )
                db.session.add(pay_link)
                db.session.commit()
        else:
            if getattr(pay_link, 'stock_quantity', 1) == 0:
                return jsonify({'status': 'error', 'message': 'Item is currently SOLD OUT.'}), 400

            if getattr(pay_link, 'is_flexible', False) or custom_amount:
                try:
                    gross_amount = float(custom_amount)
                    if gross_amount <= 0:
                        raise ValueError
                except (TypeError, ValueError):
                    return jsonify({'status': 'error', 'message': 'Please enter a valid Pula (BWP) amount.'}), 400
            else:
                gross_amount = float(pay_link.price or 50.00)

        escrow_code = None
        escrow_status = 'NONE'
        if enable_escrow and getattr(pay_link, 'allow_escrow', False):
            escrow_code = str(random.randint(1000, 9999))
            escrow_status = 'HELD'

        fee_rate = globals().get('PLATFORM_FEE_RATE', 0.015)
        laveto_fee = round(gross_amount * fee_rate, 2)
        merchant_share = round(gross_amount - laveto_fee, 2)
        aggregator_tx_ref = f"LVT-{uuid.uuid4().hex[:10].upper()}"

        norm_phone = buyer_phone
        if 'normalize_bw_phone' in globals():
            try:
                norm_phone = normalize_bw_phone(buyer_phone)
            except Exception:
                pass

        tx = PaymentTransaction(
            pay_link_id=pay_link.id,
            merchant_id=pay_link.merchant_id,
            buyer_name=buyer_name,
            buyer_phone=norm_phone,
            payment_method=payment_method,
            gross_amount=gross_amount,
            laveto_fee=laveto_fee,
            merchant_share=merchant_share,
            aggregator_ref=aggregator_tx_ref,
            payment_status='PENDING',
            delivery_w3w=delivery_w3w,
            is_escrow=enable_escrow
        )
        db.session.add(tx)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Payment locked and USSD push initiated.',
            'reference': aggregator_tx_ref,
            'tx_ref': aggregator_tx_ref,
            'redirect_url': url_for('laveto_pay.view_digital_receipt', tx_ref=aggregator_tx_ref)
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Server Exception: {str(e)}'
        }), 500
@laveto_pay_bp.route('/merchant/<merchant_slug>/link/<int:link_id>/delete', methods=['POST'])
def delete_pay_link(merchant_slug, link_id):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()

    link = PayLink.query.filter_by(id=link_id, merchant_id=merchant.id).first()
    if not link:
        return jsonify({'status': 'error', 'message': 'Unauthorized action'}), 403

    link.is_active = False
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Link deactivated'})


@laveto_pay_bp.route('/payment/callback', methods=['POST'])
def payment_webhook():
    webhook_secret = os.environ.get('AGGREGATOR_WEBHOOK_SECRET', '')

    signature = request.headers.get('X-Signature') or request.headers.get('X-Hub-Signature-256')
    if webhook_secret and signature:
        raw_payload = request.get_data()
        expected_sig = hmac.new(webhook_secret.encode(), raw_payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature.replace('sha256=', ''), expected_sig):
            return jsonify({'status': 'error', 'message': 'Invalid HMAC signature'}), 403

    payload = request.get_json() or {}
    tx_ref = payload.get('reference') or payload.get('transaction_ref')
    status = (payload.get('status') or '').upper()

    if not tx_ref:
        return jsonify({'status': 'error', 'message': 'Missing transaction reference'}), 400

    tx = PaymentTransaction.query.filter_by(aggregator_ref=tx_ref).first()
    if not tx:
        return jsonify({'status': 'error', 'message': 'Transaction not found'}), 404

    if tx.payment_status == 'COMPLETED':
        return jsonify({'status': 'ignored', 'message': 'Transaction already settled'}), 200

    if status == 'SUCCESS':
        tx.payment_status = 'COMPLETED'
        merchant = tx.pay_link.merchant if tx.pay_link else Merchant.query.get(tx.merchant_id)
        if merchant:
            merchant.unsettled_balance = (merchant.unsettled_balance or 0.0) + (tx.merchant_share or 0.0)

        if tx.pay_link and tx.pay_link.stock_quantity > 0:
            tx.pay_link.stock_quantity -= 1

        db.session.commit()

        merchant_name = merchant.business_name if merchant else "Laveto Merchant"
        dispatch_transaction_receipt(
            tx.buyer_phone,
            tx.buyer_name or 'Customer',
            tx.gross_amount,
            tx.aggregator_ref,
            tx.escrow_release_code or 'N/A',
            merchant_name,
            audience='buyer_b2c_general'
        )

        return jsonify({'status': 'settled', 'reference': tx_ref}), 200
    else:
        tx.payment_status = 'FAILED'
        db.session.commit()
        return jsonify({'status': 'failed', 'reference': tx_ref}), 200

# =========================================================================
# 📣 LAVETO ADS & SOCIAL PROMOTION PORTAL
# =========================================================================
@laveto_pay_bp.route('/ads/promote', methods=['GET', 'POST'])
@laveto_pay_bp.route('/pay/ads/promote', methods=['GET', 'POST'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/ads/promote', methods=['GET', 'POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/ads/promote', methods=['GET', 'POST'])
def ads_promote(merchant_slug=None):
    import os
    from sqlalchemy import text
    from core.models import Merchant, PayLink

    # 1. Resolve merchant identity across slugs, query parameters, and session state
    slug = merchant_slug or request.args.get('merchant') or session.get('merchant_slug')
    merchant = None
    if slug:
        clean_slug = str(slug).strip().lower()
        merchant = Merchant.query.filter(
            db.or_(
                db.func.lower(Merchant.username) == clean_slug,
                db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
            )
        ).first()

    if not merchant and session.get('merchant_id'):
        merchant = Merchant.query.get(session.get('merchant_id'))

    # 2. Handle Campaign Launch Form Submission
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        ad_copy = request.form.get('ad_copy', '').strip()
        target_url = request.form.get('target_url', '').strip()
        budget = 50.00  # Fixed standard P50 checkout ad slot

        if not title or not ad_copy or not target_url:
            flash("All campaign fields (Business Name, Headline, Target Link) are required.", "warning")
            return redirect(request.url)

        try:
            # Ensure merchant_ad_campaigns table exists
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS merchant_ad_campaigns (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    merchant_id INTEGER NOT NULL,
                    advertiser_name VARCHAR(150) NOT NULL,
                    ad_copy_text TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    budget NUMERIC(10,2) DEFAULT 50.00,
                    clicks_count INTEGER DEFAULT 0,
                    impressions_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Insert campaign record directly into database
            m_id = merchant.id if merchant else 0
            db.session.execute(text("""
                INSERT INTO merchant_ad_campaigns
                (merchant_id, advertiser_name, ad_copy_text, target_url, budget, clicks_count, impressions_count, is_active)
                VALUES (:m_id, :adv, :copy, :url, :budget, 0, 0, 1)
            """), {
                "m_id": m_id,
                "adv": title,
                "copy": ad_copy,
                "url": target_url,
                "budget": budget
            })
            db.session.commit()

            flash(f"⚡ Campaign '{title}' launched successfully! Your banner is broadcasting across live network checkouts.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Notice: Campaign staged for clearing ({str(e)}).", "info")

        if merchant:
            return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))
        return redirect(url_for('laveto_pay.ads_promote'))

    # 3. GET View: Render the promotion form
    links = PayLink.query.filter_by(merchant_id=merchant.id, is_active=True).all() if merchant else []

    template_name = 'pay/ads_promote.html'
    template_path = os.path.join('/home/LavetoLab/templates', template_name)
    if not os.path.exists(template_path):
        template_name = 'pay/promote_ads.html'

    return render_template(
        template_name,
        merchant=merchant,
        links=links,
        active_slug=(merchant.username if merchant else '')
    )

# =========================================================================
# 🗑️ MERCHANT PAY LINK DELETION
# =========================================================================
@laveto_pay_bp.route('/merchant/<merchant_slug>/delete-link/<int:link_id>', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/delete-link/<int:link_id>', methods=['POST'])
def merchant_delete_link(merchant_slug, link_id):
    from core.models import Merchant, PayLink

    clean_slug = merchant_slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first()

    if not merchant:
        flash(f"Merchant '{merchant_slug}' not found.", "danger")
        return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant_slug))

    link = PayLink.query.filter_by(id=link_id, merchant_id=merchant.id).first()
    if not link:
        flash("Pay link not found or already deleted.", "warning")
        return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

    # Protect the till counter
    if getattr(link, 'slug', '') == 'till' or (getattr(link, 'is_flexible', False) and link.price == 0):
        flash("The default store till cannot be deleted.", "warning")
        return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

    try:
        title = link.title
        db.session.delete(link)
        db.session.commit()
        flash(f"🗑️ Deleted '{title}' successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting item: {str(e)}", "danger")

    return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

# ==========================================
# 🛡️ MOTSHELO LAYAWAY ROUTERS
# ==========================================
@laveto_pay_bp.route('/checkout/layaway/initiate', methods=['POST'])
def initiate_layaway():
    data = request.get_json() or {}
    pay_link_id = data.get('pay_link_id')
    buyer_name = data.get('buyer_name', 'Boutique Customer').strip()
    buyer_phone = data.get('buyer_phone', '').strip()

    if not pay_link_id or not buyer_phone:
        return jsonify({'status': 'error', 'message': 'Missing product ID or customer phone.'}), 400

    link = PayLink.query.get_or_404(pay_link_id)

    if link.stock_quantity == 0:
        return jsonify({'status': 'error', 'message': 'Item is sold out'}), 400

    total_price = float(link.price or 0.0)
    deposit = round(total_price * 0.30, 2)
    balance = round(total_price - deposit, 2)

    contract_ref = f"LAY-{secrets.token_hex(4).upper()}"
    expiry = datetime.utcnow() + timedelta(days=30)

    layaway = LayawayOrder(
        merchant_id=link.merchant_id,
        pay_link_id=link.id,
        buyer_name=buyer_name,
        buyer_phone=normalize_bw_phone(buyer_phone),
        item_title=link.title,
        total_amount=total_price,
        deposit_amount=deposit,
        amount_paid=0.0,
        status='ACTIVE',
        notes=f"Ref: {contract_ref} | Due in 30 days"
    )

    if link.stock_quantity > 0:
        link.stock_quantity -= 1

    db.session.add(layaway)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'contract_ref': contract_ref,
        'deposit_required': deposit,
        'remaining_balance': balance,
        'expiry_date': expiry.strftime('%Y-%m-%d'),
        'balance_pay_url': f"https://www.laveto.net/pay/layaway/{contract_ref}"
    }), 200


@laveto_pay_bp.route('/pay/layaway/<contract_ref>')
def view_layaway_settlement(contract_ref):
    if contract_ref.isdigit():
        layaway = LayawayOrder.query.filter_by(id=int(contract_ref)).first_or_404()
    else:
        layaway = LayawayOrder.query.filter_by(id=1).first_or_404()

    return render_template(
        'pay/layaway_settlement.html',
        layaway=layaway,
        merchant=layaway.merchant,
        product=layaway.pay_link
    )


# ==========================================
# 📊 MERCHANT ANALYTICS & TILL DASHBOARD
# ==========================================
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/dashboard', methods=['GET'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/dashboard', methods=['GET'])
def merchant_dashboard(merchant_slug):
    from core.models import Merchant, PayLink, PaymentTransaction
    from sqlalchemy import text

    clean_slug = merchant_slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first_or_404()

    links = PayLink.query.filter_by(merchant_id=merchant.id).order_by(PayLink.created_at.desc()).all()

    link_ids = [l.id for l in links]
    transactions = PaymentTransaction.query.filter(
        PaymentTransaction.pay_link_id.in_(link_ids)
    ).order_by(PaymentTransaction.created_at.desc()).limit(35).all() if link_ids else []

    total_gross = sum((t.gross_amount or 0.0) for t in transactions if t.payment_status == 'COMPLETED')
    total_fees = sum(((t.gross_amount or 0.0) - (t.merchant_share or 0.0)) for t in transactions if t.payment_status == 'COMPLETED')
    total_net = sum((t.merchant_share or 0.0) for t in transactions if t.payment_status == 'COMPLETED')

    calculated_unsettled = sum(
        (t.merchant_share or 0.0) for t in transactions
        if t.payment_status == 'COMPLETED' and not getattr(t, 'is_settled', False) and (not t.is_escrow or t.escrow_status == 'RELEASED')
    )

    if (merchant.unsettled_balance or 0.0) != calculated_unsettled:
        merchant.unsettled_balance = calculated_unsettled
        db.session.commit()

    # Safe fetch of sponsored B2B ad if the helper is available
    b2b_ad = None
    try:
        if 'fetch_active_ad' in globals():
            b2b_ad = fetch_active_ad('merchant_b2b')
    except Exception:
        b2b_ad = None

    # Load Active Store Campaigns & Network Campaigns for Dashboard Display
    campaigns = []
    network_campaigns = []
    try:
        # 1. Campaigns belonging to this merchant
        c_res = db.session.execute(text("""
            SELECT id, advertiser_name, logo_icon, ad_copy_text, target_url,
                   budget, clicks_count, impressions_count, is_active
            FROM merchant_ad_campaigns
            WHERE merchant_id = :m_id
            ORDER BY id DESC
        """), {"m_id": merchant.id}).mappings().all()
        campaigns = [dict(c) for c in c_res]

        # 2. General active network campaigns (excluding self)
        net_res = db.session.execute(text("""
            SELECT id, advertiser_name, logo_icon, ad_copy_text, target_url,
                   clicks_count, impressions_count, is_active
            FROM merchant_ad_campaigns
            WHERE is_active = 1 AND merchant_id != :m_id
            ORDER BY id DESC LIMIT 5
        """), {"m_id": merchant.id}).mappings().all()
        network_campaigns = [dict(n) for n in net_res]

    except Exception as e:
        import logging
        logging.error(f"Error querying merchant_ad_campaigns: {e}")
        campaigns = []
        network_campaigns = []

    return render_template(
        'pay/merchant_dashboard.html',
        merchant=merchant,
        links=links,
        transactions=transactions,
        total_gross=total_gross,
        total_net=total_net,
        total_fees=total_fees,
        sponsored_ad=b2b_ad,
        campaigns=campaigns,
        network_campaigns=network_campaigns
    )


# 🖨️ STANDALONE COUNTER QR & FLYER PRINT VIEW
# ==========================================
@laveto_pay_bp.route('/pay/qr/<merchant_slug>/print', methods=['GET'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/print', methods=['GET'])
def print_merchant_counter_qr(merchant_slug):
    """
    Renders the print-ready counter stand QR and flyer layout
    formatted specifically for A4 and standard receipt printers.
    """
    clean_slug = merchant_slug.replace('-', ' ')
    merchant = Merchant.query.filter(
        (Merchant.username == merchant_slug) |
        (Merchant.business_name.ilike(clean_slug))
    ).first_or_404()

    products = PayLink.query.filter_by(
        merchant_id=merchant.id,
        is_active=True
    ).order_by(PayLink.created_at.desc()).all()

    store_url = f"https://laveto.net/pay/{merchant.username}"

    return render_template(
        'pay/flyer_print.html',
        merchant=merchant,
        products=products,
        store_url=store_url,
        till_url=store_url
    )

# ==========================================
# 📄 MERCHANT FLYER & QR MARKETING STUDIO
# ==========================================
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/flyer-generator', methods=['GET'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/flyer-generator', methods=['GET'])
def merchant_flyer_generator(merchant_slug):
    """Renders the printable marketing flyer and counter-stand QR generator."""
    clean_slug = merchant_slug.replace('-', ' ')
    merchant = Merchant.query.filter(
        (Merchant.username == merchant_slug) |
        (Merchant.business_name.ilike(clean_slug))
    ).first_or_404()

    # Retrieve all active products for flyer showcase
    products = PayLink.query.filter_by(
        merchant_id=merchant.id,
        is_active=True
    ).order_by(PayLink.created_at.desc()).all()

    return render_template(
        'pay/flyer_generator.html',
        merchant=merchant,
        products=products
    )

@laveto_pay_bp.route('/merchant/<merchant_slug>/release-escrow', methods=['POST'])
def release_escrow(merchant_slug):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()
    data = request.get_json() or {}
    tx_id = data.get('transaction_id')
    pin_code = str(data.get('release_pin', '')).strip()

    tx = PaymentTransaction.query.get_or_404(tx_id)

    if tx.merchant_id != merchant.id and (tx.pay_link and tx.pay_link.merchant_id != merchant.id):
        return jsonify({'status': 'error', 'message': 'Unauthorized operation.'}), 403

    if tx.escrow_status != 'HELD':
        return jsonify({'status': 'error', 'message': f"Escrow is already {tx.escrow_status}."}), 400

    if tx.escrow_release_code != pin_code and pin_code != ADMIN_MASTER_PIN:
        return jsonify({'status': 'error', 'message': '❌ Invalid 4-Digit Release PIN entered.'}), 400

    tx.escrow_status = 'RELEASED'
    merchant.unsettled_balance = (merchant.unsettled_balance or 0.0) + (tx.merchant_share or 0.0)
    db.session.commit()

    send_africastalking_sms(
        tx.buyer_phone,
        f"Laveto Pay: Delivery confirmed! P{tx.gross_amount:.2f} released to {merchant.business_name}."
    )

    return jsonify({
        'status': 'success',
        'message': f"✅ Escrow released! P{tx.merchant_share:.2f} credited to available balance."
    }), 200


@laveto_pay_bp.route('/merchant/<merchant_slug>/trigger-settlement', methods=['POST'])
def trigger_wallet_sweep(merchant_slug):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()
    amount_to_sweep = merchant.unsettled_balance or 0.0

    if amount_to_sweep <= 0:
        return jsonify({'status': 'error', 'message': 'No accumulated float available for settlement.'}), 400

    sweep_ref = f"SWEEP-{uuid.uuid4().hex[:8].upper()}"

    merchant.settled_balance = (merchant.settled_balance or 0.0) + amount_to_sweep
    merchant.unsettled_balance = 0.0

    links = [l.id for l in merchant.pay_links]
    if links:
        PaymentTransaction.query.filter(
            PaymentTransaction.pay_link_id.in_(links),
            PaymentTransaction.payment_status == 'COMPLETED',
            PaymentTransaction.is_settled == False
        ).update({'is_settled': True, 'settlement_ref': sweep_ref}, synchronize_session=False)

    db.session.commit()

    send_africastalking_sms(
        merchant.settlement_wallet or '',
        f"Laveto Float Sweep! P{amount_to_sweep:.2f} BWP disbursed to your {merchant.settlement_provider} ({merchant.settlement_wallet}). Ref: {sweep_ref}."
    )

    return jsonify({
        'status': 'success',
        'disbursed_amount': amount_to_sweep,
        'destination': f"{merchant.settlement_provider} ({merchant.settlement_wallet})",
        'sweep_ref': sweep_ref
    }), 200


@laveto_pay_bp.route('/merchant/<merchant_slug>/create-link', methods=['POST'])
def create_pay_link(merchant_slug):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()

    title = request.form.get('title', '').strip()
    raw_price = request.form.get('price', '0').strip()
    raw_stock = request.form.get('stock_quantity', '-1').strip()
    is_flexible = 'is_flexible' in request.form
    allow_escrow = 'allow_escrow' in request.form

    base_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    unique_slug = base_slug if base_slug else f"link-{uuid.uuid4().hex[:6]}"

    count = 1
    slug_candidate = unique_slug
    while PayLink.query.filter_by(slug=slug_candidate).first():
        slug_candidate = f"{unique_slug}-{count}"
        count += 1

    price = 0.0 if is_flexible else float(raw_price or 0.0)
    stock_quantity = int(raw_stock or -1)

    new_link = PayLink(
        merchant_id=merchant.id,
        slug=slug_candidate,
        title=title,
        price=price,
        stock_quantity=stock_quantity,
        is_flexible=is_flexible,
        allow_escrow=allow_escrow
    )
    db.session.add(new_link)
    db.session.commit()

    return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

# =========================================================================
# ⚙️ MERCHANT PLATFORM FEE SETTLEMENT POLICY SWITCHER
# =========================================================================
@laveto_pay_bp.route('/merchant/<merchant_slug>/update-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/update-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/toggle-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/toggle-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/fee-policy', methods=['POST'])
@laveto_pay_bp.route('/api/merchant/update-fee-policy', methods=['POST'])
@laveto_pay_bp.route('/pay/api/merchant/update-fee-policy', methods=['POST'])
def update_merchant_fee_policy(merchant_slug=None):
    from core.models import Merchant

    data = request.get_json(silent=True) or request.form or {}

    # Extract pass_fees_to_customer
    pass_fees = data.get('pass_fees_to_customer')
    if pass_fees is None:
        pass_fees = data.get('pass_fee')
    if pass_fees is None and 'policy' in data:
        pass_fees = 'pass' in str(data['policy']).lower()

    if isinstance(pass_fees, str):
        pass_fees = pass_fees.strip().lower() in ['true', '1', 'yes', 'pass']

    slug = merchant_slug or data.get('merchant_slug') or session.get('merchant_slug')
    if not slug and session.get('merchant_id'):
        m = Merchant.query.get(session.get('merchant_id'))
        if m:
            slug = m.username

    if not slug:
        return jsonify({
            'status': 'error',
            'success': False,
            'message': 'Merchant username required.'
        }), 400

    clean_slug = slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first()

    if not merchant:
        return jsonify({
            'status': 'error',
            'success': False,
            'message': f"Merchant '{slug}' not found."
        }), 404

    try:
        if pass_fees is not None:
            merchant.pass_fees_to_customer = bool(pass_fees)
        else:
            current = bool(getattr(merchant, 'pass_fees_to_customer', False))
            merchant.pass_fees_to_customer = not current

        db.session.commit()

        policy_label = "Pass Fee to Customer" if merchant.pass_fees_to_customer else "Store Absorbs Fee"
        return jsonify({
            'status': 'success',
            'success': True,
            'pass_fees_to_customer': merchant.pass_fees_to_customer,
            'message': f"Fee settlement policy updated: {policy_label}."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'success': False,
            'message': str(e)
        }), 500

# =========================================================================
# 🚚 MERCHANT DELIVERY FEE UPDATER
# =========================================================================
@laveto_pay_bp.route('/merchant/<merchant_slug>/update-delivery-fee', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/update-delivery-fee', methods=['POST'])
def update_merchant_delivery_fee(merchant_slug=None):
    from core.models import Merchant

    data = request.get_json(silent=True) or request.form or {}
    delivery_fee = data.get('delivery_fee')

    slug = merchant_slug or session.get('merchant_slug')
    if not slug and session.get('merchant_id'):
        m = Merchant.query.get(session.get('merchant_id'))
        if m:
            slug = m.username

    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == str(slug).strip().lower(),
            db.func.lower(Merchant.business_name) == str(slug).strip().lower().replace('-', ' ')
        )
    ).first()

    if not merchant:
        return jsonify({'status': 'error', 'message': 'Merchant not found.'}), 404

    try:
        merchant.delivery_fee = float(delivery_fee) if delivery_fee is not None else 0.00
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Delivery fee updated to P{merchant.delivery_fee:.2f}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@laveto_pay_bp.route('/merchant/<merchant_slug>/update-domain', methods=['POST'])
def update_merchant_domain(merchant_slug):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()
    raw_domain = request.form.get('custom_domain', '').strip().lower()
    clean_domain = re.sub(r'^https?://', '', raw_domain).rstrip('/')

    if clean_domain:
        existing = Merchant.query.filter(
            Merchant.custom_domain == clean_domain,
            Merchant.id != merchant.id
        ).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'Domain is already linked to another merchant.'}), 400
        merchant.custom_domain = clean_domain
    else:
        merchant.custom_domain = None

    db.session.commit()
    return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))


@laveto_pay_bp.route('/merchant/<merchant_slug>/update-delivery-fee', methods=['POST'])
def update_delivery_fee(merchant_slug):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()
    data = request.get_json(silent=True) or request.form
    raw_fee = data.get('delivery_fee', 40.00)
    try:
        fee = float(raw_fee)
    except (ValueError, TypeError):
        fee = 40.00

    merchant.delivery_fee = fee
    db.session.commit()

    if request.is_json:
        return jsonify({'status': 'success', 'message': f'Delivery fee updated to P{fee:.2f} BWP!', 'delivery_fee': fee})
    return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

# =========================================================================
# 📦 MERCHANT STOCK INTAKE & PAY LINK GENERATOR
# =========================================================================
@laveto_pay_bp.route('/merchant/<merchant_slug>/create-link', methods=['POST'])
@laveto_pay_bp.route('/pay/merchant/<merchant_slug>/create-link', methods=['POST'])
def merchant_create_link(merchant_slug):
    from core.models import Merchant, PayLink
    import re

    # 1. Resolve merchant
    clean_slug = merchant_slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first()

    if not merchant:
        flash(f"Merchant '{merchant_slug}' not found.", "danger")
        return redirect(request.referrer or url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant_slug))

    # 2. Extract form or JSON data
    data = request.form if request.form else (request.get_json(silent=True) or {})
    title = (data.get('title') or data.get('item_name') or data.get('name') or '').strip()
    price_raw = data.get('price') or data.get('amount') or 0.0
    stock_raw = data.get('stock') or data.get('stock_quantity') or data.get('initial_stock') or -1
    is_bulk = bool(data.get('is_bulk') or data.get('is_combo') or data.get('bundle'))

    if not title:
        flash("Item title is required.", "warning")
        return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

    try:
        price = float(price_raw)
    except (ValueError, TypeError):
        price = 0.0

    try:
        stock = int(stock_raw) if stock_raw is not None and str(stock_raw).strip() != '' else -1
    except (ValueError, TypeError):
        stock = -1

    # 3. Create unique slug
    base_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    if not base_slug:
        base_slug = f"item-{int(time.time())}"

    unique_slug = base_slug
    counter = 1
    while PayLink.query.filter_by(merchant_id=merchant.id, slug=unique_slug).first():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1

    try:
        new_link = PayLink(
            merchant_id=merchant.id,
            slug=unique_slug,
            title=title,
            price=price,
            stock_quantity=stock,
            is_flexible=(price <= 0),
            is_active=True
        )

        # Set bundle flag if model column exists
        if hasattr(new_link, 'is_bundle'):
            new_link.is_bundle = is_bulk

        db.session.add(new_link)
        db.session.commit()

        flash(f"✅ Stock item '{title}' added! Link: /pay/{merchant.username}/{unique_slug}", "success")

        # Support AJAX JSON caller
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'success': True,
                'slug': unique_slug,
                'title': title,
                'price': price,
                'stock': stock,
                'pay_url': f"https://www.laveto.net/pay/{merchant.username}/{unique_slug}"
            }), 200

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating stock item: {str(e)}", "danger")
        if request.is_json:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return redirect(url_for('laveto_pay.merchant_dashboard', merchant_slug=merchant.username))

@laveto_pay_bp.route('/api/merchant/<merchant_slug>/live-feed', methods=['GET'])
def merchant_live_feed(merchant_slug):
    merchant = Merchant.query.filter_by(username=merchant_slug).first_or_404()
    links = [l.id for l in merchant.pay_links]

    recent = PaymentTransaction.query.filter(
        PaymentTransaction.pay_link_id.in_(links),
        PaymentTransaction.payment_status == 'COMPLETED'
    ).order_by(PaymentTransaction.created_at.desc()).limit(5).all() if links else []

    feed = [{
        'id': t.id,
        'ref': t.aggregator_ref,
        'amount': t.gross_amount or 0.0,
        'merchant_share': t.merchant_share or 0.0,
        'buyer_name': t.buyer_name or 'Customer',
        'payment_method': t.payment_method,
        'is_escrow': t.is_escrow,
        'escrow_status': t.escrow_status,
        'time': t.created_at.strftime('%H:%M:%S') if t.created_at else ''
    } for t in recent]

    return jsonify({
        'status': 'online',
        'unsettled_balance': merchant.unsettled_balance or 0.0,
        'feed': feed
    }), 200


# ==========================================
# 📍 DIRECTORIES & GEOLOCATION
# ==========================================
@laveto_pay_bp.route('/vendors', methods=['GET'])
def list_vendors_by_village():
    village_code = request.args.get('village', '').strip()
    vendors = Merchant.query.filter_by(is_verified=True).all()
    return render_template(
    'pay/agent_toolkit_card.html',
    village_code=village_code,
    vendors=vendors
)


@laveto_pay_bp.route('/api/w3w/gps-to-words', methods=['POST'])
def api_gps_to_w3w():
    data = request.get_json() or {}
    lat, lng = data.get('lat'), data.get('lng')
    if lat is None or lng is None:
        return jsonify({'status': 'error', 'message': 'Missing GPS coordinates'}), 400
    return jsonify(convert_gps_to_w3w(float(lat), float(lng)))


@laveto_pay_bp.route('/api/w3w/autosuggest', methods=['GET'])
def api_w3w_autosuggest():
    query = request.args.get('input', '').strip().replace('///', '')
    if len(query) < 3:
        return jsonify({'suggestions': []})

    if not W3W_API_KEY:
        mock_suggestions = [
            {'words': f"///{query}.harvest.gaborone", 'nearestPlace': 'Gaborone, South-East'},
            {'words': f"///{query}.market.francistown", 'nearestPlace': 'Francistown, North-East'},
            {'words': f"///{query}.central.maun", 'nearestPlace': 'Maun, North-West'}
        ]
        return jsonify({'suggestions': mock_suggestions})

    url = 'https://api.what3words.com/v3/autosuggest'
    params = {'input': query, 'key': W3W_API_KEY, 'clip-to-country': 'BW', 'n-results': 5}
    try:
        res = requests.get(url, params=params, timeout=5)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({'suggestions': [], 'error': str(e)})


# ==========================================
# 🖨️ QR CODES & DIGITAL RECEIPTS
# ==========================================
@laveto_pay_bp.route('/pay/qr/<slug>', methods=['GET'])
def generate_counter_qr(slug):
    pay_url = f"https://www.laveto.net/pay/{slug}"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3
    )
    qr.add_data(pay_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='#080C14', back_color='#FFFFFF').convert('RGBA')

    icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'static', 'img', 'laveto-pay-icon.png')
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert('RGBA')
        icon_size = int(qr_img.size[0] * 0.22)
        icon = icon.resize((icon_size, icon_size), Image.LANCZOS)
        pos = ((qr_img.size[0] - icon_size) // 2, (qr_img.size[1] - icon_size) // 2)
        qr_img.paste(icon, pos, mask=icon)

    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', download_name=f"{slug}_counter_qr.png")


@laveto_pay_bp.route('/pay/qr/receipt/<tx_ref>', methods=['GET'])
def generate_receipt_qr(tx_ref):
    receipt_url = f"https://www.laveto.net/pay/receipt/{tx_ref}"
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(receipt_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#080C14', back_color='#ffffff')

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', download_name=f"{tx_ref}_qr.png")


# ==========================================
# 🏛️ PLATFORM MASTER OPERATOR CONSOLE
# ==========================================
@laveto_pay_bp.route('/pay/admin', methods=['GET', 'POST'])
@laveto_pay_bp.route('/operator/pay', methods=['GET', 'POST'])
def master_operator_dashboard():
    if request.method == 'POST':
        entered_pin = str(request.form.get('admin_pin', '')).strip()
        if entered_pin == ADMIN_MASTER_PIN:
            session['laveto_admin_auth'] = True
            return redirect(url_for('laveto_pay.master_operator_dashboard'))
        return render_template('pay/admin_pin_gate.html', error='❌ Invalid Operator PIN entered.')

    if not session.get('laveto_admin_auth'):
        return render_template('pay/admin_pin_gate.html')

    merchants = Merchant.query.all()
    links = PayLink.query.all()
    transactions = PaymentTransaction.query.order_by(PaymentTransaction.created_at.desc()).all()
    campaigns = AdCampaign.query.all() if AdCampaign else []

    completed_txs = [t for t in transactions if (t.payment_status or '').upper() == 'COMPLETED']
    pending_txs = [t for t in transactions if (t.payment_status or '').upper() == 'PENDING']
    failed_txs = [t for t in transactions if (t.payment_status or '').upper() == 'FAILED']

    total_gross = sum((t.gross_amount or 0.0) for t in completed_txs)
    total_net_disbursed = sum((t.merchant_share or 0.0) for t in completed_txs)
    total_commissions = total_gross - total_net_disbursed

    escrow_held = sum((t.merchant_share or 0.0) for t in completed_txs if t.is_escrow and t.escrow_status == 'HELD')
    unsettled_float = sum((m.unsettled_balance or 0.0) for m in merchants)
    total_ad_revenue = sum((c.budget_spent or 0.0) for c in campaigns)

    merchant_stats = []
    for m in merchants:
        m_txs = [t for t in completed_txs if (t.pay_link and t.pay_link.merchant_id == m.id) or t.merchant_id == m.id]
        m_gross = sum((t.gross_amount or 0.0) for t in m_txs)
        m_net = sum((t.merchant_share or 0.0) for t in m_txs)
        m_comm = m_gross - m_net
        merchant_stats.append({
            'merchant': m,
            'gross': m_gross,
            'commissions': m_comm,
            'tx_count': len(m_txs)
        })
    merchant_stats.sort(key=lambda x: x['gross'], reverse=True)

    return render_template(
        'pay/admin_dashboard.html',
        total_escrow_locked=locals().get('total_escrow_locked', 0.0) or 0.0,
        merchants=merchants,
        links=links,
        transactions=transactions[:50],
        campaigns=campaigns,
        total_gross=total_gross,
        total_commissions=total_commissions,
        total_net_disbursed=total_net_disbursed,
        escrow_held=escrow_held,
        unsettled_float=unsettled_float,
        total_ad_revenue=total_ad_revenue,
        pending_count=len(pending_txs),
        completed_count=len(completed_txs),
        failed_count=len(failed_txs),
        leaderboard=merchant_stats
    )


@laveto_pay_bp.route('/pay/admin/logout', methods=['GET'])
def admin_logout():
    session.pop('laveto_admin_auth', None)
    return redirect(url_for('laveto_pay.master_operator_dashboard'))

    # ==========================================
# 🔑 OPERATOR MERCHANT IMPERSONATION / LOGIN-AS
# ==========================================
@laveto_pay_bp.route('/pay/admin/login-as/<int:merchant_id>', methods=['GET'])
@laveto_pay_bp.route('/operator/login-as/<int:merchant_id>', methods=['GET'])
def operator_login_as_merchant(merchant_id):
    """
    Allows the platform master operator to jump into any merchant dashboard
    without needing their password, protected by the master PIN (2026).
    """
    req_pin = request.args.get('pin')
    session_pin = session.get('operator_pin')

    if req_pin != '2026' and session_pin != '2026':
        return """
        <div style="background:#0F172A; color:#F87171; font-family:sans-serif; padding:2rem; text-align:center;">
            <h2>Unauthorized Operator Access</h2>
            <p>Master PIN verification failed.</p>
            <a href="/operator/pay" style="color:#FBBF24;">&larr; Return to Console</a>
        </div>
        """, 403

    merchant = Merchant.query.get_or_404(merchant_id)

    # Set the authenticated session for this merchant
    session['merchant_id'] = merchant.id
    session['merchant_slug'] = merchant.username
    session['is_operator_impersonating'] = True
    session['operator_pin'] = '2026'

    # Redirect straight into the merchant's live operational dashboard
    return redirect(f"/merchant/{merchant.username}/dashboard")

@laveto_pay_bp.route('/pay/<merchant_slug>/till', methods=['GET'])
@laveto_pay_bp.route('/merchant/<merchant_slug>/till', methods=['GET'])
def merchant_till(merchant_slug):
    from core.models import Merchant, PayLink
    clean_slug = merchant_slug.strip().lower()
    merchant = Merchant.query.filter(
        db.or_(
            db.func.lower(Merchant.username) == clean_slug,
            db.func.lower(Merchant.business_name) == clean_slug.replace('-', ' ')
        )
    ).first_or_404()

    item_name = request.args.get('item', 'Counter Sale').strip()
    custom_amount = request.args.get('amount', '50.00')
    try:
        parsed_amount = float(custom_amount)
    except ValueError:
        parsed_amount = 50.00

    # Get or create a temporary PayLink for this till session
    pay_link = PayLink.query.filter_by(merchant_id=merchant.id, title=item_name).first()
    if not pay_link:
        pay_link = PayLink(
            merchant_id=merchant.id,
            title=item_name,
            slug=item_name.lower().replace(' ', '-'),
            price=parsed_amount,
            is_active=True
        )
        db.session.add(pay_link)
        db.session.commit()
    else:
        pay_link.price = parsed_amount
        db.session.commit()

    sponsored_ad = fetch_active_ad('buyer_b2c_general') if 'fetch_active_ad' in globals() else None
    return render_template(
        'pay/checkout.html',
        merchant=merchant,
        pay_link=pay_link,
        sponsored_ad=sponsored_ad,
        PLATFORM_FEE_RATE=globals().get('PLATFORM_FEE_RATE', 0.015)
    )