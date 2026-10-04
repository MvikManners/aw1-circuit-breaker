from flask import Blueprint, jsonify
lemon_webhook_bp = Blueprint('lemon_webhook', __name__)
@lemon_webhook_bp.route('/webhook/lemonsqueezy', methods=['POST'])
def lemon_callback():
    return jsonify({"status": "received"}), 200
