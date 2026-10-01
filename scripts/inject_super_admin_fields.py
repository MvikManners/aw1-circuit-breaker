path = '/home/LavetoLab/lvt_backend/templates/super_admin.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

statutory_inputs = """
                    <!-- Statutory CEDA & CEE Compliance Fields -->
                    <div class="row g-2 mb-3">
                        <div class="col-md-4">
                            <label class="form-label small fw-bold">CEDA Registration ID</label>
                            <input type="text" name="ceda_reg_number" class="form-control form-control-sm" placeholder="e.g. CEDA-2026-01" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small fw-bold">CEE Act Certificate</label>
                            <input type="text" name="cee_cert_number" class="form-control form-control-sm" placeholder="e.g. CEE-BW-9921" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small fw-bold">Citizen Equity (%)</label>
                            <input type="number" step="0.1" min="50.0" max="100.0" name="citizen_equity_pct" value="100.0" class="form-control form-control-sm" required>
                            <div class="form-text text-muted" style="font-size: 0.75rem;">Min 50.0% required by CEE Act 2021</div>
                        </div>
                    </div>
"""

# Target the submit button inside the provision village form
if 'name="ceda_reg_number"' not in html:
    targets = [
        '<button type="submit" class="btn btn-primary',
        '<button type="submit" class="btn btn-success',
        '<button type="submit"'
    ]
    for target in targets:
        if target in html:
            html = html.replace(target, statutory_inputs + '\n                    ' + target, 1)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print("✓ STATUTORY_FORM_FIELDS_INJECTED")
            break
    else:
        print("❌ Submit button target not matched")
else:
    print("• Form fields already present in super_admin.html")
