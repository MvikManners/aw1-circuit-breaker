import re

path = '/home/LavetoLab/lvt_backend/main.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add alert dispatcher import if not present
import_snippet = """import sys
if '/home/LavetoLab/aw1-breaker/scripts' not in sys.path:
    sys.path.insert(0, '/home/LavetoLab/aw1-breaker/scripts')
from alert_dispatcher import dispatch_statutory_breach_alert
"""

if "from alert_dispatcher import dispatch_statutory_breach_alert" not in code:
    code = import_snippet + "\n" + code
    print("✓ Added alert_dispatcher import to main.py")

# 2. Hook alert dispatch into provision_village_tenant statutory rejection
old_gate = '''    # AW-1 CEDA & CEE ACT 2021 ONBOARDING GATE
    is_valid, reason = validate_society_statutory_compliance(ceda_reg_number, cee_cert_number, citizen_equity_pct)
    if not is_valid:
        flash(f"🚨 Statutory Onboarding Blocked: {reason}", "danger")
        return redirect(url_for("super_admin_console"))'''

new_gate = '''    # AW-1 CEDA & CEE ACT 2021 ONBOARDING GATE
    is_valid, reason = validate_society_statutory_compliance(ceda_reg_number, cee_cert_number, citizen_equity_pct)
    if not is_valid:
        dispatch_statutory_breach_alert(
            event_type="STATUTORY_ONBOARDING_BREACH",
            society_code=society_code,
            reason=reason,
            details={"ceda_reg_number": ceda_reg_number, "cee_cert_number": cee_cert_number, "citizen_equity_pct": citizen_equity_pct}
        )
        flash(f"🚨 Statutory Onboarding Blocked: {reason}", "danger")
        return redirect(url_for("super_admin_console"))'''

if old_gate in code:
    code = code.replace(old_gate, new_gate, 1)
    print("✓ Alert dispatch hooked into provision_village_tenant statutory gate")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ ALERT_DISPATCH_HOOKED_SUCCESSFULLY")
