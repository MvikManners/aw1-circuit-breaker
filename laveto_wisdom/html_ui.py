# Generated HTML UI and Deliberation templates for Laveto Wisdom

HTML_DELIBERATION_SNIPPET = """
<div id="delib-feed-container" class="container" style="margin-top: 25px; margin-bottom: 40px;">
    <div style="background: #070B14; border: 1px solid #1E293B; border-radius: 8px; padding: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px;">
            <div>
                <h3 style="margin: 0; color: #FBBF24; font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
                    <span>⚖️</span> Institutional Deliberation Console
                </h3>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">Direct Conversational Statutory Assurance</div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <button type="button" onclick="branchAuditV2()" style="background: #059669; color: #FFF; border: none; padding: 6px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;">
                    🌱 Branch to v2 Audit
                </button>
                <button type="button" onclick="exportDelibTranscript()" style="background: #1E293B; color: #FBBF24; border: 1px solid #D97706; padding: 5px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;">
                    📥 Export Transcript
                </button>
                <span style="font-size: 0.72rem; background: #0E1726; color: #94A3B8; border: 1px solid #1E293B; padding: 4px 8px; border-radius: 4px;">
                    Pass 1–5 Context Active
                </span>
            </div>
        </div>

        <div id="delib-chat-stream" style="min-height: 180px; max-height: 380px; overflow-y: auto; background: #04070F; border: 1px solid #1E293B; border-radius: 6px; padding: 14px; display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px;">
            <div style="color: #64748B; font-size: 0.85rem;">
                Dossier is anchored. Challenge the verdict, propose mitigation clauses, or explore the suggested prompts below.
            </div>
        </div>

        <div style="display: flex; gap: 10px;">
            <input type="text" id="delib-prompt-input" placeholder="Type a mitigation proposal or statutory query..."
                   style="flex: 1; background: #0D131F; border: 1px solid #334155; color: #F1F5F9; padding: 12px 14px; border-radius: 6px; font-size: 0.92rem; outline: none;">
            <button type="button" id="delib-exec-btn" onclick="executeDelibChat()"
                    style="background: #D97706; color: #000; font-weight: 700; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 0.95rem;">
                Deliberate
            </button>
        </div>
    </div>
</div>

<style>
.delib-tag-pill {
    background: #111827; border: 1px solid #374151; color: #9CA3AF; padding: 6px 12px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; text-align: left;
}
.delib-tag-pill:hover { border-color: #FBBF24; color: #FBBF24; background: #1F2937; }
</style>

<script>
(function() {
    var delibHistory = [];
    var currentDossier = {{ (audit if audit is defined and audit else (result if result is defined and result else {})) | tojson | safe }};

    window.sendDelibProbe = function(txt) {
        var inp = document.getElementById('delib-prompt-input');
        if (inp) {
            inp.value = txt;
            window.executeDelibChat();
        }
    };

    window.branchAuditV2 = function() {
        var inp = document.getElementById('delib-prompt-input');
        var val = (inp && inp.value.trim()) ? inp.value.trim() : prompt("Enter specific statutory mitigations to branch this dossier to v2:");
        if (val) {
            window.location.href = "/wisdom/generate?intent=" + encodeURIComponent("Branching child audit v2 with mitigations: " + val);
        }
    };

    window.exportDelibTranscript = function() {
        var stream = document.getElementById('delib-chat-stream');
        if (!stream) return;
        var text = stream.innerText;
        var blob = new Blob([text], { type: 'text/plain' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'Laveto_Wisdom_Deliberation_Transcript.txt';
        a.click();
    };

    window.executeDelibChat = function() {
        var inp = document.getElementById('delib-prompt-input');
        var btn = document.getElementById('delib-exec-btn');
        var stream = document.getElementById('delib-chat-stream');
        if (!inp || !stream) return;

        var msg = inp.value.trim();
        if (!msg) return;

        var uBubble = document.createElement('div');
        uBubble.style.cssText = "align-self: flex-end; background: #1E293B; color: #F8FAFC; padding: 10px 14px; border-radius: 6px; max-width: 82%; font-size: 0.9rem; border: 1px solid #475569;";
        uBubble.textContent = msg;
        stream.appendChild(uBubble);

        var wait = document.createElement('div');
        wait.id = 'delib-running-note';
        wait.style.cssText = "align-self: flex-start; color: #FBBF24; font-size: 0.8rem; font-style: italic; padding: 4px 8px;";
        wait.textContent = "Conscience deliberating against statutory law...";
        stream.appendChild(wait);

        inp.value = '';
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Evaluating...';
        }
        stream.scrollTop = stream.scrollHeight;

        fetch('/wisdom/api/v1/deliberate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                audit_dossier: currentDossier,
                history: delibHistory,
                message: msg
            })
        })
        .then(function(res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .then(function(data) {
            var w = document.getElementById('delib-running-note');
            if (w) w.remove();

            var reply = data.reply || data.response || "No statutory response returned.";
            var botBubble = document.createElement('div');
            botBubble.style.cssText = "align-self: flex-start; background: #0D1526; border: 1px solid #D97706; color: #F1F5F9; padding: 12px 16px; border-radius: 6px; max-width: 85%; font-size: 0.9rem; line-height: 1.55; white-space: pre-wrap;";
            botBubble.innerHTML = '<strong style="color:#FBBF24; display:block; margin-bottom:6px; font-size:0.75rem; text-transform:uppercase;">⚖️ AW Statutory Verdict:</strong>' + reply;
            stream.appendChild(botBubble);

            delibHistory.push({ role: 'user', text: msg });
            delibHistory.push({ role: 'model', text: reply });
            stream.scrollTop = stream.scrollHeight;
        })
        .catch(function(err) {
            var w = document.getElementById('delib-running-note');
            if (w) w.remove();

            var errBubble = document.createElement('div');
            errBubble.style.cssText = "background: rgba(220, 38, 38, 0.2); border: 1px solid #EF4444; color: #FCA5A5; padding: 8px 12px; border-radius: 6px; font-size: 0.85rem;";
            errBubble.textContent = "Deliberation error: " + err.message;
            stream.appendChild(errBubble);
            stream.scrollTop = stream.scrollHeight;
        })
        .finally(function() {
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Deliberate';
            }
        });
    };

    var inputEl = document.getElementById('delib-prompt-input');
    if (inputEl) {
        inputEl.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                window.executeDelibChat();
            }
        });
    }
})();
</script>
"""


HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Laveto Wisdom AW — Decision Assurance Console</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/svg+xml" href="/wisdom/static/favicon.svg">
    <style>
        :root {
            --bg: #0B0F19; --card: #151C2C; --gold: #D97706; --gold-light: #FBBF24;
            --text: #F3F4F6; --border: #232E42; --halt: #DC2626; --cal: #EAB308; --proc: #16A34A;
        }
        body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 1.5rem 1rem; }
        .container { max-width: 1060px; margin: 0 auto; }
        .top-control-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 1.25rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .clearance-group { display: inline-flex; align-items: center; gap: 8px; font-size: 0.8rem; }
        .clearance-select { background: #0B1120; border: 1px solid #D97706; color: #FBBF24; padding: 6px 12px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; outline: none; cursor: pointer; }
        .top-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .top-btn { background: #111827; color: #F1F5F9; border: 1px solid #374151; padding: 6px 14px; font-size: 0.8rem; border-radius: 4px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
        .top-btn:hover { border-color: var(--gold); color: var(--gold-light); }
        .brand-header { text-align: center; margin-bottom: 1.5rem; }
        .brand-logo { max-width: 440px; width: 100%; height: auto; display: block; margin: 0 auto 0.5rem auto; }
        .nav-links { display: flex; justify-content: center; gap: 8px; margin-bottom: 2rem; flex-wrap: wrap; }
        .nav-links a { color: #9CA3AF; text-decoration: none; font-size: 0.82rem; font-weight: 600; padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border); background: #0E1424; }
        .nav-links a:hover, .nav-links a.active { color: var(--gold-light); border-color: var(--gold); }
        .nav-links a.incubator-pill { background: #D97706; color: #FFFFFF !important; border-color: #D97706; font-weight: 700; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
        textarea { width: 100%; background: #0A0D14; border: 1px solid var(--border); color: #FFF; padding: 0.85rem; border-radius: 6px; font-size: 16px; box-sizing: border-box; min-height: 120px; resize: vertical; }
        button.btn-primary { background: var(--gold); color: #000; font-weight: 700; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; font-size: 0.95rem; cursor: pointer; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: 800; font-size: 0.85rem; }
        .badge-HALT { background: var(--halt); color: #fff; }
        .badge-CALIBRATE, .badge-RECALIBRATE { background: var(--cal); color: #000; }
        .badge-PROCEED { background: var(--proc); color: #fff; }
        .upload-panel { margin-top: 1rem; padding: 14px; background: #080C16; border: 1px dashed #D97706; border-radius: 6px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
        .upload-label { background: #1E293B; color: #FBBF24; border: 1px solid #D97706; padding: 8px 14px; border-radius: 5px; cursor: pointer; font-size: 0.85rem; font-weight: 700; display: inline-flex; align-items: center; gap: 8px; }
        .drawer { display: none; position: fixed; right: 0; top: 0; width: 380px; max-width: 90vw; height: 100%; background: #0D131F; border-left: 1px solid var(--border); padding: 1.5rem; box-sizing: border-box; overflow-y: auto; z-index: 1000; }
        @keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }
    </style>
</head>
<body>
<div class="container">
    <div class="top-control-bar">
        <div class="clearance-group">
            <span>Institutional Clearance:</span>
            <select class="clearance-select" onchange="window.location.href='/wisdom/set-role/'+this.value">
                <option value="INVESTOR" {% if user_role == 'INVESTOR' %}selected{% endif %}>Tier 1: External Investor</option>
                <option value="ANALYST" {% if user_role == 'ANALYST' %}selected{% endif %}>Tier 2: CEDA / BITC Analyst</option>
                <option value="REGULATOR" {% if user_role == 'REGULATOR' %}selected{% endif %}>Tier 3: Sovereign Regulator</option>
            </select>
        </div>
        <div class="top-actions">
            <a href="/wisdom/diff" class="top-btn" title="Compare Lineage Revisions"><span>⚖️</span> Revision Diff</a>
                        <button type="button" onclick="toggleWhatIfModal()" class="top-btn" title="Statutory What-If CEE & NPL Simulator" style="background: #0B1120; border: 1px solid #0284C7; color: #38BDF8; cursor: pointer;"><span>🎛️</span> What-If Simulator</button>
<a href="/wisdom/ledger/verify" class="top-btn" title="Verify Cryptographic Continuity"><span>🛡️</span> Verify Ledger Chain</a>
            <button type="button" class="top-btn" onclick="toggleDrawer()"><span>📜</span> Past Audits</button>
        </div>
    </div>

    <div class="brand-header">
        <a href="/wisdom/"><img src="/wisdom/static/logo.svg" alt="Laveto Wisdom AW" class="brand-logo" /></a>
    </div>

    <!-- 12 Sovereign Navigation Links -->
        <!-- STRUCTURED 3-TIER OPERATIONAL NAVIGATION DECK -->
    <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 2rem;">
        <!-- Tier 1: Core Governance -->
        <div class="nav-links" style="margin-bottom: 0; gap: 8px;">
            <span style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: bold; align-self: center; margin-right: 4px;">Core:</span>
            <a href="/wisdom/" class="active">Assurance Console</a>
            <a href="/wisdom/generate" class="incubator-pill">💡 Idea Incubator</a>
            <a href="/wisdom/sandbox">Policy Simulator</a>
            <a href="/wisdom/analytics">Executive Analytics</a>
        </div>
        <!-- Tier 2: Developer & Enterprise Suite -->
        <div class="nav-links" style="margin-bottom: 0; gap: 8px;">
            <span style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: bold; align-self: center; margin-right: 4px;">Enterprise:</span>
            <a href="/wisdom/api-console" style="color: #38BDF8; border-color: #0369A1;">⚡ API Console</a>
            <a href="/wisdom/docs">B2B API Docs</a>
            <a href="/wisdom/onboard">Partner Onboarding</a>
            <a href="/wisdom/deck">Institutional Deck</a>
        </div>
        <!-- Tier 3: Ecosystem & Citizen Network -->
        <div class="nav-links" style="margin-bottom: 0; gap: 8px;">
            <span style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: bold; align-self: center; margin-right: 4px;">Ecosystem:</span>
            <a href="/join?ref=BW-GENESIS-APEX" style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #FFF !important; border: 1px solid #10B981; font-weight: 700;" target="_blank">👑 Join Genesis Squad (+10 AWT)</a>
            <a href="/wisdom/citizen">🏠 Citizen Portal</a>
        </div>
    </div>

    <div id="async-progress-card" class="card" style="display: none; border-left: 4px solid var(--gold); margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="animation: pulse 1.5s infinite; display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #FBBF24;"></span>
                <h3 style="margin: 0; color: #FBBF24; font-size: 1.1rem;">⚖️ Sovereign 5-Pass Conscience Active</h3>
            </div>
            <span id="async-progress-pct" style="font-family: monospace; font-weight: bold; color: #FBBF24; font-size: 1.1rem;">15%</span>
        </div>
        <div style="width: 100%; background: #070B14; border: 1px solid #1E293B; height: 12px; border-radius: 6px; overflow: hidden; margin-bottom: 12px;">
            <div id="async-progress-bar" style="width: 15%; height: 100%; background: linear-gradient(90deg, #D97706, #FBBF24); transition: width 0.6s ease;"></div>
        </div>
        <div id="async-stage-text" style="font-size: 0.88rem; color: #94A3B8; font-style: italic;">
            Pass 1: Teleological Intent Matrix & Statutory Ground-Truth Active...
        </div>
    </div>

    <div class="card">
        <h3 style="margin-top: 0; margin-bottom: 1rem;">Submit Policy / Capital Dilemma</h3>
        <form method="POST" action="/wisdom/" enctype="multipart/form-data">
            <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <label style="cursor: pointer; background: #1E293B; border: 1px solid #D97706; color: #FBBF24; padding: 7px 14px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 6px;">
                    📄 Upload Dossier to Generate Prompt
                    <input type="file" id="dossier-upload-btn" accept=".txt,.json,.md,.csv,.pdf" style="display: none;" onchange="generatePromptFromDoc(this)">
                </label>
                <span id="upload-status-text" style="font-size: 0.82rem; color: #94A3B8;">Attach document for AW to formulate statutory audit dilemma</span>
            </div>

            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #CBD5E1; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    <span>⚖️</span> Select Statutory Audit Lenses (Scope Filter):
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.8rem; color: #94A3B8;">
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                        <input type="checkbox" name="lens_mining" value="1"> Mining &amp; Beneficiation
                    </label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer; color: #60A5FA;">
                        <input type="checkbox" name="lens_seza" value="1" checked> SEZA / SPEDU Hubs
                    </label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                        <input type="checkbox" name="lens_water" value="1"> Water &amp; Agriculture
                    </label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                        <input type="checkbox" name="lens_energy" value="1"> Energy &amp; IRP Solar
                    </label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                        <input type="checkbox" name="lens_dpa" value="1"> Data Sovereignty (DPA)
                    </label>
                </div>
            </div>

            <textarea id="proposal-input" name="proposal" placeholder="Paste policy decree, CEDA application, or capital expenditure plan to stress-test against Botswana statutory ground-truth..." required>{{ proposal }}</textarea>

            <div class="upload-panel">
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <button type="button" class="upload-label" onclick="loadSampleDossier()" style="background:#111827; border-color:#374151; color:#CBD5E1;">
                        📋 Load Sample Dossier
                    </button>
                    <label for="dossier-file" class="upload-label">
                        <span>📁 Choose Dossier File</span>
                    </label>
                    <input type="file" id="dossier-file" name="file" accept=".txt,.json,.md,.csv,.pdf" style="display: none;" onchange="handleFileSelected(this)">
                    <span id="file-chosen-name" style="color: #94A3B8; font-size: 0.85rem;">No dossier attached</span>
                </div>
                <button type="submit" class="btn-primary" style="margin: 0;">Execute Wisdom Audit</button>
            </div>
        </form>
    </div>

    {% if result %}
    <div id="audit-result-container" class="card" style="border: 1px solid #1E293B; background: #0D1424; padding: 2rem; border-radius: 10px;">
        {% if result.parent_audit_id %}
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 0.82rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #6EE7B7;">🌿 <b>Lineage Branch:</b> Version {{ result.version }} (Child of <a href="/wisdom/audit/{{ result.parent_audit_id }}" style="color: #FBBF24; text-decoration: underline;">{{ result.parent_audit_id }}</a>)</span>
            <span style="font-family: monospace; font-size: 0.72rem; color: #94A3B8;">Parent Linked</span>
        </div>
        {% endif %}

        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; padding-bottom: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; color: #FFF; font-size: 1.4rem;">Dossier: <span id="audit-id-val" style="color: #38BDF8;">{{ result.audit_id }}</span></h2>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px; font-family: monospace;">
                    🔒 SHA-256 Seal: {{ result.sha256_seal[:24] if result.sha256_seal else 'SEALED-GENESIS' }}...
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span id="audit-posture-val" class="badge badge-{{ result.posture }}" style="font-size: 0.9rem; padding: 6px 14px;">{{ result.posture }}</span>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: bold; display: block;">Wisdom Quotient</span>
                    <strong id="audit-w-val" style="color: #FBBF24; font-size: 1.25rem;">ω = {{ result.wisdom_quotient }}</strong>
                </div>
            </div>
        </div>

        <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: #94A3B8;">
            <strong>Formula Breakdown:</strong> <code id="audit-formula-val" style="color: #38BDF8;">{{ result.formula }}</code>
        </p>

        <div style="background: rgba(220, 38, 38, 0.12); border-left: 4px solid #EF4444; border-radius: 6px; padding: 14px 18px; margin-bottom: 1.5rem;">
            <h4 style="color: #F87171; margin: 0 0 6px 0; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.5px;">⚖️ The Uncomfortable Truth:</h4>
            <p id="audit-truth-val" style="color: #FEE2E2; font-style: italic; margin: 0; font-size: 0.95rem; line-height: 1.5;">
                "{{ result.passes.pass_5_verdict.the_uncomfortable_truth if (result and result.passes and result.passes.pass_5_verdict) else 'Audit completed against statutory ground-truth.' }}"
            </p>
        </div>

        <!-- 3 Bankable Alternatives -->
        <div style="margin: 2rem 0; border: 1px solid #D97706; background: linear-gradient(180deg, rgba(217, 119, 6, 0.08) 0%, rgba(11, 19, 43, 0.9) 100%); border-radius: 10px; padding: 20px;">
            <h3 style="margin: 0 0 12px 0; color: #FBBF24; font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
                <span>💡</span> Autonomous Idea Incubator: 3 Bankable Alternate Proposals
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 14px;">
                {% for prop in result.creative_proposals %}
                <div style="background: #080D1A; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <strong style="color: #F8FAFC; font-size: 0.9rem; display: block; margin-bottom: 4px;">{{ prop.title }}</strong>
                        <span style="background: #0F172A; color: #38BDF8; border: 1px solid #0284C7; font-size: 0.68rem; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 8px;">{{ prop.sector }}</span>
                        <p style="color: #CBD5E1; font-size: 0.8rem; line-height: 1.45; margin: 0 0 10px 0;">{{ prop.strategy }}</p>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button type="button" onclick="loadProposalIntoConsole({{ prop.actionable_text | tojson }})" style="flex: 1; background: #D97706; color: #000; font-weight: bold; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.78rem; cursor: pointer;">⚡ Test Proposal</button>
                        <a href="/wisdom/generate?intent={{ prop.actionable_text | urlencode }}&sector={{ prop.sector | urlencode }}" style="background: #1E293B; border: 1px solid #334155; color: #FBBF24; padding: 8px 10px; border-radius: 4px; font-size: 0.78rem; text-decoration: none; font-weight: bold;">🛠️ Incubate</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Download Buttons -->
        <div style="margin-top: 1.5rem; display: flex; gap: 10px; flex-wrap: wrap;">
            {% if result.statutory_remedy_term_sheet or result.posture in ['CALIBRATE', 'HALT'] %}
            <a href="/wisdom/audit/{{ result.audit_id }}/term-sheet-pdf" style="background: #D97706; color: #000; font-weight: 700; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 0.85rem;">📄 Download Term Sheet PDF</a>
            {% endif %}
            <a href="/wisdom/audit/{{ result.audit_id }}/audio-brief" style="background: #1E293B; border: 1px solid #334155; color: #38BDF8; font-weight: 600; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 0.85rem;">🎧 Audio Briefing</a>
        </div>
    </div>
    {% endif %}

    """ + HTML_DELIBERATION_SNIPPET + """

    <div id="drawer" class="drawer">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: var(--gold);">Audit History</h3>
            <button type="button" onclick="toggleDrawer()" style="background: transparent; border: none; color: #FFF; font-size: 1.2rem; cursor: pointer;">✕</button>
        </div>
        <div id="history-content">Loading past audits...</div>
    </div>
</div>

<script src="/wisdom/static/wisdom_console.js?v=20260918_clean"></script>
<script src="/wisdom/static/support_widget.js?v=20260918_clean"></script>

<!-- INTERACTIVE STATUTORY WHAT-IF SIMULATOR MODAL -->
<div id="whatif-modal" style="display:none; position:fixed; z-index:99999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(6px); align-items:center; justify-content:center;">
    <div style="background:#0F172A; border:1px solid #1E293B; border-radius:12px; max-width:850px; width:92%; max-height:90vh; overflow-y:auto; padding:24px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); color:#F8FAFC;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:12px; margin-bottom:18px;">
            <div>
                <h3 style="color:#38BDF8; margin:0; font-size:1.2rem;">🛡️ Statutory "What-If" Simulator & Dossier Engine</h3>
                <span style="font-size:0.75rem; color:#94A3B8;">Economic Inclusion Act 2021 & AW-1 Out-of-Band Risk Auditing</span>
            </div>
            <button type="button" onclick="toggleWhatIfModal()" style="background:transparent; border:none; color:#94A3B8; font-size:1.5rem; cursor:pointer;">&times;</button>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
            <div style="background:#090D16; padding:16px; border-radius:8px; border:1px solid #1E293B;">
                <h4 style="color:#CBD5E1; margin-top:0; font-size:0.85rem; border-bottom:1px solid #1E293B; padding-bottom:8px;">🎛️ Scenario Inputs</h4>
                <div style="margin-bottom:12px;">
                    <label style="font-size:0.75rem; color:#94A3B8; display:flex; justify-content:space-between;">
                        <span>Loan / Tender Valuation</span>
                        <span id="lbl-loan" style="color:#38BDF8; font-family:monospace;">BWP 25,000,000</span>
                    </label>
                    <input type="range" id="wi-loan" min="1000000" max="100000000" step="1000000" value="25000000" style="width:100%; accent-color:#0284C7;" oninput="updateWhatIf()">
                </div>
                <div style="margin-bottom:12px;">
                    <label style="font-size:0.75rem; color:#94A3B8; display:flex; justify-content:space-between;">
                        <span>Local Labor Quota (%)</span>
                        <span id="lbl-labor" style="color:#38BDF8; font-family:monospace;">55%</span>
                    </label>
                    <input type="range" id="wi-labor" min="10" max="100" value="55" style="width:100%; accent-color:#0284C7;" oninput="updateWhatIf()">
                </div>
                <div style="margin-bottom:12px;">
                    <label style="font-size:0.75rem; color:#94A3B8; display:flex; justify-content:space-between;">
                        <span>Local Subcontracting Quota (%)</span>
                        <span id="lbl-subcontract" style="color:#38BDF8; font-family:monospace;">50%</span>
                    </label>
                    <input type="range" id="wi-subcontract" min="10" max="100" value="50" style="width:100%; accent-color:#0284C7;" oninput="updateWhatIf()">
                </div>
                <div>
                    <label style="font-size:0.75rem; color:#94A3B8; display:flex; justify-content:space-between;">
                        <span>Environmental Compliance (0 - 10)</span>
                        <span id="lbl-env" style="color:#38BDF8; font-family:monospace;">8.5</span>
                    </label>
                    <input type="range" id="wi-env" min="1" max="10" step="0.5" value="8.5" style="width:100%; accent-color:#0284C7;" oninput="updateWhatIf()">
                </div>
            </div>

            <div style="display:flex; flex-direction:column; justify-content:space-between; background:#090D16; padding:16px; border-radius:8px; border:1px solid #1E293B;">
                <div>
                    <h4 style="color:#CBD5E1; margin-top:0; font-size:0.85rem; border-bottom:1px solid #1E293B; padding-bottom:8px;">📊 Simulated Statutory Metrics</h4>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;">
                        <div style="background:#0F172A; padding:10px; border-radius:6px; border:1px solid #1E293B;">
                            <span style="font-size:0.7rem; color:#94A3B8; display:block;">Effective CEE Quota</span>
                            <span id="res-cee" style="font-size:1.2rem; font-weight:bold; color:#10B981;">52.0%</span>
                            <span style="font-size:0.65rem; color:#64748B; display:block;">Min Statute: 50.0%</span>
                        </div>
                        <div style="background:#0F172A; padding:10px; border-radius:6px; border:1px solid #1E293B;">
                            <span style="font-size:0.7rem; color:#94A3B8; display:block;">Wisdom Quotient (W)</span>
                            <span id="res-w" style="font-size:1.2rem; font-weight:bold; color:#10B981;">2.45</span>
                            <span style="font-size:0.65rem; color:#64748B; display:block;">Threshold: &ge; 1.50</span>
                        </div>
                    </div>
                    <div style="background:#0F172A; padding:10px; border-radius:6px; border:1px solid #1E293B; margin-top:10px;">
                        <span style="font-size:0.7rem; color:#94A3B8; display:block;">Predicted Default (NPL) Risk</span>
                        <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                            <span id="res-npl" style="font-size:1.1rem; font-weight:bold; color:#38BDF8;">4.8%</span>
                            <span style="font-size:0.75rem; color:#10B981; font-weight:bold;">(-64% vs Base)</span>
                        </div>
                    </div>
                </div>

                <div style="margin-top:14px;">
                    <button type="button" onclick="exportDossierPdfFromWhatIf()" style="width:100%; background:#0284C7; color:#FFF; font-weight:bold; font-size:0.8rem; padding:10px; border:none; border-radius:6px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px;">
                        <span>📄</span> Export 1-Click SHA-256 Decision Assurance Dossier (PDF)
                    </button>
                    <span id="pdf-export-msg" style="display:none; font-size:0.7rem; color:#10B981; text-align:center; margin-top:6px; font-family:monospace;"></span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function toggleWhatIfModal() {
    var m = document.getElementById('whatif-modal');
    if (!m) return;
    m.style.display = (m.style.display === 'none' || m.style.display === '') ? 'flex' : 'none';
    if (m.style.display === 'flex') updateWhatIf();
}

function updateWhatIf() {
    var loan = parseFloat(document.getElementById('wi-loan').value);
    var labor = parseFloat(document.getElementById('wi-labor').value);
    var subcontract = parseFloat(document.getElementById('wi-subcontract').value);
    var env = parseFloat(document.getElementById('wi-env').value);

    document.getElementById('lbl-loan').textContent = 'BWP ' + Number(loan).toLocaleString();
    document.getElementById('lbl-labor').textContent = labor + '%';
    document.getElementById('lbl-subcontract').textContent = subcontract + '%';
    document.getElementById('lbl-env').textContent = env.toFixed(1);

    var cee = (0.4 * labor + 0.6 * subcontract);
    var axiological = Math.min(1.0, (cee / 100.0) * (env / 10.0));
    var irreversibility = Math.max(0.2, (loan / 50000000.0));
    var w = Math.max(0.1, (4.0 * axiological) / (irreversibility + 0.5));
    var npl = Math.max(2.1, (15.0 * (1.0 - (w / 4.0))));

    var elCee = document.getElementById('res-cee');
    elCee.textContent = cee.toFixed(1) + '%';
    elCee.style.color = (cee >= 50.0) ? '#10B981' : '#F43F5E';

    var elW = document.getElementById('res-w');
    elW.textContent = w.toFixed(2);
    elW.style.color = (w >= 1.50) ? '#10B981' : '#FBBF24';

    document.getElementById('res-npl').textContent = npl.toFixed(1) + '%';
}

function exportDossierPdfFromWhatIf() {
    var loan = document.getElementById('wi-loan').value;
    var w = document.getElementById('res-w').textContent;
    var cee = document.getElementById('res-cee').textContent.replace('%','');
    var msg = document.getElementById('pdf-export-msg');
    
    if (msg) {
        msg.style.display = 'block';
        msg.textContent = '⏳ Compiling SHA-256 Dossier PDF...';
    }
    
    var url = '/wisdom/api/v1/whatif/export-dossier-pdf?loan_amount_bwp=' + loan + '&wisdom_quotient_W=' + w + '&cee_quota_percentage=' + cee;
    window.location.href = url;
    
    setTimeout(function() {
        if (msg) msg.textContent = '✓ Decision_Assurance_Dossier.pdf exported with SHA-256 seal';
    }, 1500);
}
</script>

</body>
</html>
"""

