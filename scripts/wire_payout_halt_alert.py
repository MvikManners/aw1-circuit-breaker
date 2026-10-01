path = '/home/LavetoLab/lvt_backend/main.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

target = '''    if not allowed:
        return jsonify({
            "status": "HALTED",
            "statutory_violation": True,
            "reason": reason
        }), 422'''

replacement = '''    if not allowed:
        try:
            from alert_dispatcher import dispatch_statutory_breach_alert
            dispatch_statutory_breach_alert(
                event_type="UNAUTHORIZED_PAYOUT_HALT",
                society_code=session.get("active_coop_code", "UNKNOWN"),
                reason=reason,
                details={"requested_amount": amount, "beneficiary_phone": phone_number}
            )
        except Exception as e:
            pass
        return jsonify({
            "status": "HALTED",
            "statutory_violation": True,
            "reason": reason
        }), 422'''

if target in code and 'UNAUTHORIZED_PAYOUT_HALT' not in code:
    code = code.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ Payout halt alert hooked successfully.")
else:
    print("• Payout halt target already updated or not matched.")
