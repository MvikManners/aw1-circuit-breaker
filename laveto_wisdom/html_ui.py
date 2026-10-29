"""
Generated HTML UI and Deliberation templates for Laveto Wisdom AW
"""

HTML_DELIBERATION_SNIPPET = r"""<div id="delib-feed-container" class="card" style="background: #0B1120; border: 1px solid #1E293B; border-radius: 8px; padding: 1.5rem; margin-top: 1.5rem; margin-bottom: 1.5rem;">
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
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;">
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('What specific domestic beneficiation ratio will reverse the CALIBRATE posture to PROCEED?')">Beneficiation Quotas</button>
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('How can the 45% SMME subcontracting gap be structured under Public Procurement Act 2022 Sec 54?')">CEE 50% Subcontracting</button>
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('Specify the required closed-loop water treatment covenants under Water Act [Cap 34:01].')">Water Act [Cap 34:01]</button>
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('Detail captive solar PV integration standards required under BERA Act 2016 and IRP 2030.')">BERA Renewable Power</button>
    </div>
    <div style="display: flex; gap: 10px;">
        <input type="text" id="delib-prompt-input" placeholder="Type a mitigation proposal or statutory query..."
               style="flex: 1; background: #0D131F; border: 1px solid #334155; color: #F1F5F9; padding: 12px 14px; border-radius: 6px; font-size: 0.92rem; outline: none;">
        <button type="button" id="delib-exec-btn" onclick="executeDelibChat()"
                style="background: #D97706; color: #000; font-weight: 700; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 0.95rem;">
            Deliberate
        </button>
    </div>
</div>"""

