from flask import Blueprint, jsonify

spark_bp = Blueprint('spark_assistant', __name__)

@spark_bp.route('/spark/status', methods=['GET'])
def spark_status():
    return jsonify({"status": "ONLINE", "agent": "SPARK_ASSISTANT"}), 200
