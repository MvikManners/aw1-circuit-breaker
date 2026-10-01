import re

path = '/home/LavetoLab/lvt_backend/main.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update SocietyTenant SQLAlchemy model
model_target = "    society_code = db.Column(db.String(32), unique=True, nullable=False)"
model_injection = """    society_code = db.Column(db.String(32), unique=True, nullable=False)
    ceda_reg_number = db.Column(db.String(64), nullable=True)
    cee_cert_number = db.Column(db.String(64), nullable=True)
    citizen_equity_pct = db.Column(db.Float, default=100.0, nullable=False)"""

if "ceda_reg_number = db.Column" not in code and model_target in code:
    code = code.replace(model_target, model_injection, 1)
    print("✓ Model SocietyTenant updated with statutory columns.")

# 2. Add Statutory Validator Function
validator_func = '''
def validate_society_statutory_compliance(ceda_no: str, cee_cert: str, citizen_equity_pct: float) -> tuple[bool, str]:
    """
    Validates society onboarding against CEDA and CEE Act 2021 requirements:
    - Minimum 50.0% Citizen Shareholding/Equity.
    - Non-empty CEDA registration and CEE certificate numbers.
    """
    if citizen_equity_pct < 50.0:
        return False, f"Citizen equity ({citizen_equity_pct:.1f}%) fails statutory threshold of >= 50.0% (CEE Act 2021)."
    if not ceda_no or not re.match(r"^CEDA-[A-Z0-9-]{3,20}$", ceda_no.strip().upper()):
        return False, "Invalid CEDA Registration ID format. Must match 'CEDA-XXXXX'."
    if not cee_cert or len(cee_cert.strip()) < 4:
        return False, "Valid CEE Act Certificate reference required."
    return True, "COMPLIANT"
'''

if "def validate_society_statutory_compliance" not in code:
    # Insert validator above society routes
    code = validator_func + "\n" + code
    print("✓ Added validate_society_statutory_compliance helper.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ PATCH_APPLIED_SUCCESSFULLY")
