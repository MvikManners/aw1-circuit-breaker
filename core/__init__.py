import os
from flask import Flask, url_for, redirect
from .config import Config, basedir
from .extensions import db, mail, login_manager, csrf, init_extensions

# 🟢 GLOBAL CLOUD SECURITY
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/LavetoLab/credentials.json"

def create_app(config_class=Config):
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    # 🟢 FORENSIC DATABASE STABILIZATION
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Initialize Extensions using the consolidated factory function
    init_extensions(app)

    # Register Blueprints
    from .routes.hangar import hangar_bp
    from .routes.auth import auth_bp
    from .routes.treasury import treasury_bp

    # Ensure clean URL namespaces
    app.register_blueprint(hangar_bp, url_prefix='/hangar')
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(treasury_bp, url_prefix='/treasury')

    # 🚀 THE ROOT BRIDGE
    @app.route('/')
    def root_domain():
        return redirect(url_for('hangar.index'))

    # 🛰️ THE SUB-CONSCIOUS WELD (Context Processor)
    @app.context_processor
    def inject_system_stats():
        stats = {
            "liquidation_requests": 0,
            "bleeding_count": 0,
            "quarantine_count": 0,
            "pending_mandates": 0
        }
        try:
            from core.models.vehicles import SovereignLedger
            from core.models.finance import Prospect, StopOrderMandate
            from sqlalchemy import or_

            stats["liquidation_requests"] = SovereignLedger.query.filter(
                or_(
                    SovereignLedger.current_status.ilike('%SALE%'),
                    SovereignLedger.current_status.ilike('%LIQUIDATION%')
                )
            ).count()

            stats["bleeding_count"] = SovereignLedger.query.filter(
                getattr(SovereignLedger, 'health_score', 0) <= 20
            ).count()

            stats["quarantine_count"] = Prospect.query.filter_by(status='PENDING').count()

            # Payroll Alert: Count all newly signed mandates
            stats["pending_mandates"] = StopOrderMandate.query.filter_by(status='ACTIVE').count()

        except Exception as e:
            print(f"[SYSTEM_STATS_FAILURE]: {str(e)}")

        return stats

    # 🕵️ DEBUG: Print all registered routes
    with app.app_context():
        print("--- REGISTERED ENDPOINTS ---")
        for rule in app.url_map.iter_rules():
            print(f"Endpoint: {rule.endpoint} | Route: {rule.rule}")
        print("----------------------------")

    return app