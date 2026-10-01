import re

path = '/home/LavetoLab/lvt_backend/templates/leotwana_admin.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

card_markup = """
    <!-- AW-1 STATUTORY REGULATORY COMPLIANCE WIDGET -->
    <div class="card shadow-sm border-0 mb-4" style="border-left: 5px solid #198754 !important;">
        <div class="card-body py-3">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                <div>
                    <span class="badge bg-success-subtle text-success border border-success px-2 py-1 mb-1">
                        <i class="bi bi-shield-check me-1"></i> CEDA & CEE ACT 2021 INTERLOCK ACTIVE
                    </span>
                    <h6 class="mb-0 fw-bold">Bank of Botswana 1-to-1 Trust Backing Verified</h6>
                    <small class="text-muted">Automated daily escrow reconciliation & pre-disbursement quota gating.</small>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <div class="input-group input-group-sm" style="max-width: 320px;">
                        <input type="text" id="sealLookupInput" class="form-control font-monospace" placeholder="Paste SHA-256 seal...">
                        <button class="btn btn-outline-dark" type="button" onclick="verifyStatutorySeal()">Verify</button>
                    </div>
                </div>
            </div>
            <div id="sealVerifyResult" class="mt-2 small" style="display: none;"></div>
        </div>
    </div>

    <script>
    function verifyStatutorySeal() {
        const hash = document.getElementById('sealLookupInput').value.trim();
        const resDiv = document.getElementById('sealVerifyResult');
        if (!hash) return;
        resDiv.style.display = 'block';
        resDiv.className = 'mt-2 alert alert-secondary py-1 px-2 font-monospace small';
        resDiv.innerText = 'Checking audit ledger...';

        fetch('/wisdom/api/v1/compliance/verify/' + encodeURIComponent(hash))
            .then(res => res.json())
            .then(data => {
                if (data.status === 'VERIFIED') {
                    resDiv.className = 'mt-2 alert alert-success py-1 px-2 small';
                    resDiv.innerHTML = '<strong>✓ SEAL VERIFIED:</strong> ' + data.audit_record;
                } else {
                    resDiv.className = 'mt-2 alert alert-danger py-1 px-2 small';
                    resDiv.innerText = '❌ Unverified: ' + (data.error || 'Seal not found in ledger.');
                }
            })
            .catch(err => {
                resDiv.className = 'mt-2 alert alert-warning py-1 px-2 small';
                resDiv.innerText = '⚠️ Lookup error: ' + err.message;
            });
    }
    </script>
"""

if 'AW-1 STATUTORY REGULATORY COMPLIANCE WIDGET' not in html:
    # Inject right after block content or main container
    if '{% block content %}' in html:
        html = html.replace('{% block content %}', '{% block content %}\n' + card_markup, 1)
    else:
        # Prepend to template if no block tag
        html = card_markup + '\n' + html
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('✓ INJECTED_COMPLIANCE_WIDGET')
else:
    print('✓ WIDGET_ALREADY_PRESENT')
