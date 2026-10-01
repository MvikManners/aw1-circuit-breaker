path = '/home/LavetoLab/lvt_backend/main.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

target_params = '''    society_title = request.form.get("society_title", "").strip() or f"{village_name} Society"
    admin_passphrase = request.form.get("admin_passphrase", "").strip()'''

replacement_params = '''    society_title = request.form.get("society_title", "").strip() or f"{village_name} Society"
    admin_passphrase = request.form.get("admin_passphrase", "").strip()
    ceda_reg_number = request.form.get("ceda_reg_number", "").strip().upper()
    cee_cert_number = request.form.get("cee_cert_number", "").strip().upper()
    try:
        citizen_equity_pct = float(request.form.get("citizen_equity_pct", 100.0))
    except (ValueError, TypeError):
        citizen_equity_pct = 0.0'''

if target_params in code and 'ceda_reg_number = request.form.get' not in code:
    code = code.replace(target_params, replacement_params, 1)

target_create = '''    existing = SocietyTenant.query.filter_by(society_code=society_code).first()
    if existing:
        flash(f"🚨 Society Code '{society_code}' already exists.", "danger")
        return redirect(url_for("super_admin_console"))

    try:
        pass_hash = generate_password_hash(admin_passphrase) if admin_passphrase else ADMIN_PASSPHRASE_HASH
        new_tenant = SocietyTenant(
            village_name=village_name,
            society_code=society_code,
            society_title=society_title,
            admin_passphrase_hash=pass_hash,
            is_active=True
        )'''

replacement_create = '''    existing = SocietyTenant.query.filter_by(society_code=society_code).first()
    if existing:
        flash(f"🚨 Society Code '{society_code}' already exists.", "danger")
        return redirect(url_for("super_admin_console"))

    # AW-1 CEDA & CEE ACT 2021 ONBOARDING GATE
    is_valid, reason = validate_society_statutory_compliance(ceda_reg_number, cee_cert_number, citizen_equity_pct)
    if not is_valid:
        flash(f"🚨 Statutory Onboarding Blocked: {reason}", "danger")
        return redirect(url_for("super_admin_console"))

    try:
        pass_hash = generate_password_hash(admin_passphrase) if admin_passphrase else ADMIN_PASSPHRASE_HASH
        new_tenant = SocietyTenant(
            village_name=village_name,
            society_code=society_code,
            society_title=society_title,
            admin_passphrase_hash=pass_hash,
            is_active=True,
            ceda_reg_number=ceda_reg_number,
            cee_cert_number=cee_cert_number,
            citizen_equity_pct=citizen_equity_pct
        )'''

if target_create in code and 'AW-1 CEDA & CEE ACT 2021 ONBOARDING GATE' not in code:
    code = code.replace(target_create, replacement_create, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ PROVISION_VILLAGE_GATE_PATCHED")
