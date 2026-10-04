from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from core.decorators import admin_only

scrap_bp = Blueprint('scrap_treasury', __name__)

@scrap_bp.route('/', methods=['GET'])
@scrap_bp.route('/inventory', methods=['GET'])
def scrap_inventory():
    return jsonify({
        "status": "ONLINE",
        "module": "scrap_treasury",
        "salvage_vault": "ACTIVE",
        "items": []
    }), 200

@scrap_bp.route('/valuation', methods=['POST'])
def estimate_scrap_value():
    data = request.get_json() or {}
    metal_type = data.get("metal_type", "STEEL")
    weight_kg = float(data.get("weight_kg", 0.0))
    
    # Base rates per KG in BWP
    rate_map = {
        "STEEL": 4.50,
        "ALUMINUM": 18.20,
        "COPPER": 75.00,
        "CATALYTIC_CONVERTER": 450.00
    }
    unit_rate = rate_map.get(metal_type.upper(), 3.50)
    estimated_pula = round(weight_kg * unit_rate, 2)
    
    return jsonify({
        "status": "SUCCESS",
        "metal_type": metal_type,
        "weight_kg": weight_kg,
        "unit_rate_bwp": unit_rate,
        "estimated_value_bwp": estimated_pula
    }), 200

@scrap_bp.route('/status', methods=['GET'])
def scrap_status():
    return jsonify({
        "status": "OPERATIONAL",
        "bridge": "SOVEREIGN_SCRAP_TREASURY_v1"
    }), 200
