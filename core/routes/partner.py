from flask import Blueprint, jsonify
partner_bp = Blueprint('partner', __name__)
@partner_bp.route('/partner/status', methods=['GET'])
def partner_status():
    return jsonify({"status": "active"}), 200
