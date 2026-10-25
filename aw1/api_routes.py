"""
aw1.api_routes
~~~~~~~~~~~~~~
REST API Endpoints for Institutional Compliance Auditing.
Exposes endpoints for Bank of Botswana 1-to-1 Trust Verification and CEDA Statutory Assessment.
"""

from flask import Blueprint, request, jsonify
from aw1.trust_reconciliation import TrustAccountReconciliationEngine
from aw1.sandbox_profile import InstitutionalPilotSuite

compliance_bp = Blueprint('compliance_api', __name__, url_prefix='/wisdom/api/v1/compliance')


@compliance_bp.route('/trust-audit', methods=['POST'])
def trust_audit():
    """
    Ingests daily bank settlement balances and verifies 1-to-1 backing under BoB NCSS.
    Expected JSON:
    {
        "audit_date": "YYYY-MM-DD",
        "custodian_bank": "Bank Name",
        "escrow_fiat_balance_bwp": float,
        "circulating_float_bwp": float,
        "pending_settlements_bwp": float (optional)
    }
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    required = ["audit_date", "custodian_bank", "escrow_fiat_balance_bwp", "circulating_float_bwp"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        result = TrustAccountReconciliationEngine.audit_daily_trust_balance(
            audit_date=str(data['audit_date']),
            custodian_bank_name=str(data['custodian_bank']),
            escrow_fiat_balance_bwp=float(data['escrow_fiat_balance_bwp']),
            circulating_float_bwp=float(data['circulating_float_bwp']),
            pending_outbound_settlements_bwp=float(data.get('pending_settlements_bwp', 0.0))
        )
        status_code = 200 if result['runtime_posture'] == 'PROCEED' else 422
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@compliance_bp.route('/ceda-audit', methods=['POST'])
def ceda_audit():
    """
    Ingests credit facility applications and verifies citizen equity quota under CEE Act 2022.
    Expected JSON:
    {
        "applicant_id": str,
        "loan_amount_bwp": float,
        "citizen_equity_ratio": float,
        "proposed_action_payload": str
    }
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    required = ["applicant_id", "loan_amount_bwp", "citizen_equity_ratio", "proposed_action_payload"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        result = InstitutionalPilotSuite.evaluate_ceda_loan_application(
            applicant_id=str(data['applicant_id']),
            loan_amount_bwp=float(data['loan_amount_bwp']),
            citizen_equity_ratio=float(data['citizen_equity_ratio']),
            proposed_action_payload=str(data['proposed_action_payload'])
        )
        status_code = 200 if result['runtime_posture'] == 'PROCEED' else 422
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
