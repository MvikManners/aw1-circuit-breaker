from core.routes.partner import partner_bp
# /home/LavetoLab/core/__init__.py
import os
import time
import traceback
import re
from datetime import datetime, timedelta, timezone
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    g,
    send_from_directory,
    make_response
)
from flask.sessions import NullSession, SecureCookieSession
from jinja2 import ChoiceLoader, FileSystemLoader
from dotenv import load_dotenv
from flask_session import Session
from flask_login import current_user, login_required
from sqlalchemy import text

# 1. Extensions & DB initialized first
from core.extensions import db, init_extensions

# 2. Application Config
from .config import Config, basedir

# 3. Import Latency Router & Semantic Entropy Filter Module
try:
    from routes_latency_and_entropy import LatencyRouter, SemanticEntropyFilter
except (ImportError, ModuleNotFoundError):
    class LatencyRouter:
        pass
    class SemanticEntropyFilter:
        pass

try:
    import google.genai as genai
    GOOGLE_GENAI_ENABLED = True
except ImportError:
    genai = None
    GOOGLE_GENAI_ENABLED = False
    print("WARNING: google.genai package is not installed. AI features will be disabled.")

_stats_cache = {"data": None, "last_updated": 0}

def get_safe_utc_now():
    """Returns a consistent offset-naive UTC datetime to prevent subtraction errors."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_app(config_class=Config):
    dotenv_path = '/home/LavetoLab/.env'
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/LavetoLab/google_key.json"

    root_templates = os.path.join(basedir, 'templates')
    core_templates = os.path.join(basedir, 'core', 'templates')
    static_dir = os.path.join(basedir, 'static')

    app = Flask(__name__, static_folder=static_dir, template_folder=root_templates)
    app.config.from_object(config_class)

    app.secret_key = 'LAVETO-GOSPEL-OS-SECURE-KEY-99'
    app.config['SECRET_KEY'] = 'LAVETO-GOSPEL-OS-SECURE-KEY-99'

    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'pool_reset_on_return': 'rollback',
        'connect_args': {'connect_timeout': 10}
    }

    init_extensions(app)

    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'

    try:
        Session(app)
    except Exception:
        pass

    original_open_session = app.session_interface.open_session

    def safe_open_session(app_instance, req):
        try:
            sess = original_open_session(app_instance, req)
            if sess is None:
                return SecureCookieSession()
            return sess
        except Exception:
            try:
                db.session.rollback()
                db.engine.dispose()
            except Exception:
                pass
            return SecureCookieSession()

    app.session_interface.open_session = safe_open_session

    with app.app_context():
        db.create_all()

    app.jinja_loader = ChoiceLoader([FileSystemLoader(root_templates), FileSystemLoader(core_templates)])

    from .routes.hangar import hangar_bp
    from .routes.auth import auth_bp
    from .routes.treasury import treasury_bp
    from .routes.audit import audit_bp
    from .routes.silk_road import silk_road_bp
    from .routes.scrap_treasury import scrap_bp
    from .routes.laveto_pay import laveto_pay_bp
    from core.routes.spark_assistant import spark_bp

    app.register_blueprint(spark_bp)
    app.register_blueprint(silk_road_bp, url_prefix='/silk_road')
    app.register_blueprint(audit_bp, url_prefix='/audit')
    app.register_blueprint(hangar_bp, url_prefix='/hangar')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(treasury_bp, url_prefix='/treasury')
    app.register_blueprint(scrap_bp, url_prefix='/api/scrap')
    app.register_blueprint(laveto_pay_bp)

    # Register Laveto Wisdom AW Blueprint
    from laveto_wisdom.routes import wisdom_bp
    app.register_blueprint(wisdom_bp, url_prefix='/wisdom')

    # =========================================================================
    # ⚡ AW-1 ZERO-TRUST LATENCY ROUTER & SEMANTIC ENTROPY FILTER ENDPOINTS
    # =========================================================================
    @app.route("/v1/aw/intercept", methods=["POST"])
    def intercept_action():
        payload = request.get_json() or {}
        decision = LatencyRouter.route_request(payload)
        return jsonify(decision), 200

    @app.route("/v1/aw/pouc/submit", methods=["POST"])
    def evaluate_submission():
        payload = request.get_json() or {}
        embedding = payload.get("submission_embedding", [])
        risk_severity = payload.get("uncovered_risk_severity", 0.0)

        result = SemanticEntropyFilter.evaluate_submission(embedding, risk_severity)
        return jsonify(result), 200

    # =========================================================================
    # 🌐 V3 WHITE-LABEL HOST INTERCEPTION MIDDLEWARE
    # =========================================================================
    PRIMARY_PLATFORM_HOSTS = {
        'laveto.net',
        'www.laveto.net',
        'p20.laveto.net',
        'pay.laveto.net',
        'dashboard.laveto.net',
        'localhost',
        '127.0.0.1'
    }

    @app.before_request
    def intercept_custom_domain_hosts():
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            try:
                db.session.rollback()
                db.engine.dispose()
            except Exception:
                pass

        raw_host = request.host.lower().split(':')[0]

        if raw_host in PRIMARY_PLATFORM_HOSTS or raw_host.endswith('.pythonanywhere.com'):
            return None

        if (
            request.path.startswith('/static/') or
            request.path.startswith('/pay/') or
            request.path.startswith('/wisdom') or
            request.path.startswith('/nexus') or
            request.path.startswith('/ledger') or
            request.path in ['/manifest.json', '/sw.js', '/favicon.ico', '/checkout/initiate', '/payment/callback']
        ):
            return None

        from core.models import Merchant, PayLink
        merchant = Merchant.query.filter(
            (Merchant.custom_domain == raw_host) |
            (Merchant.custom_domain == f"www.{raw_host}") |
            (Merchant.custom_domain == raw_host.replace('www.', ''))
        ).first()

        if not merchant:
            return None

        clean_path = request.path.strip('/')

        if not clean_path:
            pay_link = PayLink.query.filter_by(merchant_id=merchant.id, is_flexible=True, is_active=True).first()
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
            return render_template('pay/checkout.html', merchant=merchant, pay_link=pay_link, link=pay_link)

        pay_link = PayLink.query.filter_by(merchant_id=merchant.id, slug=clean_path, is_active=True).first()
        if pay_link:
            return render_template('pay/checkout.html', merchant=merchant, pay_link=pay_link, link=pay_link)

        return render_template('pay/checkout.html', merchant=merchant, pay_link=None, link=None), 404

    @app.after_request
    def emergency_flask_login_shield(response):
        try:
            import flask
            if session is None:
                if hasattr(flask, 'request_ctx') and flask.request_ctx:
                    flask.request_ctx.session = NullSession()
                elif hasattr(flask, '_request_ctx_stack') and flask._request_ctx_stack.top:
                    flask._request_ctx_stack.top.session = NullSession()
        except Exception:
            pass
        return response

    # =========================================================================
    # 📱 PWA SYSTEM ASSET ROUTERS
    # =========================================================================
    @app.route('/manifest.json')
    def pwa_manifest():
        return send_from_directory(static_dir, 'manifest.json', mimetype='application/manifest+json')

    @app.route('/sw.js')
    def pwa_service_worker():
        response = make_response(send_from_directory(static_dir, 'sw.js', mimetype='application/javascript'))
        response.headers['Service-Worker-Allowed'] = '/'
        return response

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(static_dir, 'img'),
            'laveto-nexus-emblem.svg',
            mimetype='image/svg+xml'
        )

    # ROOT & SHORTCUT ROUTE HANDLERS
    @app.route('/')
    def index():
        return render_template('nexus.html')

    @app.route('/nexus')
    @app.route('/nexus/')
    @app.route('/ledger')
    @app.route('/ledger/')
    def village_ledger():
        return render_template('nexus.html')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            if exception:
                try:
                    db.session.rollback()
                except Exception:
                    db.engine.dispose()
            db.session.remove()
        except Exception:
            try:
                db.engine.dispose()
            except Exception:
                pass
            db.session.remove()

    @app.route('/login')
    def root_login():
        return redirect(url_for('auth.login'))

    @app.route('/logout')
    def root_logout():
        return redirect(url_for('auth.logout'))

    @app.context_processor
    def inject_system_stats():
        from core.utils import get_system_counts
        global _stats_cache
        current_time = time.time()
        if current_time - _stats_cache["last_updated"] > 300 or _stats_cache["data"] is None:
            _stats_cache["data"] = get_system_counts()
            _stats_cache["last_updated"] = current_time
        return _stats_cache["data"]

    @app.route('/pay/receipt/<string:ref>')
    def global_view_receipt(ref):
        from core.models import PaymentTransaction, Merchant
        tx = None
        if ref.isdigit():
            tx = PaymentTransaction.query.get(int(ref))
        else:
            tx = PaymentTransaction.query.filter_by(aggregator_ref=ref).first()
            if not tx and hasattr(PaymentTransaction, 'order_ref'):
                tx = PaymentTransaction.query.filter_by(order_ref=ref).first()
        if not tx:
            return f"Receipt/Invoice not found for reference: {ref}", 404
        merchant = Merchant.query.get(tx.merchant_id) if tx.merchant_id else None
        return render_template('pay/receipt.html', tx=tx, merchant=merchant)

   # =========================================================================
    # 🏪 STOREFRONT & CHECKOUT ROUTING SEPARATION
    # =========================================================================
    @app.route('/pay/<string:username>')
    @app.route('/pay/<string:username>/')
    def global_merchant_storefront(username):
        clean_user = username.strip().lower()

        # 1. Blueprint feature endpoints & subpath pass-throughs
        if clean_user == 'ads':
            return redirect(url_for('laveto_pay.ads_promote'))
        if clean_user == 'basket':
            return redirect(url_for('laveto_pay.smart_basket_portal'))
        if clean_user == 'admin':
            return redirect(url_for('laveto_pay.admin_onboarding'))

        # 2. Reserved system words (prevent interpreting system prefixes as merchant slugs)
        if clean_user in ['merchant', 'qr', 'api', 'checkout', 'receipt', 'invoice', 'static', 'auth']:
            return redirect(url_for('index'))

        from core.models import Merchant, PayLink

        # 3. Resolve Merchant
        merchant = Merchant.query.filter(
            db.or_(
                db.func.lower(Merchant.username) == clean_user,
                db.func.lower(Merchant.username).like(f"%{clean_user}%"),
                db.func.lower(Merchant.business_name).like(f"%{clean_user.replace('-', ' ')}%")
            )
        ).first()

        if not merchant:
            return f"Merchant profile not found for: {username}", 404

        links = PayLink.query.filter_by(merchant_id=merchant.id, is_active=True).all() if getattr(merchant, 'id', None) else []
        return render_template('pay/storefront.html', merchant=merchant, links=links)

    @app.route('/pay/<string:username>/till')
    @app.route('/pay/<string:username>/till/')
    @app.route('/pay/<string:username>/checkout')
    @app.route('/pay/<string:username>/checkout/')
    def global_merchant_shortcut(username):
        from core.models import Merchant, PayLink
        clean_user = username.strip().lower()

        if clean_user in ['admin', 'ads', 'checkout', 'api', 'receipt', 'invoice', 'static', 'auth', 'basket']:
            return redirect(url_for('index'))

        merchant = None
        is_dummy = False

        try:
            merchant = Merchant.query.filter(
                db.or_(
                    db.func.lower(Merchant.username) == clean_user,
                    db.func.lower(Merchant.username).like(f"%{clean_user}%"),
                    db.func.lower(Merchant.business_name).like(f"%{clean_user.replace('-', ' ')}%")
                )
            ).first()
        except Exception:
            pass

        if not merchant:
            try:
                logged_id = session.get('merchant_id')
                if logged_id:
                    merchant = Merchant.query.filter_by(id=logged_id).first()
                if not merchant:
                    merchant = Merchant.query.first()
            except Exception:
                pass

        if not merchant:
            is_dummy = True
            class DummyMerchant:
                id = None
                username = clean_user
                business_name = clean_user.replace('-', ' ').title()
                phone_number = '+26772000000'
                settlement_provider = 'Orange Money'
                settlement_wallet = '72000000'
                is_verified = True
                pass_fees_to_customer = False
                delivery_fee = 40.00
            merchant = DummyMerchant()

        custom_item = request.args.get('item')
        custom_amount = request.args.get('amount')

        if custom_item or custom_amount:
            class DynamicPosLink:
                def __init__(self, item_name, price_val):
                    self.id = 0
                    self.title = item_name or f"{merchant.business_name} Counter Till"
                    try:
                        self.price = float(price_val) if price_val else 0.0
                    except (ValueError, TypeError):
                        self.price = 0.0
                    self.slug = 'till'
                    self.is_flexible = True
            link = DynamicPosLink(custom_item, custom_amount)
        else:
            link = None
            if not is_dummy and hasattr(merchant, 'id') and merchant.id:
                try:
                    link = PayLink.query.filter_by(merchant_id=merchant.id).first()
                except Exception:
                    pass

        if not link:
            class DummyLink:
                def __init__(self):
                    self.id = 0
                    self.title = f"{merchant.business_name} Till"
                    self.price = 0.0
                    self.is_flexible = True
                    self.slug = 'till'
            link = DummyLink()

        delivery_fee = float(getattr(merchant, 'delivery_fee', 40.00) or 40.00)

        return render_template(
            'pay/checkout.html',
            merchant=merchant,
            pay_link=link,
            link=link,
            dynamic_delivery_fee=delivery_fee
        )

    @app.route("/store/system-restoration")
    def root_store_redirect():
        from flask import redirect
        return redirect("/wisdom/store/system-restoration")

    app.register_blueprint(partner_bp)
    return app