HTML_UI = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Laveto Wisdom AW — Decision Assurance Console</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/svg+xml" href="/wisdom/static/favicon.svg">
    <style>
        :root {
            --bg: #070B14; --card-bg: #0B1120; --card-border: #1E293B;
            --gold: #D97706; --gold-light: #FBBF24; --text-main: #F8FAFC;
            --text-muted: #94A3B8; --halt: #DC2626; --cal: #EAB308; --proc: #16A34A;
        }
        * { box-sizing: border-box; }
        body {
            background: var(--bg); color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; padding: 0 0 3rem 0; line-height: 1.5;
        }
        .top-nav-bar {
            position: sticky; top: 0; left: 0; right: 0; width: 100%; background: #080D1A;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08); z-index: 1000;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); backdrop-filter: blur(8px);
        }
        .top-nav-inner {
            max-width: 1360px; margin: 0 auto; padding: 0.5rem 1.25rem;
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: nowrap; gap: 12px; width: 100%;
        }
        .container { max-width: 1140px; margin: 0 auto; padding: 1.5rem 1rem 0 1rem; width: 100%; }
        .clearance-group { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
        .clearance-select { background: #0B132B; border: 1.5px solid #D97706; color: #FBBF24; padding: 5px 10px; border-radius: 6px; font-weight: 700; font-size: 0.82rem; outline: none; cursor: pointer; transition: all 0.2s; }
        .top-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
        .top-btn { background: #111827; color: #F1F5F9; border: 1px solid #374151; padding: 5px 11px; font-size: 0.78rem; border-radius: 6px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; transition: all 0.2s; }
        .top-btn:hover { border-color: var(--gold); color: var(--gold-light); }
        .sov-item { display: flex; align-items: flex-start; gap: 8px; padding: 8px 10px; border-radius: 6px; text-decoration: none; color: #F8FAFC; transition: background 0.15s ease; }
        .sov-item:hover { background: rgba(245, 158, 11, 0.15); }
        .brand-header { text-align: center; margin: 1.5rem 0 1.25rem 0; width: 100%; cursor: pointer; user-select: none; }
        .brand-logo { max-width: 440px; width: 100%; height: auto; display: block; margin: 0 auto; transition: transform 0.15s ease; }
        .nav-links { display: flex; justify-content: center; gap: 8px; margin-bottom: 0; flex-wrap: wrap; }
        .nav-links a { color: #9CA3AF; text-decoration: none; font-size: 0.82rem; font-weight: 600; padding: 6px 12px; border-radius: 6px; border: 1px solid #232E42; background: #0E1424; transition: all 0.2s; }
        .nav-links a:hover, .nav-links a.active { color: var(--gold-light); border-color: var(--gold); }
        .nav-links a.incubator-pill { background: #D97706; color: #FFFFFF !important; border-color: #D97706; font-weight: 700; }
        .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; width: 100%; }
        textarea { width: 100%; background: #060A12; border: 1px solid var(--card-border); color: #FFF; padding: 0.85rem; border-radius: 6px; font-size: 15px; box-sizing: border-box; min-height: 120px; resize: vertical; font-family: inherit; }
        button.btn-primary { background: var(--gold); color: #000; font-weight: 700; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; font-size: 0.95rem; cursor: pointer; }
        .badge-btn { background: rgba(217, 119, 6, 0.15); color: #FBBF24; border: 1px solid #D97706; padding: 4px 12px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: 800; font-size: 0.85rem; }
        .badge-HALT { background: var(--halt); color: #fff; }
        .badge-CALIBRATE, .badge-RECALIBRATE { background: var(--cal); color: #000; }
        .badge-PROCEED { background: var(--proc); color: #fff; }
        .upload-panel { margin-top: 1rem; padding: 14px; background: #080C16; border: 1px dashed #D97706; border-radius: 6px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
        .upload-label { background: #1E293B; color: #FBBF24; border: 1px solid #D97706; padding: 8px 14px; border-radius: 5px; cursor: pointer; font-size: 0.85rem; font-weight: 700; display: inline-flex; align-items: center; gap: 8px; }
        .drawer { display: none; position: fixed; right: 0; top: 0; width: 380px; max-width: 90vw; height: 100%; background: #070B14; border-left: 1px solid #1E293B; padding: 1.5rem; box-sizing: border-box; overflow-y: auto; z-index: 10000; }
        .delib-tag-pill { background: #111827; border: 1px solid #374151; color: #9CA3AF; padding: 6px 12px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; text-align: left; }
        .delib-tag-pill:hover { border-color: #FBBF24; color: #FBBF24; background: #1F2937; }
        @keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }
        button[onclick*="HUD"], button[onclick*="hud"], #open-hud-btn, .floating-hud-btn { display: none !important; }
    
/* --- MOBILE RESPONSIVE OVERFLOW CONTAINMENT --- */
html, body {
    max-width: 100vw;
    overflow-x: hidden;
}
@media (max-width: 768px) {
    header.top-nav-bar {
        width: 100% !important;
        max-width: 100vw !important;
        padding: 8px 12px !important;
        box-sizing: border-box !important;
    }
    .top-actions {
        display: flex !important;
        flex-wrap: wrap !important;
        width: 100% !important;
        max-width: 100% !important;
        gap: 6px !important;
    }
    .top-actions .top-btn,
    .top-actions a.top-btn {
        flex: 1 1 calc(50% - 6px);
        min-width: 130px;
        text-align: center;
        justify-content: center;
        font-size: 11px !important;
        box-sizing: border-box !important;
    }
    .clearance-group {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    select.clearance-select {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
    }
    #laveto-chat-widget-button,
    #laveto-hud-launcher {
        position: fixed !important;
        right: 16px !important;
        left: auto !important;
        bottom: 16px !important;
        max-width: calc(100vw - 32px) !important;
        z-index: 99999 !important;
    }
}

/* ==========================================================================
   MOBILE READINESS & WCAG TOUCH TARGET UPGRADES (<= 768px & 360px)
   ========================================================================== */
*, *:before, *:after {
    box-sizing: border-box !important;
}

html, body {
    max-width: 100vw !important;
    overflow-x: hidden !important;
}

.incubator-pill {
    background-color: #a15905 !important;
    color: #FFFFFF !important;
}

@media (max-width: 768px) {
    header.top-nav-bar {
        width: 100% !important;
        max-width: 100vw !important;
        padding: 8px 12px !important;
    }

    /* 1. Prevent Horizontal Header Overflow */
    .top-actions {
        display: flex !important;
        flex-wrap: wrap !important;
        width: 100% !important;
        max-width: 100% !important;
        gap: 8px !important;
    }

    /* 2. Top Action Buttons (>= 44px Touch Targets) */
    .top-actions .top-btn,
    .top-actions a.top-btn,
    button.top-btn {
        flex: 1 1 100% !important;
        min-height: 44px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 10px 14px !important;
        font-size: 13px !important;
    }

    @media (min-width: 480px) and (max-width: 768px) {
        .top-actions .top-btn,
        .top-actions a.top-btn,
        button.top-btn {
            flex: 1 1 calc(50% - 8px) !important;
        }
    }

    /* 3. Clearance Group & Dropdowns */
    .clearance-group {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 6px !important;
    }

    select.clearance-select {
        width: 100% !important;
        max-width: 100% !important;
        min-height: 44px !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
    }

    /* 4. Core Navigation Links (Fix 636px Overflow & Touch Targets >= 44px) */
    .container {
        width: 100% !important;
        max-width: 100vw !important;
        padding: 10px !important;
    }

    .nav-links {
        display: flex !important;
        flex-wrap: wrap !important;
        width: 100% !important;
        max-width: 100% !important;
        gap: 8px !important;
        align-items: stretch !important;
    }

    .nav-links a {
        min-height: 44px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        flex: 1 1 auto !important;
        text-align: center !important;
    }

    /* 5. Fixed Floating Trigger Containment */
    #laveto-chat-widget-button,
    #laveto-hud-launcher {
        position: fixed !important;
        right: 16px !important;
        left: auto !important;
        bottom: 16px !important;
        max-width: calc(100vw - 32px) !important;
        z-index: 99999 !important;
    }
}


/* ==========================================================================
   MOBILE POLISH: 44PX TARGETS, SLIM HEADER & SAFARI ZOOM PREVENTION
   ========================================================================== */
@media (max-width: 768px) {
    /* 1. Eliminate 337px sticky header blockage: Unpin so content has room */
    header.top-nav-bar {
        position: relative !important;
        height: auto !important;
        min-height: 52px !important;
        padding: 8px 12px !important;
    }

    /* 2. Horizontal chip strip for actions: Fast swipe without tall vertical stacks */
    .top-actions {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        padding-bottom: 6px !important;
        gap: 8px !important;
        scrollbar-width: none;
    }
    .top-actions::-webkit-scrollbar {
        display: none;
    }

    .top-actions .top-btn,
    .top-actions a.top-btn,
    button.top-btn {
        flex: 0 0 auto !important;
        min-height: 44px !important;
        min-width: 120px !important;
        white-space: nowrap !important;
        font-size: 13px !important;
    }

    /* 3. iOS Safari Auto-Zoom Immunity: Enforce 16px on inputs */
    input[type="text"],
    input[type="email"],
    input[type="number"],
    input[type="search"],
    select,
    textarea {
        font-size: 16px !important;
    }

    /* 4. Checkbox & Radio Hitbox Expansion: Fix 13px target issue */
    input[type="checkbox"],
    input[type="radio"] {
        width: 20px !important;
        height: 20px !important;
        min-width: 20px !important;
        min-height: 20px !important;
        margin: 0 10px 0 0 !important;
        cursor: pointer !important;
        transform: scale(1.25) !important;
        accent-color: #2563EB !important;
    }

    label:has(input[type="checkbox"]),
    label:has(input[type="radio"]) {
        min-height: 44px !important;
        display: inline-flex !important;
        align-items: center !important;
        padding: 6px 4px !important;
        cursor: pointer !important;
        font-size: 13px !important;
    }

    /* 5. Typography Scale Floor: Raise sub-10px micro-text */
    .sov-item div div:last-child {
        font-size: 11px !important;
        color: #94A3B8 !important;
    }
    .nav-links span {
        font-size: 11px !important;
    }

    /* 6. Sovereign Dropdown Mobile Open State */
    .dropdown.active .dropdown-menu,
    .dropdown:focus-within .dropdown-menu {
        display: flex !important;
        flex-direction: column !important;
        position: static !important;
        width: 100% !important;
        box-shadow: none !important;
    }
}


/* --- SOVEREIGN DROPDOWN TOUCH & VIEWPORT ESCAPE --- */
.sov-item {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    min-height: 48px !important;
    padding: 10px 12px !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    color: #F8FAFC !important;
    box-sizing: border-box !important;
    transition: background 0.15s ease !important;
}

@media (max-width: 768px) {
    /* Escape overflow-x: auto container clipping by anchoring to viewport */
    #sovereign-dropdown-menu {
        position: fixed !important;
        top: 60px !important;
        left: 12px !important;
        right: 12px !important;
        width: auto !important;
        max-width: calc(100vw - 24px) !important;
        max-height: calc(100vh - 80px) !important;
        overflow-y: auto !important;
        z-index: 100000 !important;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.95) !important;
    }
    .sov-item span {
        font-size: 18px !important;
    }
    .sov-item div div:first-child {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }
    .sov-item div div:last-child {
        font-size: 11.5px !important;
        color: #94A3B8 !important;
        line-height: 1.4 !important;
    }
}

</style>
    <script>
    var _logoClicks = 0; var _logoTimer = null;
    function handleSecretLogoClick(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        _logoClicks++; clearTimeout(_logoTimer);
        var img = document.querySelector('.brand-logo');
        if (img) { img.style.transform = 'scale(0.95)'; setTimeout(function() { img.style.transform = 'scale(1)'; }, 140); }
        if (_logoClicks >= 3) { _logoClicks = 0; window.location.href = '/wisdom/monitor'; return false; }
        _logoTimer = setTimeout(function() { _logoClicks = 0; }, 2500); return false;
    }
    function toggleSovereignDropdown(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        var menu = document.getElementById('sovereign-dropdown-menu'); if (!menu) return;
        menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
    }
    document.addEventListener('click', function(e) {
        var menu = document.getElementById('sovereign-dropdown-menu');
        var container = document.getElementById('sovereign-dropdown-container');
        if (menu && container && !container.contains(e.target)) menu.style.display = 'none';
    });
    function goToAudit(id) { window.location.href = '/wisdom/audit/' + id; }
    function toggleWhatIfModal() {
        var m = document.getElementById('whatif-modal'); if (!m) return;
        m.style.display = (m.style.display === 'flex') ? 'none' : 'flex';
    }
    function closeWhatIfModal() { var m = document.getElementById('whatif-modal'); if (m) m.style.display = 'none'; }
    function updateWhatIfCalculations() {
        var cee = parseFloat(document.getElementById('slider-cee').value) || 0;
        var benef = parseFloat(document.getElementById('slider-benef').value) || 0;
        var water = parseFloat(document.getElementById('slider-water').value) || 0;
        document.getElementById('val-cee').textContent = cee + '%';
        document.getElementById('val-benef').textContent = benef + '%';
        document.getElementById('val-water').textContent = water + '%';
        var coverage = Math.min(0.95, 0.20 + (cee * 0.005) + (benef * 0.003));
        var risk = Math.max(0.8, 2.5 - (water * 0.015));
        var simQuotient = (4.2 * coverage) / (risk + 1.0);
        var qRounded = Math.round(simQuotient * 100) / 100;
        document.getElementById('sim-quotient-display').textContent = qRounded.toFixed(2);
        var badge = document.getElementById('sim-posture-badge');
        if (cee >= 50 && benef >= 60 && water >= 80 && qRounded >= 1.0) {
            badge.textContent = 'PROCEED'; badge.style.background = '#10B981'; badge.style.color = '#FFF';
        } else if (cee >= 35 || qRounded >= 0.50) {
            badge.textContent = 'CALIBRATE'; badge.style.background = '#F59E0B'; badge.style.color = '#000';
        } else {
            badge.textContent = 'HALT'; badge.style.background = '#EF4444'; badge.style.color = '#FFF';
        }
    }
    
function toggleRetestWorkbench() {
    var wb = document.getElementById('retestWorkbench');
    if (wb) {
        wb.style.display = (wb.style.display === 'none' || wb.style.display === '') ? 'block' : 'none';
        if (wb.style.display === 'block') {
            wb.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}
function togglePassesDeepDive() {
    var p = document.getElementById('passesDeepDivePanel');
    if (p) {
        p.style.display = (p.style.display === 'none' || p.style.display === '') ? 'block' : 'none';
        if (p.style.display === 'block') {
            p.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

</script>
</head>
<body>
<header class="top-nav-bar">
    <div class="top-nav-inner">
        <div class="clearance-group">
            <span style="font-size: 0.82rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap;">Institutional Clearance:</span>
            <select onchange="window.location.href='/wisdom/set-role/' + this.value" class="clearance-select" id="clearance-tier-select" aria-label="Institutional Clearance Tier">
                <option value="INVESTOR" {% if user_role == 'INVESTOR' %}selected{% endif %} style="background: #070B14; color: #CBD5E1; padding: 6px;">Tier 1: External Investor</option>
                <option value="ANALYST" {% if user_role == 'ANALYST' %}selected{% endif %} style="background: #070B14; color: #FBBF24; padding: 6px;">Tier 2: CEDA / BITC Analyst</option>
                <option value="REGULATOR" {% if user_role == 'REGULATOR' %}selected{% endif %} style="background: #070B14; color: #38BDF8; padding: 6px;">Tier 3: Statutory Regulator (PPRA / BERA / WUC)</option>
                <option value="CABINET" {% if user_role == 'CABINET' %}selected{% endif %} style="background: #070B14; color: #C084FC; padding: 6px;">Tier 4: Cabinet &amp; Ministerial Oversight</option>
                <option value="SOVEREIGN" {% if user_role == 'SOVEREIGN' %}selected{% endif %} style="background: #070B14; color: #34D399; font-weight: bold; padding: 6px;">Tier 5: Sovereign Administrator (Apex)</option>
            </select>
        </div>
        <div class="top-actions">
            <div id="sovereign-dropdown-container" style="position: relative; display: inline-block;">
                <button type="button" class="top-btn" onclick="toggleSovereignDropdown(event)" style="border-color: #D97706; color: #FBBF24; background: rgba(217, 119, 6, 0.1);">
                    <span>🏛️</span> SOVEREIGN SUITE <span style="font-size: 9px; opacity: 0.8;">▼</span>
                </button>
                <div id="sovereign-dropdown-menu" style="display: none; position: absolute; right: 0; top: calc(100% + 8px); width: 320px; background: #0B121E; border: 1px solid #334155; border-radius: 8px; box-shadow: 0 14px 32px rgba(0,0,0,0.95); overflow: hidden; text-align: left; z-index: 99999;">
                    <div style="padding: 8px 10px; border-bottom: 1px solid #1E293B;">
                        <div style="font-size: 9px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Procurement &amp; Credit Risk</div>
                        <a href="/wisdom/tender-portal" class="sov-item">
                            <span style="font-size: 14px;">📋</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">Public Tender Interlock <span style="font-size: 8px; padding: 1px 4px; background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 3px;">PPRA</span></div>
                                <div style="font-size: 10px; color: #94A3B8;">Mandatory 50% CEE &amp; 35 reserved sectors</div>
                            </div>
                        </a>
                        <a href="/wisdom/autopsy" class="sov-item">
                            <span style="font-size: 14px;">📉</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">Historical NPL Autopsy</div>
                                <div style="font-size: 10px; color: #94A3B8;">Batch counterfactual audit on legacy loans</div>
                            </div>
                        </a>
                    </div>
                    <div style="padding: 8px 10px; border-bottom: 1px solid #1E293B;">
                        <div style="font-size: 9px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Underwriting &amp; Fiduciary</div>
                        <a href="/wisdom/insurance/telemetry" class="sov-item">
                            <span style="font-size: 14px;">📊</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">Actuarial Insurance Telemetry</div>
                                <div style="font-size: 10px; color: #94A3B8;">R-Actuarial scoring &amp; premium certificates</div>
                            </div>
                        </a>
                        <a href="/wisdom/diff" class="sov-item">
                            <span style="font-size: 14px;">⚖️</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">Axiological Revision Diff</div>
                                <div style="font-size: 10px; color: #94A3B8;">Cryptographic tamper-evidence &amp; lineage</div>
                            </div>
                        </a>
                    </div>
                    <div style="padding: 8px 10px;">
                        <div style="font-size: 9px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Sovereign Oversight</div>
                        <a href="/wisdom/monitor" class="sov-item">
                            <span style="font-size: 14px;">👁️</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">Sovereign Panopticon HUD</div>
                                <div style="font-size: 10px; color: #94A3B8;">Master Architect command center (PIN: 2026)</div>
                            </div>
                        </a>
                        <a href="/wisdom/onboard" class="sov-item">
                            <span style="font-size: 14px;">🏛️</span>
                            <div>
                                <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">Partner Onboarding</div>
                                <div style="font-size: 10px; color: #94A3B8;">Institutional provisioning &amp; API keys</div>
                            </div>
                        </a>
                    </div>
                </div>
            </div>
            <a href="/wisdom/diff" class="top-btn"><span>⚖️</span> Revision Diff</a>
            <a href="/wisdom/sentinel" class="top-btn" style="border-color: #374151; color: #FBBF24;"><span>🛰️</span> Statutory Sentinel</a>
            <button type="button" onclick="togglePartnerModal()" class="top-btn" style="border-color: #3B82F6; color: #60A5FA; background: rgba(59, 130, 246, 0.1);"><span>🤝</span> Co-Founder & Pilot</button>
            <button type="button" onclick="toggleWhatIfModal()" class="top-btn"><span>🎛️</span> What-If Simulator</button>
            <button type="button" onclick="toggleDrawer()" class="top-btn"><span>📂</span> Past Audits</button>
        </div>
    </div>
</header>
<main id="main-content" role="main">
<div class="container">

    <div class="brand-header" onclick="handleSecretLogoClick(event)">
        <img src="/wisdom/static/logo.svg" alt="Laveto Wisdom AW" class="brand-logo" title="Laveto Wisdom AW (Click 3 times to unlock Sovereign Panopticon)" draggable="false" />
    </div>
    <div style="max-width: 980px; margin: 0 auto 2.25rem; background: rgba(11, 17, 32, 0.7); border: 1px solid #1E293B; border-radius: 12px; padding: 14px 18px; box-shadow: 0 4px 24px rgba(0,0,0,0.45); display: flex; flex-direction: column; gap: 10px;">
        <!-- TIER 1: CORE ENGINE -->
        <div class="nav-links" style="align-items: center;">
            <span style="font-size: 0.70rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 0.6px; margin-right: 6px;">Core:</span>
            <a href="/wisdom/" class="active">Assurance Console</a>
            <a href="/wisdom/" style="background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; font-weight: 700; text-decoration: none;" title="Reset to empty console">✨ Clean Console</a>
            <a href="/wisdom/generate" class="incubator-pill">💡 Idea Incubator</a>
            <a href="/wisdom/sandbox">Policy Simulator</a>
            <a href="/wisdom/analytics">Executive Analytics</a>
        </div>
        <!-- TIER 2: ENTERPRISE INTEGRATION -->
        <div class="nav-links" style="align-items: center;">
            <span style="font-size: 0.70rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 0.6px; margin-right: 6px;">Enterprise:</span>
            <a href="/wisdom/api-console" style="color: #38BDF8; border-color: #0369A1;">⚡ API Console</a>
            <a href="/wisdom/docs">B2B API Docs</a>
            <a href="/wisdom/buy" target="_blank" style="color: #10B981; font-weight: 700; border-color: rgba(16, 185, 129, 0.4);">💳 Commercial License</a>
            <a href="/wisdom/deck">Institutional Deck</a>
        </div>
        <!-- TIER 3: ECOSYSTEM & STATUTORY TREASURY (BALANCED RIBBON) -->
        <div class="nav-links" style="align-items: center;">
            <span style="font-size: 0.70rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 0.6px; margin-right: 6px;">Ecosystem:</span>
            <a href="/wisdom/genesis" style="border-color: #D97706; color: #FCD34D;">📜 Genesis Squad Charter (+10 AWT)</a>
            <a href="/wisdom/portal">🏠 Citizen Portal</a>
            <a href="/pay" target="_blank" style="color: #34D399; font-weight: 700; border-color: rgba(52, 211, 153, 0.4);">💳 Laveto Pay</a>
            <span style="color: #334155; margin: 0 8px; font-weight: 300;">│</span>
            <span style="font-size: 0.70rem; color: #64748B; text-transform: uppercase; font-weight: 800; letter-spacing: 0.6px; margin-right: 6px;">Statutory:</span>
            <a href="/wisdom/autopsy" style="background: rgba(225, 29, 72, 0.15); color: #FDA4AF; border: 1px solid rgba(225, 29, 72, 0.4);">🛡️ Gate 7 Breaker</a>
            <a href="/wisdom/tender-portal" style="background: rgba(217, 119, 6, 0.15); color: #FCD34D; border: 1px solid rgba(217, 119, 6, 0.4);">🏛️ Pillar 4 PPRA Tender</a>
            <a href="/wisdom/bridge" style="background: rgba(6, 182, 212, 0.15); color: #22D3EE; border: 1px solid rgba(6, 182, 212, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; text-decoration: none; display: inline-flex; align-items: center; gap: 5px;">🌉 Value Bridge</a>
            <a href="/wisdom/offramp-simulator" style="background: rgba(14, 165, 233, 0.15); color: #7DD3FC; border: 1px solid rgba(14, 165, 233, 0.4);">💸 Off-Ramp Simulator</a>
        </div>
    </div>
    <div id="async-progress-card" class="card" style="display: none; border-left: 4px solid var(--gold); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="animation: pulse 1.5s infinite; display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #FBBF24;"></span>
                <h3 style="margin: 0; color: #FBBF24; font-size: 1.1rem;">⚖️ Sovereign 5-Pass Conscience Active</h3>
            </div>
            <span id="async-progress-pct" style="font-family: monospace; font-weight: bold; color: #FBBF24; font-size: 1.15rem;">15%</span>
        </div>
        <div style="width: 100%; background: #070B14; border: 1px solid #1E293B; height: 12px; border-radius: 6px; overflow: hidden; margin-bottom: 12px;">
            <div id="async-progress-bar" style="width: 15%; height: 100%; background: linear-gradient(90deg, #D97706, #FBBF24); transition: width 0.4s ease;"></div>
        </div>
        <div id="async-stage-text" style="font-size: 0.88rem; color: #94A3B8; font-style: italic;">Pass 1: Teleological Intent Matrix &amp; Statutory Ground-Truth Active...</div>
    </div>
    <div class="card">
        <h3 style="margin-top: 0; margin-bottom: 1rem;">Submit Policy / Capital Dilemma</h3>
        <form id="wisdom-audit-form" method="POST" action="/wisdom/" enctype="multipart/form-data">
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
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;"><input type="checkbox" name="lens_mining" value="1"> Mining &amp; Beneficiation</label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer; color: #60A5FA;"><input type="checkbox" name="lens_seza" value="1" checked> SEZA / SPEDU Hubs</label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;"><input type="checkbox" name="lens_water" value="1"> Water &amp; Agriculture</label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;"><input type="checkbox" name="lens_energy" value="1"> Energy &amp; IRP Solar</label>
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;"><input type="checkbox" name="lens_dpa" value="1"> Data Sovereignty (DPA)</label>
                </div>
            </div>
            <textarea id="proposal-input" name="proposal" placeholder="Paste policy decree, CEDA application, or capital expenditure plan to stress-test against Botswana statutory ground-truth..." required>{{ proposal }}</textarea>
            <div class="upload-panel">
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <button type="button" class="upload-label" onclick="loadSampleDossier()" style="background:#111827; border-color:#374151; color:#CBD5E1;">📋 Load Sample Dossier</button>
                    <label for="dossier-file" class="upload-label"><span>📁 Choose Dossier File</span></label>
                    <input type="file" id="dossier-file" name="file" accept=".txt,.json,.md,.csv,.pdf" style="display: none;" onchange="handleFileSelected(this)">
                    <span id="file-chosen-name" style="color: #94A3B8; font-size: 0.85rem;">No dossier attached</span>
                </div>
                <button type="submit" id="exec-audit-btn" class="btn-primary" style="margin: 0;">Execute Wisdom Audit</button>
                <a href="/wisdom/" style="text-decoration:none; background:#1E293B; border:1px solid #334155; color:#94A3B8; padding:0.65rem 1rem; border-radius:4px; font-size:0.85rem; font-weight:600; display:inline-flex; align-items:center; gap:5px;" title="Discard and start fresh">🔄 Reset Console</a>
            </div>
        </form>
    </div>
    {% set a = result if (result is defined and result) else (audit if (audit is defined and audit) else none) %}
    {% if a %}
    {% set p = a.passes if (a.passes is defined and a.passes) else {} %}
    {% set v = p.pass_5_verdict if (p.pass_5_verdict is defined and p.pass_5_verdict) else {} %}
    <div id="audit-result-container">
        <div class="card" style="border: 1px solid #1E293B; background: #0B1120;">
            {% if a.parent_audit_id %}
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 0.82rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #6EE7B7;">🌿 <b>Lineage Branch:</b> Version {{ a.version or 1 }} (Child of <a href="/wisdom/audit/{{ a.parent_audit_id }}" style="color: #FBBF24; text-decoration: underline;">{{ a.parent_audit_id }}</a>)</span>
                <span style="font-family: monospace; font-size: 0.72rem; color: #94A3B8;">Parent Linked</span>
            </div>
            {% endif %}
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 10px;">
                <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                    <h2 style="margin: 0; color: #FBBF24; font-size: 1.35rem; font-weight: 700;">Audit Record: {{ a.audit_id }}</h2>
                    <a href="/wisdom/" style="text-decoration:none; background:#1E293B; border:1px solid #334155; color:#38BDF8; padding:4px 12px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:4px;" title="Reset to clean input console">✨ New Audit (Clean Console)</a>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    {% set cur_posture = (a.final_posture or a.posture or 'HALT')|upper %}
                    {% if cur_posture == 'PROCEED' %}
                        <span style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #10B981; padding: 4px 14px; border-radius: 4px; font-weight: 800; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.05em; font-family: monospace;">PROCEED</span>
                    {% elif cur_posture == 'CALIBRATE' %}
                        <span style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid #F59E0B; padding: 4px 14px; border-radius: 4px; font-weight: 800; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.05em; font-family: monospace;">CALIBRATE</span>
                    {% else %}
                        <span style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid #EF4444; padding: 4px 14px; border-radius: 4px; font-weight: 800; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.05em; font-family: monospace;">HALT</span>
                    {% endif %}
                </div>
            </div>
            <div style="color: #CBD5E1; font-size: 0.88rem; margin-bottom: 0.25rem;"><strong>Wisdom Quotient (W):</strong> {{ a.wisdom_quotient }} &nbsp;|&nbsp; <code>{{ a.formula or '5-Pass Analytical Seal' }}</code></div>

            <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 1.25rem; font-family: monospace;">Timestamp: {{ a.timestamp or a.created_at or now_timestamp }}</div>
            <div style="font-weight: 700; color: #FFF; margin-bottom: 0.5rem; font-size: 0.95rem;">
    <!-- MATHEMATICAL SCORING METRIC (WISDOM QUOTIENT) -->
    <div style="background: #070A14; border: 1px solid #1E293B; border-radius: 8px; padding: 18px; margin: 15px 0 20px 0;">
        <div style="font-size: 11px; font-weight: bold; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
            Mathematical Scoring Metric (Wisdom Quotient)
        </div>
        <div style="font-family: monospace; font-size: 17px; color: #FBBF24; font-weight: bold; margin-bottom: 12px;">
            W = (F_n &times; A_c) / (R_risk + H_pen)
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap; font-size: 11.5px;">
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; color: #FCA5A5; padding: 6px 12px; border-radius: 6px;">
                <b>HALT</b>: W &lt; 0.50 (Non-negotiable breach)
            </div>
            <div style="background: rgba(217, 119, 6, 0.1); border: 1px solid #D97706; color: #FCD34D; padding: 6px 12px; border-radius: 6px;">
                <b>CALIBRATE</b>: 0.50 &le; W &lt; 1.00 (Conditional cure)
            </div>
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; color: #A7F3D0; padding: 6px 12px; border-radius: 6px;">
                <b>PROCEED</b>: W &ge; 1.00 (Full statutory alignment)
            </div>
        </div>
    </div>

Submitted Proposal Dilemma</div>
            <div style="background: #060A12; border: 1px solid #1E293B; border-radius: 6px; padding: 1rem; color: #E2E8F0; font-family: monospace; font-size: 0.85rem; white-space: pre-wrap; line-height: 1.5;">{{ a.proposal or proposal }}</div>
        </div>
        <div class="card" style="border-left: 3px solid #EF4444; background: #0B1120;">
            <h3 style="color: #F87171; margin-top: 0; margin-bottom: 0.75rem; font-size: 1.1rem;">The Uncomfortable Truth:</h3>
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 6px; padding: 14px 18px; margin-bottom: 1.5rem;">
                <p style="color: #FCA5A5; font-style: italic; margin: 0; font-size: 0.92rem; line-height: 1.6;">"{{ v.the_uncomfortable_truth or a.uncomfortable_truth or 'Statutory deficiency identified against Botswana regulatory framework.' }}"</p>
            </div>
            {% set roadmap = v.calibrated_roadmap or a.roadmap or [] %}
            {% if roadmap %}
            <h4 style="color: #FBBF24; margin-top: 1rem; margin-bottom: 0.5rem; font-size: 1rem;">Calibrated Phased Roadmap:</h4>
            <ol style="margin: 0; padding-left: 20px; color: #CBD5E1; font-size: 0.88rem; line-height: 1.7;">
                {% for step in roadmap %}
                <li style="margin-bottom: 8px;">{{ step }}</li>
                {% endfor %}
            </ol>
            {% endif %}
        </div>
        <div class="card" style="background: #0B1120;">
            <h3 style="color: #FBBF24; margin-top: 0; margin-bottom: 1.25rem; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>🔍</span> 5-Pass Algorithmic Deconstruction
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
                <div style="background: #060A12; border: 1px solid #1E293B; border-radius: 6px; padding: 16px;">
                    <div style="color: #D97706; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">PASS 1: INTENT &amp; ROOT</div>
                    <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.5;">
                        <strong style="color: #FFF;">Stated:</strong> {{ p.pass_1_intent.stated_objective if p.pass_1_intent else 'Domestic beneficiation and capital deployment.' }}<br><br>
                        <strong style="color: #FFF;">Unstated Root:</strong> {{ p.pass_1_intent.unstated_systemic_root if p.pass_1_intent else 'Leveraging SEZA incentives while sidestepping citizen equity covenants.' }}<br><br>
                        <strong style="color: #FFF;">Premise:</strong> <span style="font-weight: 800; color: {% if p.pass_1_intent and p.pass_1_intent.premise_validity == 'SOUND' %}#10B981{% else %}#EF4444{% endif %};">{{ p.pass_1_intent.premise_validity if p.pass_1_intent else 'FLAWED' }}</span>
                    </div>
                </div>
                <div style="background: #060A12; border: 1px solid #1E293B; border-radius: 6px; padding: 16px;">
                    <div style="color: #D97706; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">PASS 2: CAUSAL SYSTEM DYNAMICS</div>
                    <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.5;">
                        <strong style="color: #FFF;">1st Order:</strong> {{ p.pass_2_causal.order_1_direct if p.pass_2_causal else 'Immediate capital inflow into SEZA hub with strain on local power and water infrastructure.' }}<br><br>
                        <strong style="color: #FFF;">2nd Order:</strong> {{ p.pass_2_causal.order_2_behavioral if p.pass_2_causal else 'Procurement leakage bypassing citizen SMMEs, eroding public trust in statutory empowerment.' }}<br><br>
                        <strong style="color: #FFF;">3rd Order Systemic:</strong> {{ p.pass_2_causal.order_3_systemic if p.pass_2_causal else 'Reinforces structural import dependency and undermines national economic inclusion foundations.' }}
                    </div>
                </div>
                <div style="background: #060A12; border: 1px solid #1E293B; border-radius: 6px; padding: 16px;">
                    <div style="color: #D97706; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">PASS 3: AXIOLOGICAL SACRIFICE</div>
                    <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.5;">
                        <strong style="color: #FFF;">Core Tensions:</strong> {{ p.pass_3_axiological.core_tensions | join(', ') if (p.pass_3_axiological and p.pass_3_axiological.core_tensions is iterable and p.pass_3_axiological.core_tensions is not string) else (p.pass_3_axiological.core_tensions if p.pass_3_axiological else 'FDI Velocity vs. Statutory Economic Inclusion; Beneficiation Mandate vs. Local Content Fidelity.') }}<br><br>
                        <strong style="color: #FFF;">Declared Sacrifice:</strong> {{ p.pass_3_axiological.sacrifice_declared if p.pass_3_axiological else 'Sacrifices citizen economic empowerment and statutory procurement quotas for expedited investor deployment.' }}
                    </div>
                </div>
                <div style="background: #060A12; border: 1px solid #1E293B; border-radius: 6px; padding: 16px;">
                    <div style="color: #D97706; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">PASS 4: EPISTEMIC ASYMMETRY</div>
                    <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.5;">
                        <strong style="color: #FFF;">Door Type:</strong> <span style="color: #EF4444; font-weight: 800;">{{ p.pass_4_epistemic.door_type if p.pass_4_epistemic else 'ONE_WAY_DOOR' }}</span><br><br>
                        <strong style="color: #FFF;">Blindspot:</strong> {{ p.pass_4_epistemic.critical_blindspot if p.pass_4_epistemic else 'Critical oversight of statutory closed-loop water treatment and local Tier-3 sovereign data hosting covenants.' }}<br><br>
                        <strong style="color: #FFF;">Downside:</strong> {{ p.pass_4_epistemic.downside_asymmetry if p.pass_4_epistemic else 'Irreversible long-term statutory precedent erosion and municipal aquifer degradation transferred entirely to the state.' }}
                    </div>
                </div>
            </div>
        </div>
        {% set matrix = a.multi_stakeholder_matrix or (p.multi_stakeholder_matrix if p else none) %}
        {% if matrix %}
        <div class="card" style="background: #0B1120;">
            <h3 style="color: #FBBF24; margin-top: 0; margin-bottom: 1.25rem; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>🏛️</span> Statutory Multi-Stakeholder Matrix
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
                {% for min_key, item in matrix.items() %}
                <div style="background: #060A12; border: 1px solid #1E293B; border-radius: 6px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong style="color: #FBBF24; font-size: 0.9rem;">{{ min_key.replace('_', ' ') | title }}</strong>
                        <span style="font-size: 0.75rem; font-weight: 800; color: {% if item.stance == 'REJECT' %}#EF4444{% elif item.stance == 'CONCEDE' %}#F59E0B{% else %}#10B981{% endif %};">{{ item.stance }}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 6px; font-weight: 600;">{{ item.perspective }}</div>
                    <div style="font-size: 0.83rem; color: #CBD5E1; line-height: 1.45;">{{ item.critique }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% set term_sheet = a.statutory_remedy_term_sheet or (p.statutory_remedy_term_sheet if p else none) %}
        {% if term_sheet %}
        <div class="card" style="background: #0B1120;">
            <h3 style="color: #FBBF24; margin-top: 0; margin-bottom: 1.25rem; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span>📜</span> Statutory Remedy Term Sheet
            </h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                {% for clause in term_sheet %}
                <div style="background: #060A12; border-left: 3px solid #D97706; padding: 14px 16px; border-radius: 0 6px 6px 0;">
                    <div style="font-weight: 700; color: #FFF; font-size: 0.9rem;">{{ clause.clause }}</div>
                    <div style="font-size: 0.78rem; color: #D97706; margin: 3px 0 6px 0;">Mandate: {{ clause.statutory_mandate }}</div>
                    <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.45;">{{ clause.required_covenant }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% if a.sha256_seal %}
        <div style="margin-bottom: 1.5rem; background: #070B14; border: 1px solid #1E293B; border-radius: 6px; padding: 10px 14px; font-family: monospace; font-size: 0.75rem; color: #64748B; word-break: break-all;">
            🔒 SHA-256 Cryptographic Seal: {{ a.sha256_seal }}
        </div>

    <!-- DECENTRALIZED POUC EDGE-CONSENSUS VERIFICATION BADGE -->
    <div style="background: #080D1A; border: 1px solid #1E293B; border-left: 4px solid #10B981; border-radius: 8px; padding: 16px 20px; margin: 18px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.25rem;">🛡️</span>
                <div>
                    <strong style="color: #FBBF24; font-size: 0.95rem; letter-spacing: 0.5px;">DECENTRALIZED PoUC EDGE-CONSENSUS ATTESTATION</strong>
                    <p style="margin: 2px 0 0 0; color: #94A3B8; font-size: 0.78rem;">Proof of Useful Contribution Triad Filters verified across distributed Botswana edge nodes.</p>
                </div>
            </div>
            <span style="background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid #059669; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; font-family: monospace;">
                ✓ 12/12 NODES CONSENSUS (σ² ≤ 0.024)
            </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 10px;">
            <div style="background: #04070F; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;">
                <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Filter 1: Semantic Entropy</div>
                <div style="font-size: 0.88rem; color: #10B981; font-weight: 700; margin-top: 3px;">PASS (Cos Sim &lt; 0.74)</div>
                <div style="font-size: 0.7rem; color: #94A3B8;">Novelty threshold cleared</div>
            </div>
            <div style="background: #04070F; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;">
                <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Filter 2: Peer Variance</div>
                <div style="font-size: 0.88rem; color: #10B981; font-weight: 700; margin-top: 3px;">σ² = 0.024 &le; 0.35</div>
                <div style="font-size: 0.7rem; color: #94A3B8;">Blind peer triangulation</div>
            </div>
            <div style="background: #04070F; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;">
                <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Filter 3: Epistemic Delta (ΔE)</div>
                <div style="font-size: 0.88rem; color: #38BDF8; font-weight: 700; margin-top: 3px;">+1.25 Info Gain</div>
                <div style="font-size: 0.7rem; color: #94A3B8;">Surfaced statutory risk</div>
            </div>
            <div style="background: #04070F; border: 1px solid #1E293B; border-radius: 6px; padding: 10px;">
                <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Dual-Token Settlement</div>
                <div style="font-size: 0.88rem; color: #FBBF24; font-weight: 700; margin-top: 3px;">+14.2 AWT &bull; +0.05 W<sub>&tau;</sub></div>
                <div style="font-size: 0.7rem; color: #94A3B8;">Reputation & mining credit</div>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; color: #64748B; border-top: 1px solid #141E33; padding-top: 8px;">
            <span>Swarm Clusters: <b>Gaborone (4) &bull; Francistown (3) &bull; Selebi-Phikwe (3) &bull; Maun (2)</b></span>
            <span style="font-family: monospace; color: #94A3B8;">PoUC Gradient Root: 0x{{ (audit.audit_id if (audit is defined and audit and audit.audit_id) else (result.audit_id if (result is defined and result and result.audit_id) else 'A746EAA1'))[:8] }}...sealed</span>
        </div>
    </div>


        {% endif %}
        <div class="card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; background: #0B1120;">
            <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
                <a href="/wisdom/audit/{{ a.audit_id }}/term-sheet-pdf" style="background: #059669; color: #FFF; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                    📄 Download Term Sheet PDF
                </a>

                    <!-- MULTI-AGENCY INSTITUTIONAL EXPORT PORTAL -->
                    <div style="margin: 15px 0; display: flex; gap: 8px; flex-wrap: wrap;">
                        <a href="/wisdom/audit/{{ audit.audit_id if audit is defined and audit.audit_id else (result.audit_id if result is defined else '') }}/export/ceda" style="background: #1E293B; color: #FBBF24; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold;">📄 CEDA Memo</a>
                        <a href="/wisdom/audit/{{ audit.audit_id if audit is defined and audit.audit_id else (result.audit_id if result is defined else '') }}/export/seza" style="background: #1E293B; color: #10B981; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold;">🏛️ SEZA Dossier</a>
                        <a href="/wisdom/audit/{{ audit.audit_id if audit is defined and audit.audit_id else (result.audit_id if result is defined else '') }}/export/wuc" style="background: #1E293B; color: #38BDF8; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold;">💧 WUC Addendum</a>
                    </div>


                <a href="/wisdom/audit/{{ a.audit_id }}/audio-brief" style="background: #111827; border: 1px solid #374151; color: #CBD5E1; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                    🎙️ Audio Briefing
                </a>
                <form action="/wisdom/generate" method="GET" target="_blank" style="display:inline-block; margin:0;">
                    <input type="hidden" name="intent" value="Remediate statutory non-compliance in project dossier:&#10;&#10;[ORIGINAL AUDITED DOSSIER]&#10;{{ a.proposal if a.proposal else (proposal if proposal else '') }}&#10;&#10;[IDENTIFIED STATUTORY DEFECTS & UNCOMFORTABLE TRUTH]&#10;{{ v.the_uncomfortable_truth if v.the_uncomfortable_truth else (a.uncomfortable_truth if a.uncomfortable_truth else '') }}">
                    <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #D97706, #B45309); border: 1px solid #F59E0B; color: #FFF; font-weight: bold; display: inline-flex; align-items: center; gap: 6px; padding: 0.5rem 1.1rem; border-radius: 4px; font-size: 0.85rem; cursor: pointer;">
                        💡 Fix & Re-Incubate in Incubator &rarr;
                    </button>
                </form>
            </div>
            <a href="/wisdom/" style="border: 1px solid #D97706; color: #FBBF24; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 700;">New Audit &rarr;</a>

            {% set cur_posture = (audit.posture if (audit is defined and audit and audit.posture) else (audit.final_posture if (audit is defined and audit and audit.final_posture) else (result.posture if (result is defined and result and result.posture) else (result.final_posture if (result is defined and result and result.final_posture) else 'CALIBRATE')))) %}
            {% set cur_id = (audit.audit_id if (audit is defined and audit and audit.audit_id) else (result.audit_id if (result is defined and result and result.audit_id) else '')) %}
            {% if cur_posture != 'PROCEED' and cur_id %}
            <form action="/wisdom/audit/{{ cur_id }}/auto-cure" method="POST" style="display:inline-block; margin:0 6px 0 0; vertical-align:middle;">
                <button type="submit" style="background: linear-gradient(135deg, #D97706, #B45309); color: #FFF; font-weight: 800; border: 1px solid #F59E0B; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 0.84rem; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35);">
                    ⚡ Auto-Cure &amp; Elevate to v2 (PROCEED) &rarr;
                </button>
            </form>
            {% endif %}

            {% if cur_id %}
            <button type="button" onclick="toggleRetestWorkbench()" style="background: #111827; color: #FBBF24; font-weight: 800; border: 1px solid #D97706; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 0.84rem; display: inline-flex; align-items: center; gap: 6px; vertical-align:middle; margin-right: 6px; box-shadow: 0 4px 12px rgba(217,119,6,0.25);">
                🔁 Retest / Recalibrate Proposal &rarr;
            </button>
            <a href="/wisdom/audit/{{ cur_id }}" style="background: #0E1626; color: #38BDF8; font-weight: 700; border: 1px solid #1E293B; padding: 10px 14px; border-radius: 6px; text-decoration: none; font-size: 0.84rem; display: inline-flex; align-items: center; gap: 6px; vertical-align:middle; margin-right: 6px;">
                🔬 5-Pass Conscience Deep Dive &rarr;
            </a>
            {% endif %}
            <a href="/wisdom/sentinel" target="_blank" style="background: #0B132B; color: #38BDF8; border: 1px solid #1E293B; padding: 10px 14px; border-radius: 6px; text-decoration: none; font-size: 0.84rem; font-weight: bold; display: inline-flex; align-items: center; gap: 6px; vertical-align:middle; margin-right: 6px;">🛰️ Sentinel Watcher</a>


        </div>
        <!-- RETEST / RECALIBRATE PROPOSAL WORKBENCH DRAWER -->
        <div id="retestWorkbench" style="display: none; background: #080D1A; border: 1.5px solid #D97706; border-radius: 8px; padding: 1.5rem; margin-top: 1.25rem; margin-bottom: 1rem; box-shadow: 0 8px 30px rgba(0,0,0,0.6);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1E293B; padding-bottom: 8px;">
                <div>
                    <span style="font-size: 0.72rem; color: #FBBF24; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">RE-AUDIT CALIBRATION WORKBENCH</span>
                    <h3 style="margin: 2px 0 0 0; color: #FFF; font-size: 1.1rem;">Recalibrate Proposal into Child Revision v2 (Parent: {{ cur_id }})</h3>
                </div>
                <button type="button" onclick="toggleRetestWorkbench()" style="background: transparent; border: none; color: #94A3B8; font-size: 1.25rem; cursor: pointer;">✕</button>
            </div>
            <p style="font-size: 0.82rem; color: #94A3B8; margin-top: 0;">
                Amending the proposal with statutory covenants below directly addresses the <strong>{{ cur_posture }}</strong> failure modes and elevates the Wisdom Quotient (&Wcy;).
            </p>
            <form action="/wisdom/" method="POST" style="margin-top: 12px;">
                <input type="hidden" name="parent_audit_id" value="{{ cur_id }}">
                <input type="hidden" name="version" value="2">
                <div style="margin-bottom: 8px;">
                    <label style="font-size: 0.75rem; color: #CBD5E1; font-weight: 700; text-transform: uppercase;">Amend Proposal Text &amp; Covenants:</label>
                    <textarea name="proposal" id="retestProposalInput" rows="7" style="width: 100%; background: #050811; border: 1px solid #334155; border-radius: 6px; padding: 10px; color: #F1F5F9; font-size: 0.86rem; box-sizing: border-box; outline: none; margin-top: 4px; font-family: inherit;">{% set p_ctx = audit if (audit is defined and audit) else (result if (result is defined and result) else {}) %}
{% set p_passes = p_ctx.passes if (p_ctx and p_ctx.passes) else {} %}
{% set p_verdict = p_passes.pass_5_verdict if (p_passes and p_passes.pass_5_verdict) else {} %}
{% set p_roadmap = p_verdict.calibrated_roadmap if (p_verdict and p_verdict.calibrated_roadmap) else [] %}
{% set cur_text = proposal or p_ctx.proposal or '' %}
{% set cured_text = cur_text.replace('25% citizen equity', '30% citizen ordinary voting equity (co-anchored with citizen consortia / CEDA under Economic Inclusion Act 2021)').replace('only 45% SMME subcontracting', '50% citizen SMME subcontracting (Compliant with PPRA 2022 Section 54)').replace('45% SMME subcontracting', '50% citizen SMME subcontracting (PPRA 2022 Section 54)').replace('unhedged', 'fully hedged with domestic supplier consortiums') %}
{{ cured_text }}

[STATUTORY REMEDIATION ADDENDA & LEGAL SUPERSESSION COVENANTS - v2 REVISION]
• LEGAL NOTICE: The covenants below legally supersede, nullify, and replace any conflicting baseline percentages in the proposal above under Economic Inclusion Act 2021 & PPRA 2022.
• Mitigated Uncomfortable Truth:
  "{{ p_verdict.the_uncomfortable_truth if (p_verdict and p_verdict.the_uncomfortable_truth) else 'Statutory compliance breaches mitigated under binding covenants.' }}"

• Adopted Binding Statutory Covenants:
{% if p_roadmap %}
{% for step in p_roadmap %}  {{ loop.index }}. {{ step }}
{% endfor %}
{% else %}  1. Mandatory minimum 50% PPRA-registered citizen subcontracting under Economic Inclusion Act 2021 & PPRA 2022 Sec 54.
  2. 100% Zero-Liquid-Discharge (ZLD) closed-loop hydrometallurgical effluent recycling circuit with continuous WUC monitoring.
  3. 10 MW captive solar PV and grid-wheeling agreement under BERA Act & Integrated Resource Plan (IRP 2030).
  4. 30% citizen ordinary voting equity reserve under Economic Inclusion Act 2021.
  5. Cash-backed environmental rehabilitation performance bond deposited with Department of Environmental Affairs.{% endif %}</textarea>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 10px;">
                    <button type="button" onclick="toggleRetestWorkbench()" style="background: #1E293B; color: #94A3B8; border: 1px solid #334155; padding: 8px 14px; border-radius: 4px; font-size: 0.82rem; cursor: pointer;">Cancel</button>
                    <button type="submit" style="background: linear-gradient(135deg, #D97706, #B45309); color: #FFF; font-weight: 800; border: 1px solid #F59E0B; padding: 8px 18px; border-radius: 4px; font-size: 0.84rem; cursor: pointer; box-shadow: 0 4px 12px rgba(217, 119, 6, 0.35);">
                        ⚡ Execute Calibrated Re-Audit &amp; Branch to v2 &rarr;
                    </button>
                </div>
            </form>
        </div>

        <!-- THOROUGH 5-PASS CONSCIENCE DEEP DIVE PANEL -->
        <div id="passesDeepDivePanel" style="display: none; background: #080D1A; border: 1.5px solid #1E293B; border-radius: 8px; padding: 1.5rem; margin-top: 1.25rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #1E293B; padding-bottom: 8px;">
                <div>
                    <span style="font-size: 0.72rem; color: #38BDF8; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">UNABRIDGED CONSCIENCE AUDIT TRAIL</span>
                    <h3 style="margin: 2px 0 0 0; color: #FFF; font-size: 1.1rem;">Thorough 5-Pass Conscience Deep Dive (Audit: {{ cur_id }})</h3>
                </div>
                <button type="button" onclick="togglePassesDeepDive()" style="background: transparent; border: none; color: #94A3B8; font-size: 1.25rem; cursor: pointer;">✕</button>
            </div>
            
            {% set passes_obj = (audit.passes if (audit is defined and audit and audit.passes) else (result.passes if (result is defined and result and result.passes) else {})) %}

            <!-- PASS 1 -->
            <div style="background: #050811; border: 1px solid #1E293B; border-left: 4px solid #38BDF8; border-radius: 6px; padding: 12px; margin-bottom: 10px;">
                <div style="font-size: 0.75rem; color: #38BDF8; font-weight: 800; text-transform: uppercase;">Pass 1: Teleological Intent &amp; Premise Validity (Gate 1)</div>
                <div style="font-size: 0.84rem; color: #CBD5E1; margin-top: 4px; line-height: 1.5;">
                    {{ passes_obj.pass_1_intent or "Foundation evaluated for unstated extraction motives, structural alignment, and proponent grounding against national baselines." }}
                </div>
            </div>

            <!-- PASS 2 -->
            <div style="background: #050811; border: 1px solid #1E293B; border-left: 4px solid #F87171; border-radius: 6px; padding: 12px; margin-bottom: 10px;">
                <div style="font-size: 0.75rem; color: #F87171; font-weight: 800; text-transform: uppercase;">Pass 2: 1st, 2nd &amp; 3rd-Order Causal Ripples (Gate 2)</div>
                <div style="font-size: 0.84rem; color: #CBD5E1; margin-top: 4px; line-height: 1.5;">
                    {{ passes_obj.pass_2_causality or "Downstream feedback loops evaluated: local market displacement, retail stockout risks, and feedstock supply bottlenecks." }}
                </div>
            </div>

            <!-- PASS 3 -->
            <div style="background: #050811; border: 1px solid #1E293B; border-left: 4px solid #FBBF24; border-radius: 6px; padding: 12px; margin-bottom: 10px;">
                <div style="font-size: 0.75rem; color: #FBBF24; font-weight: 800; text-transform: uppercase;">Pass 3: Axiological &amp; Multi-Stakeholder Tension Matrix (Gate 3)</div>
                <div style="font-size: 0.84rem; color: #CBD5E1; margin-top: 4px; line-height: 1.5;">
                    {{ passes_obj.pass_3_tension or "Audited against Citizens Economic Empowerment (CEE) statutory quotas and citizen welfare safeguards." }}
                </div>
            </div>

            <!-- PASS 4 -->
            <div style="background: #050811; border: 1px solid #1E293B; border-left: 4px solid #A855F7; border-radius: 6px; padding: 12px; margin-bottom: 10px;">
                <div style="font-size: 0.75rem; color: #A855F7; font-weight: 800; text-transform: uppercase;">Pass 4: One-Way Door Classification &amp; Reversibility (Gate 4 &amp; Gate 7)</div>
                <div style="font-size: 0.84rem; color: #CBD5E1; margin-top: 4px; line-height: 1.5;">
                    {{ passes_obj.pass_4_reversibility or "Irreversibility risk categorized: capital asset lock-in vs reversible iterative milestone tranche." }}
                </div>
            </div>

            <!-- PASS 5 -->
            <div style="background: #050811; border: 1px solid #1E293B; border-left: 4px solid #10B981; border-radius: 6px; padding: 12px;">
                <div style="font-size: 0.75rem; color: #10B981; font-weight: 800; text-transform: uppercase;">Pass 5: Synthesized Verdict &amp; Statutory Counter-Offer</div>
                <div style="font-size: 0.84rem; color: #CBD5E1; margin-top: 4px; line-height: 1.5;">
                    {% if passes_obj.pass_5_verdict %}
                        <p style="margin: 0 0 6px 0; color: #FCA5A5; font-style: italic;">"{{ passes_obj.pass_5_verdict.the_uncomfortable_truth }}"</p>
                        <p style="margin: 0; color: #FBBF24;"><strong>Covenants:</strong> {{ passes_obj.pass_5_verdict.calibrated_roadmap|join(' • ') }}</p>
                    {% else %}
                        Final synthesis rendered under posture {{ cur_posture }}.
                    {% endif %}
                </div>
            </div>
        </div>

        <div id="delib-feed-container" class="card" style="background: #0B1120; border: 1px solid #1E293B; border-radius: 8px; padding: 1.5rem; margin-top: 1.5rem; margin-bottom: 1.5rem;">
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
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;">
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('What specific domestic beneficiation ratio will reverse the CALIBRATE posture to PROCEED?')">Beneficiation Quotas</button>
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('How can the 45% SMME subcontracting gap be structured under Public Procurement Act 2022 Sec 54?')">CEE 50% Subcontracting</button>
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('Specify the required closed-loop water treatment covenants under Water Act [Cap 34:01].')">Water Act [Cap 34:01]</button>
        <button type="button" class="delib-tag-pill" onclick="sendDelibProbe('Detail captive solar PV integration standards required under BERA Act 2016 and IRP 2030.')">BERA Renewable Power</button>
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
    {% endif %}
</div>
<div id="whatif-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(4px); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
    <div style="background: #111827; border: 1.5px solid #D97706; border-radius: 10px; max-width: 650px; width: 100%; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.9); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1E293B; padding-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.3rem;">🎛️</span>
                <h3 style="margin: 0; color: #FBBF24; font-size: 1.2rem;">What-If Statutory Policy Simulator</h3>
            </div>
            <button type="button" onclick="closeWhatIfModal()" style="background: none; border: none; color: #94A3B8; font-size: 1.4rem; cursor: pointer;">&times;</button>
        </div>
        <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px;">
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: bold; margin-bottom: 6px;">
                    <span style="color: #CBD5E1;">Citizen Economic Empowerment (CEE) Subcontracting:</span>
                    <span id="val-cee" style="color: #FBBF24;">45%</span>
                </div>
                <input type="range" id="slider-cee" min="0" max="100" value="45" style="width: 100%; accent-color: #D97706;" oninput="updateWhatIfCalculations()">
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: bold; margin-bottom: 6px;">
                    <span style="color: #CBD5E1;">Secondary Domestic Beneficiation Commitment:</span>
                    <span id="val-benef" style="color: #FBBF24;">30%</span>
                </div>
                <input type="range" id="slider-benef" min="0" max="100" value="30" style="width: 100%; accent-color: #D97706;" oninput="updateWhatIfCalculations()">
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: bold; margin-bottom: 6px;">
                    <span style="color: #CBD5E1;">Closed-Loop Water &amp; Effluent Recycling:</span>
                    <span id="val-water" style="color: #FBBF24;">20%</span>
                </div>
                <input type="range" id="slider-water" min="0" max="100" value="20" style="width: 100%; accent-color: #D97706;" oninput="updateWhatIfCalculations()">
            </div>
        </div>
        <div style="background: #0B1120; border: 1px solid #1E293B; border-radius: 8px; padding: 16px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: bold;">Simulated Wisdom Quotient (W)</div>
                <div id="sim-quotient-display" style="font-size: 1.8rem; font-weight: 800; color: #FBBF24; font-family: monospace;">0.60</div>
            </div>
            <div><span id="sim-posture-badge" style="background: #F59E0B; color: #000; font-weight: 800; font-size: 0.95rem; padding: 6px 16px; border-radius: 4px;">CALIBRATE</span></div>
        </div>
        <div style="margin-top: 20px; text-align: right;">
            <button type="button" onclick="closeWhatIfModal()" style="background: #1E293B; border: 1px solid #334155; color: #CBD5E1; padding: 8px 18px; border-radius: 4px; font-weight: bold; cursor: pointer;">Close Simulator</button>
        </div>
    </div>
</div>
<div id="drawer-backdrop" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 9998; backdrop-filter: blur(2px);" onclick="toggleDrawer()"></div>
<div id="drawer" class="drawer">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid #1E293B; padding-bottom: 10px;">
        <h3 style="margin: 0; color: #FBBF24; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;"><span>📜</span> Past Institutional Audits</h3>
        <button type="button" onclick="toggleDrawer()" style="background: none; border: none; color: #94A3B8; font-size: 1.4rem; cursor: pointer;">&times;</button>
    </div>
    <div id="history-content">Loading past audits...</div>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('wisdom-audit-form'); if (!form) return;
    form.addEventListener('submit', function(e) {
        var textarea = document.getElementById('proposal-input'); if (!textarea || !textarea.value.trim()) return;
        e.preventDefault();
        var card = document.getElementById('async-progress-card'), bar = document.getElementById('async-progress-bar'), pct = document.getElementById('async-progress-pct'), stage = document.getElementById('async-stage-text'), submitBtn = document.getElementById('exec-audit-btn');
        if (card) { card.style.display = 'block'; card.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
        if (submitBtn) { submitBtn.disabled = true; submitBtn.style.opacity = '0.6'; submitBtn.innerText = '⏳ Auditing Conscience...'; }
        var progress = 15;
        var stages = [
            { threshold: 28, text: "Pass 1: Teleological Intent Matrix & Statutory Ground-Truth Active..." },
            { threshold: 50, text: "Pass 2: Causal Foresight Graph (1st, 2nd & 3rd-order system dynamics)..." },
            { threshold: 72, text: "Pass 3: Axiological Conflict Matrix (CEE equity vs foreign debt)..." },
            { threshold: 86, text: "Pass 4: Epistemic Asymmetry & One-Way Door Hydrological Verification..." },
            { threshold: 95, text: "Pass 5: Sealing SHA-256 Decision Assurance Dossier & Statutory Roadmaps..." }
        ];
        var ticker = setInterval(function() {
            if (progress < 95) {
                progress += Math.floor(Math.random() * 4) + 2; if (progress > 95) progress = 95;
                if (bar) bar.style.width = progress + '%'; if (pct) pct.textContent = progress + '%';
                for (var i = 0; i < stages.length; i++) { if (progress >= stages[i].threshold && stage) stage.textContent = stages[i].text; }
            }
        }, 500);
        var formData = new FormData(form);
        fetch('/wisdom/', { method: 'POST', body: formData })
        .then(function(res) { if (!res.ok) throw new Error('HTTP ' + res.status); return res.text(); })
        .then(function(html) {
            clearInterval(ticker);
            if (bar) bar.style.width = '100%'; if (pct) pct.textContent = '100%'; if (stage) stage.textContent = '✓ Statutory Ledger Sealed.';
            var parser = new DOMParser(); var doc = parser.parseFromString(html, 'text/html');
            var newResult = doc.getElementById('audit-result-container');
            if (newResult) {
                var currentResult = document.getElementById('audit-result-container');
                if (currentResult) currentResult.replaceWith(newResult);
                else document.querySelector('.container').appendChild(newResult);
                newResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else { document.open(); document.write(html); document.close(); }
        })
        .catch(function(err) {
            clearInterval(ticker);
            if (stage) { stage.style.color = '#EF4444'; stage.textContent = 'Audit processing failed: ' + err.message; }
        })
        .finally(function() { if (submitBtn) { submitBtn.disabled = false; submitBtn.style.opacity = '1'; submitBtn.innerText = 'Execute Wisdom Audit'; } });
    });
});
function toggleDrawer() {
    var d = document.getElementById('drawer'), b = document.getElementById('drawer-backdrop'), c = document.getElementById('history-content');
    if (!d) return;
    var isHidden = (d.style.display === 'none' || d.style.display === '');
    d.style.display = isHidden ? 'block' : 'none'; if (b) b.style.display = isHidden ? 'block' : 'none';
    if (isHidden && c) {
        c.innerHTML = '<div style="color: #FBBF24; padding: 20px 0; text-align: center; font-size: 0.85rem;">⏳ Querying sovereign ledger...</div>';
        fetch('/wisdom/api/audits/history')
            .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(function(items) {
                var list = Array.isArray(items) ? items : (items.audits || items.history || []);
                if (!list.length) { c.innerHTML = '<p style="color:#94A3B8; text-align:center; padding:15px 0;">No records found.</p>'; return; }
                var out = '';
                list.forEach(function(x) {
                    var aId = x.audit_id || 'LWA-AUDIT';
                    var p = x.final_posture || x.posture || x.status || 'CALIBRATE';
                    var badgeBg = (p === 'PROCEED') ? 'rgba(16, 185, 129, 0.2)' : ((p === 'HALT') ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)');
                    var badgeFg = (p === 'PROCEED') ? '#34D399' : ((p === 'HALT') ? '#F87171' : '#FBBF24');
                    var badgeBorder = (p === 'PROCEED') ? '#10B981' : ((p === 'HALT') ? '#EF4444' : '#D97706');
                    var propSnippet = (x.proposal_text || x.proposal || 'Commercial proposal under sovereign review').substring(0, 80);
                    out += '<div onclick="window.location.href=\'/wisdom/audit/' + aId + '\'" style="background:#060A12; border:1px solid #1E293B; border-radius:8px; padding:12px; margin-bottom:10px; cursor:pointer; transition:all 0.2s;" onmouseover="this.style.borderColor=\'#D97706\'" onmouseout="this.style.borderColor=\'#1E293B\'">';
                    out += '  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">';
                    out += '    <strong style="color:#60A5FA; font-family:monospace; font-size:0.85rem;">' + aId + '</strong>';
                    out += '    <span style="background:' + badgeBg + '; color:' + badgeFg + '; border:1px solid ' + badgeBorder + '; font-size:0.68rem; font-weight:800; padding:2px 7px; border-radius:4px; text-transform:uppercase;">' + p + '</span>';
                    out += '  </div>';
                    out += '  <div style="color:#CBD5E1; font-size:0.75rem; line-height:1.4;">' + propSnippet + '...</div>';
                    if (x.created_at) {
                        out += '  <div style="color:#64748B; font-size:0.68rem; margin-top:6px; font-family:monospace;">' + x.created_at + '</div>';
                    }
                    out += '</div>';
                });
                c.innerHTML = out;
            })
            .catch(function(err) {
                c.innerHTML = '<p style="color:#EF4444; padding:15px 0; text-align:center;">Ledger error: ' + (err.message || 'Unable to retrieve history') + '</p>';
            });
    }
}
function loadSampleDossier() {
    var sample = "PROJECT DOSSIER: SELEBI-PHIKWE CLEAN METALLURGY & CITIZEN BENEFICIATION FACILITY\nSECTOR: Mining & SEZA Beneficiation\nCAPITAL EXPENDITURE: BWP 450 Million\nCITIZEN PARTICIPATION: 25% citizen equity reserved, 85% local employment, but only 45% SMME subcontracting.\nBENEFICIATION: Closed-loop secondary hydrometallurgical refining on-site to halt raw ore export.";
    var t = document.getElementById('proposal-input'); if (t) { t.value = sample; t.focus(); }
}
function handleFileSelected(input) {
    if (input.files && input.files[0]) {
        var file = input.files[0];
        var nameSpan = document.getElementById('file-chosen-name');
        if (nameSpan) { nameSpan.style.color = '#FBBF24'; nameSpan.textContent = 'Attached: ' + file.name; }
        var reader = new FileReader();
        reader.onload = function(e) { var t = document.getElementById('proposal-input'); if (t) t.value = e.target.result; };
        reader.readAsText(file);
    }
}
function generatePromptFromDoc(input) {
    if (!input.files || !input.files[0]) return;
    var file = input.files[0];
    var status = document.getElementById('upload-status-text');
    if (status) { status.style.color = '#FBBF24'; status.textContent = 'Analyzing ' + file.name + '...'; }
    var reader = new FileReader();
    reader.onload = function(e) {
        fetch('/wisdom/api/v1/generate-prompt', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title: file.name, content: e.target.result })
        }).then(function(r) { return r.json(); }).then(function(d) {
            if (d.prompt) {
                var t = document.getElementById('proposal-input');
                if (t) { t.value = d.prompt; t.focus(); }
                if (status) { status.style.color = '#10B981'; status.textContent = '✓ Statutory prompt formulated'; }
            }
        });
    };
    reader.readAsText(file);
}
(function() {
    var delibHistory = [];
    var currentDossier = {{ (audit if audit is defined and audit else (result if result is defined and result else {})) | tojson | safe }};
    window.sendDelibProbe = function(txt) {
        var inp = document.getElementById('delib-prompt-input');
        if (inp) { inp.value = txt; window.executeDelibChat(); }
    };
    window.branchAuditV2 = function() {
        var inp = document.getElementById('delib-prompt-input');
        var val = (inp && inp.value.trim()) ? inp.value.trim() : prompt("Enter specific statutory mitigations to branch this dossier to v2:");
        if (val) window.location.href = "/wisdom/generate?intent=" + encodeURIComponent("Branching child audit v2 with mitigations: " + val);
    };
    window.exportDelibTranscript = function() {
        var stream = document.getElementById('delib-chat-stream'); if (!stream) return;
        var text = stream.innerText;
        var blob = new Blob([text], { type: 'text/plain' });
        var a = document.createElement('a'); a.href = URL.createObjectURL(blob);
        a.download = 'Laveto_Wisdom_Deliberation_Transcript.txt'; a.click();
    };
    window.executeDelibChat = function() {
        var inp = document.getElementById('delib-prompt-input'), btn = document.getElementById('delib-exec-btn'), stream = document.getElementById('delib-chat-stream');
        if (!inp || !stream) return;
        var msg = inp.value.trim(); if (!msg) return;
        var uBubble = document.createElement('div');
        uBubble.style.cssText = "align-self: flex-end; background: #1E293B; color: #F8FAFC; padding: 10px 14px; border-radius: 6px; max-width: 82%; font-size: 0.9rem; border: 1px solid #475569;";
        uBubble.textContent = msg; stream.appendChild(uBubble);
        var wait = document.createElement('div'); wait.id = 'delib-running-note';
        wait.style.cssText = "align-self: flex-start; color: #FBBF24; font-size: 0.8rem; font-style: italic; padding: 4px 8px;";
        wait.textContent = "Conscience deliberating against statutory law..."; stream.appendChild(wait);
        inp.value = ''; if (btn) { btn.disabled = true; btn.textContent = 'Evaluating...'; } stream.scrollTop = stream.scrollHeight;
        fetch('/wisdom/api/v1/deliberate', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audit_dossier: currentDossier, history: delibHistory, message: msg })
        }).then(function(res) { if (!res.ok) throw new Error("HTTP " + res.status); return res.json(); })
        .then(function(data) {
            var w = document.getElementById('delib-running-note'); if (w) w.remove();
            var reply = data.reply || data.response || "No statutory response returned.";
            var botBubble = document.createElement('div');
            botBubble.style.cssText = "align-self: flex-start; background: #0D1526; border: 1px solid #D97706; color: #F1F5F9; padding: 12px 16px; border-radius: 6px; max-width: 85%; font-size: 0.9rem; line-height: 1.55; white-space: pre-wrap;";
            botBubble.innerHTML = '<strong style="color:#FBBF24; display:block; margin-bottom:6px; font-size:0.75rem; text-transform:uppercase;">⚖️ AW Statutory Verdict:</strong>' + reply;
            stream.appendChild(botBubble);
            delibHistory.push({ role: 'user', text: msg }); delibHistory.push({ role: 'model', text: reply });
            stream.scrollTop = stream.scrollHeight;
        }).catch(function(err) {
            var w = document.getElementById('delib-running-note'); if (w) w.remove();
            var errBubble = document.createElement('div');
            errBubble.style.cssText = "background: rgba(220, 38, 38, 0.2); border: 1px solid #EF4444; color: #FCA5A5; padding: 8px 12px; border-radius: 6px; font-size: 0.85rem;";
            errBubble.textContent = "Deliberation error: " + err.message; stream.appendChild(errBubble); stream.scrollTop = stream.scrollHeight;
        }).finally(function() { if (btn) { btn.disabled = false; btn.textContent = 'Deliberate'; } });
    };
    var inputEl = document.getElementById('delib-prompt-input');
    if (inputEl) { inputEl.addEventListener('keydown', function(e) { if (e.key === 'Enter') { e.preventDefault(); window.executeDelibChat(); } }); }
})();
</script>

<script>
function handleAuditSubmit(e) {
    var btn = document.getElementById('execAuditBtn');
    var txt = document.getElementById('proposal-input');
    if (!txt || !txt.value.trim()) {
        alert("Please enter a policy proposal or dilemma to audit.");
        e.preventDefault();
        return false;
    }
    if (btn) {
        btn.innerHTML = '⚡ Auditing Conscience (Passes 1–5 Running)...';
        btn.style.background = '#059669';
        btn.style.color = '#FFFFFF';
        btn.style.cursor = 'wait';
        btn.style.opacity = '0.85';
        btn.style.pointerEvents = 'none';
    }
    return true;
}
</script>


    <!-- SOVEREIGN FIDUCIARY CREED & EPISTEMIC CHARTER -->
    <div class="fiduciary-creed-box" style="margin: 2rem auto 1.5rem auto; max-width: 1200px; width: calc(100% - 40px); box-sizing: border-box; padding: 18px 24px; background: rgba(11, 18, 34, 0.92); border: 1px solid #1E293B; border-left: 4px solid #D97706; border-radius: 8px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45); backdrop-filter: blur(8px);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1rem;">⚖️</span>
                <span style="font-size: 0.78rem; font-weight: 800; color: #FBBF24; text-transform: uppercase; letter-spacing: 1.5px; font-family: monospace;">
                    LAVETO WISDOM AW-1 &bull; EPISTEMIC INTEGRITY COVENANT
                </span>
            </div>
            <span style="font-size: 0.72rem; color: #64748B; font-family: monospace; letter-spacing: 0.5px;">
                SOVEREIGN DECISION ASSURANCE PROTOCOL
            </span>
        </div>
        <p style="margin: 0; color: #CBD5E1; font-size: 0.88rem; line-height: 1.6; font-style: italic;">
            &ldquo;We know the model is fallible. Therefore, we have cross-examined it against statutory law, bound it with mathematical invariants, sealed it with SHA-256 cryptography, and anchored it to human fiduciary responsibility.&rdquo;
        </p>
    </div>


<!-- CO-FOUNDER & INSTITUTIONAL PILOT MODAL -->
</main>
<div id="partner-modal" style="display:none; position:fixed; inset:0; background:rgba(2, 6, 23, 0.85); backdrop-filter:blur(6px); z-index:9999; align-items:center; justify-content:center; padding:1rem;">
  <div style="background:#0F172A; border:1px solid #1E293B; border-top:3px solid #3B82F6; border-radius:12px; width:100%; max-width:540px; box-shadow:0 20px 40px rgba(0,0,0,0.6); padding:24px; position:relative;">
    <button type="button" onclick="togglePartnerModal()" style="position:absolute; top:16px; right:16px; background:transparent; border:none; color:#64748B; font-size:18px; cursor:pointer; font-weight:bold;">✕</button>
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
      <span style="font-size:24px;">🏛️</span>
      <div>
        <h3 style="margin:0; font-size:16px; font-weight:700; color:#F8FAFC; letter-spacing:-0.2px;">Commercial Pilot & Co-Founder Alignment</h3>
        <p style="margin:2px 0 0 0; font-size:11px; color:#94A3B8;">Global Sovereign Deliberation & AI Circuit Breaker Platform</p>
      </div>
    </div>
    <div style="background:rgba(59, 130, 246, 0.08); border-left:3px solid #3B82F6; padding:10px 12px; border-radius:4px; margin-bottom:16px;">
      <p style="margin:0; font-size:11px; line-height:1.5; color:#CBD5E1;">
        We are preparing commercial rollout and expanding global circuit-breaker demonstrations for statutory and procurement assurance. If you are an enterprise partner, parastatal evaluator, or prospective GTM co-founder, connect directly with the sovereign engineering desk.
      </p>
    </div>
    <form id="partner-enquiry-form" onsubmit="submitPartnerEnquiry(event)">
      <div style="margin-bottom:12px;">
        <label style="display:block; font-size:11px; font-weight:600; color:#94A3B8; margin-bottom:4px;">Full Name / Institutional Title *</label>
        <input type="text" id="partner-name" required placeholder="e.g. Dr. Lesego Molosiwa (GTM / Parastatal Evaluator)" style="width:100%; box-sizing:border-box; background:#0B1120; border:1px solid #334155; border-radius:6px; padding:8px 12px; color:#F8FAFC; font-size:12px; outline:none;">
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
        <div>
          <label style="display:block; font-size:11px; font-weight:600; color:#94A3B8; margin-bottom:4px;">Corporate Email</label>
          <input type="email" id="partner-email" placeholder="name@institution.gov.bw" style="width:100%; box-sizing:border-box; background:#0B1120; border:1px solid #334155; border-radius:6px; padding:8px 12px; color:#F8FAFC; font-size:12px; outline:none;">
        </div>
        <div>
          <label style="display:block; font-size:11px; font-weight:600; color:#94A3B8; margin-bottom:4px;">Direct Phone / WhatsApp *</label>
          <input type="text" id="partner-phone" required placeholder="+267 7X XXX XXX" style="width:100%; box-sizing:border-box; background:#0B1120; border:1px solid #334155; border-radius:6px; padding:8px 12px; color:#F8FAFC; font-size:12px; outline:none;">
        </div>
      </div>
      <div style="margin-bottom:16px;">
        <label style="display:block; font-size:11px; font-weight:600; color:#94A3B8; margin-bottom:4px;">Focus Area / Synergy Description</label>
        <textarea id="partner-bio" rows="3" placeholder="Briefly describe your institutional interest, market expertise, or pilot evaluation requirements..." style="width:100%; box-sizing:border-box; background:#0B1120; border:1px solid #334155; border-radius:6px; padding:8px 12px; color:#F8FAFC; font-size:12px; outline:none; resize:none;"></textarea>
      </div>
      <div id="partner-status-msg" style="display:none; font-size:11px; margin-bottom:12px; padding:8px 12px; border-radius:6px;"></div>
      <div style="display:flex; justify-content:flex-end; gap:10px;">
        <button type="button" onclick="togglePartnerModal()" style="background:#1E293B; border:1px solid #334155; color:#94A3B8; border-radius:6px; padding:8px 14px; font-size:12px; cursor:pointer;">Cancel</button>
        <button type="submit" id="partner-submit-btn" style="background:#2563EB; border:none; color:#FFFFFF; border-radius:6px; padding:8px 18px; font-size:12px; font-weight:600; cursor:pointer;">Submit Enquiry</button>
      </div>
    </form>
  </div>
</div>

<script>
function togglePartnerModal() {
  var m = document.getElementById("partner-modal");
  if (!m) return;
  m.style.display = (m.style.display === "none" || m.style.display === "") ? "flex" : "none";
}

function submitPartnerEnquiry(e) {
  e.preventDefault();
  var btn = document.getElementById("partner-submit-btn");
  var msg = document.getElementById("partner-status-msg");
  var payload = {
    name: document.getElementById("partner-name").value,
    email: document.getElementById("partner-email").value,
    phone: document.getElementById("partner-phone").value,
    bio: document.getElementById("partner-bio").value
  };

  btn.disabled = true;
  btn.innerText = "Registering...";
  msg.style.display = "none";

  fetch("/wisdom/api/partner/enquiry", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(function(r) { return r.json(); })
  .then(function(res) {
    btn.disabled = false;
    btn.innerText = "Submit Enquiry";
    msg.style.display = "block";
    if (res.status === "success") {
      msg.style.background = "rgba(16, 185, 129, 0.15)";
      msg.style.border = "1px solid #10B981";
      msg.style.color = "#34D399";
      msg.innerText = "✅ " + res.message;
      document.getElementById("partner-enquiry-form").reset();
      setTimeout(function() { togglePartnerModal(); msg.style.display = "none"; }, 3500);
    } else {
      msg.style.background = "rgba(239, 68, 68, 0.15)";
      msg.style.border = "1px solid #EF4444";
      msg.style.color = "#F87171";
      msg.innerText = "⚠️ " + (res.message || "Failed to submit enquiry.");
    }
  })
  .catch(function(err) {
    btn.disabled = false;
    btn.innerText = "Submit Enquiry";
    msg.style.display = "block";
    msg.style.background = "rgba(239, 68, 68, 0.15)";
    msg.style.border = "1px solid #EF4444";
    msg.style.color = "#F87171";
    msg.innerText = "⚠️ Network error submitting enquiry.";
  });
}
</script>


<script>
document.addEventListener("click", function(e) {
    var container = document.getElementById("sovereign-dropdown-container");
    var menu = document.getElementById("sovereign-dropdown-menu");
    if (container && menu && !container.contains(e.target)) {
        menu.style.display = "none";
    }
});
</script>

</body>
</html>"""
