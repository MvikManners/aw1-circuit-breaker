from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from core.models.vehicles import SovereignLedger, GhostOrder, SupplierDirectory, AuditLog
from core.models.finance import CorporateTreasury
from core.extensions import db

silk_road_bp = Blueprint('silk_road', __name__)

# core/routes/silk_road.py

@silk_road_bp.route('/finalize_deployment/<int:order_id>', methods=['POST'], endpoint='finalize_deployment')
def finalize_deployment(order_id):
    order = GhostOrder.query.get_or_404(order_id)
    treasury = CorporateTreasury.query.first()

    if not treasury:
        flash("🚨 CRITICAL: Treasury registry missing.", "error")
        return redirect(url_for('silk_road.procurement_hub'))

    if treasury.scrap_reclamation_profits >= order.estimated_cost:
        treasury.scrap_reclamation_profits -= order.estimated_cost
        order.status = 'DEPLOYED'

        ledger = SovereignLedger.query.get(order.ledger_id)
        if ledger:
            ledger.current_status = 'ACTIVE'

            # 🟢 ADD THIS HERE IN YOUR PYTHON FILE
            audit = AuditLog(
                vin_dna=ledger.vin_dna,
                action=f"SILK_ROAD_SETTLEMENT: {order.component_name} | Cost: {order.estimated_cost}",
                audit_score=1.0,
                status="SETTLED",
                timestamp=datetime.utcnow()
            )
            db.session.add(audit)

        db.session.commit()
        flash(f"Deployment confirmed.", "success")
    else:
        flash("🚨 INSUFFICIENT FUNDS.", "error")

    return redirect(url_for('silk_road.procurement_hub'))

@silk_road_bp.route('/procurement_hub', endpoint='procurement_hub')
def procurement_hub():
    """Central logistics dashboard for active Ghost Orders."""
    active_orders = GhostOrder.query.order_by(GhostOrder.date_logged.desc()).all()
    suppliers = SupplierDirectory.query.filter_by(is_active=True).all()

    return render_template('silk_road.html', orders=active_orders, suppliers=suppliers)

@silk_road_bp.route('/dispatch_order/<int:ledger_id>', methods=['POST'], endpoint='dispatch_order')
def dispatch_order(ledger_id):
    """Generates a new GhostOrder linked to a vehicle node."""
    ledger = SovereignLedger.query.get_or_404(ledger_id)

    new_order = GhostOrder(
        ledger_id=ledger.id,
        component_name=request.form.get('component_name'),
        status='PENDING ORDER',
        supplier=request.form.get('supplier_name'),
        estimated_cost=float(request.form.get('cost', 0.0))
    )

    db.session.add(new_order)
    db.session.commit()

    flash(f"Logistics rail engaged for {ledger.vin_dna}", "success")
    return redirect(url_for('silk_road.procurement_hub'))