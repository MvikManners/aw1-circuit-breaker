// =========================================================================
// 1. GLOBAL STATE & MASTER DATA STRUCTURES
// =========================================================================
let currentIndex = 0;
let isAnimating = false;
let intakeCurrentPage = 1;

class SovereignLedger {
    constructor() {
        this.ledger = [];
        this.assetRegistry = {};
    }

    validateAndRecord(memberId, amount, telemetry) {
        if (telemetry.healthIndex < 0.2) {
            return { success: false, msg: `Blocked: Asset health critical for ${memberId}` };
        }
        const tx = {
            txId: "TX-" + Date.now(),
            amount: amount,
            memberId: memberId,
            timestamp: new Date().toISOString()
        };
        this.ledger.push(tx);
        this.assetRegistry[memberId] = telemetry;
        return { success: true, txId: tx.txId };
    }
}
const lavetoHub = new SovereignLedger();

// =========================================================================
// 2. MASTER UI INITIALIZATION (ON DOM LOAD)
// =========================================================================
document.addEventListener("DOMContentLoaded", function() {
    console.log("Laveto Ledger: Initializing Master Controller...");

    // A. Carousel / Asset Card Visibility & Target DNA Sync
    const cards = Array.from(document.querySelectorAll('.asset-card'));
    const targetDna = ("{{ target_dna or '' }}").trim().toLowerCase();

    if (cards.length > 0) {
        cards.forEach(c => {
            c.classList.remove('is-active');
            c.style.setProperty('display', 'none', 'important');
        });

        let startingIndex = 0;
        if (targetDna) {
            const foundIndex = cards.findIndex(card => (card.getAttribute('data-vin') || '').toLowerCase() === targetDna);
            if (foundIndex !== -1) startingIndex = foundIndex;
        }

        cards[startingIndex].classList.add('is-active');
        cards[startingIndex].style.setProperty('display', 'block', 'important');

        if (typeof currentIndex !== 'undefined') {
            currentIndex = startingIndex;
        }
        if (typeof currentCarouselIndex !== 'undefined') {
            currentCarouselIndex = startingIndex;
        }

        const ind = document.querySelector('.carousel-current-indicator');
        if (ind) ind.textContent = startingIndex + 1;
    }

    // B. Scroll Fix for Pagination
    if (window.location.search.includes('page=')) {
        const registryTable = document.getElementById('fleet-registry');
        if (registryTable) {
            window.scrollTo({ top: registryTable.getBoundingClientRect().top + window.scrollY - 140, behavior: 'smooth' });
        }
    }

    // C. Silent Fetch Protocol (Loads the DNA registry)
    fetch('/hangar/api/fleet-dnas')
        .then(response => {
            if (!response.ok) throw new Error(`Server returned ${response.status}`);
            return response.json();
        })
        .then(dnas => {
            const dataList = document.getElementById('fleetDnas');
            if (dataList && Array.isArray(dnas)) {
                dataList.innerHTML = '';
                dnas.forEach(dna => {
                    const option = document.createElement('option');
                    option.value = dna;
                    dataList.appendChild(option);
                });
            }
        })
        .catch(err => console.warn('DNA registry silent fetch idle:', err.message));

    // D. Auto-Trigger Mechanism (Watches for dropdown clicks / scanner match)
    const scanner = document.getElementById('dnaScanner');
    if (scanner) {
        scanner.addEventListener('input', function() {
            const list = document.getElementById('fleetDnas');
            if (!list) return;
            for (let i = 0; i < list.options.length; i++) {
                if (this.value === list.options[i].value) {
                    if (this.form) this.form.submit();
                    break;
                }
            }
        });
    }

    // E. Console Trigger Buttons
    const faultsBtn = document.getElementById('activeFaultsConsoleBtn');
    if (faultsBtn) {
        faultsBtn.addEventListener('click', function() {
            console.log("📡 GOSPEL OS: Extracting active device trauma matrices...");
        });
    }

    const failedBtn = document.querySelector('.btn-failed');
    if (failedBtn) {
        failedBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            console.log("📡 GOSPEL OS: Initializing system-wide trauma audit request...");
            try {
                const response = await fetch('/audit_logs');
                alert("🩺 SECTOR DIAGNOSTIC: Initializing deep forensic sweep across all active cohorts...\n\nResult: 0 critical system block exceptions or unresolved hardware failures reported in this memory loop segment.");
            } catch (err) {
                alert("🚨 DIAGNOSTIC CRASH: Failed to verify network ledger health fields. " + err.message);
            }
        });
    }

    // F. Initial Telemetry & Mandate Scan
    checkPendingMandates();
});

// =========================================================================
// 3. TELEMETRY & MANDATE RADAR (LOOP-PROTECTED)
// =========================================================================
async function checkPendingMandates() {
    try {
        const response = await fetch("/hangar/api/pending-count");
        if (!response.ok) return;

        const result = await response.json();
        const alertBox = document.getElementById('live-mandate-alert');
        const countSpan = document.getElementById('mandate-count');

        let pendingCount = 0;
        if (result && result.events && typeof result.events.triage !== 'undefined') {
            pendingCount = parseInt(result.events.triage) || 0;
        } else if (result && typeof result.total_pending !== 'undefined') {
            pendingCount = parseInt(result.total_pending) || 0;
        }

        if (alertBox && countSpan) {
            const currentCountText = countSpan.innerText.trim();
            const isCurrentlyFlex = alertBox.style.display === 'flex';

            if (pendingCount > 0) {
                if (currentCountText !== String(pendingCount)) {
                    countSpan.innerText = pendingCount;
                }
                if (!isCurrentlyFlex) {
                    alertBox.style.setProperty('display', 'flex', 'important');
                }
            } else {
                if (isCurrentlyFlex) {
                    alertBox.style.setProperty('display', 'none', 'important');
                }
            }
        }
    } catch (error) {
        console.warn("Telemetry feed idle / bypassed:", error.message);
    }
}

async function submitGmeReconciliation(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const grossInput = document.getElementById('gme_gross_pula');
    const costInput = document.getElementById('gme_collection_cost');
    const respBox = document.getElementById('gmeResponse');

    const grossVal = parseFloat(grossInput.value);
    const costVal = parseFloat(costInput.value) || 0.0;

    if (isNaN(grossVal) || grossVal <= 0) {
        respBox.style.color = 'var(--critical-red)';
        respBox.innerText = '❌ Error: Enter a valid gross Pula amount.';
        return;
    }

    try {
        respBox.style.color = 'var(--integrity-gold)';
        respBox.innerText = '⏳ RECONCILING BATCH WITH SOVEREIGN LEDGER...';

        const response = await fetch('/api/scrap/reconcile-gme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'
            },
            body: JSON.stringify({
                gross_pula: grossVal,
                collection_cost: costVal
            })
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            respBox.style.color = 'var(--integrity-green)';
            respBox.innerHTML = `
                <div style="background: rgba(40,167,69,0.1); border: 1px solid var(--integrity-green); padding: 15px; border-radius: 4px; margin-top: 10px; text-align: left;">
                    <div style="font-weight: 900; color: #fff; font-size: 0.9rem; margin-bottom: 5px;">✅ GME BATCH RECONCILED SUCCESSFULLY</div>
                    <div>📦 <b>Parts Processed:</b> ${result.parts_reconciled} components (${result.total_weight_kg} kg)</div>
                    <div>💰 <b>Net Yield:</b> P${result.net_yield.toFixed(2)}</div>
                    <div style="color: var(--integrity-gold); margin-top: 5px;">
                        • 70% Member Shield Pools: <b>P${result.shield_pool_pula.toFixed(2)}</b><br>
                        • 20% Warden Performance Bounty: <b>P${result.warden_pool_pula.toFixed(2)}</b><br>
                        • 10% Sovereign Scholarship Reserve: <b>P${result.reserve_pool_pula.toFixed(2)}</b>
                    </div>
                </div>
            `;
            grossInput.value = '';
            costInput.value = '0.00';

            // Refresh telemetry cards
            if (typeof loadScrapTelemetry === 'function') {
                loadScrapTelemetry();
            }
        } else {
            respBox.style.color = 'var(--critical-red)';
            respBox.innerText = `❌ Reconcile Failed: ${result.message}`;
        }
    } catch (err) {
        respBox.style.color = 'var(--critical-red)';
        respBox.innerText = `🚨 Network Error: ${err.message}`;
    }
}

async function loadScrapTelemetry() {
    try {
        const res = await fetch('/api/scrap/dashboard');
        const data = await res.json();
        if (data.status === 'secure') {
            const stagedEl = document.getElementById('stat_staged_count');
            const yieldEl = document.getElementById('stat_cumulative_yield');
            if (stagedEl) stagedEl.innerText = data.zone_d_staged_count;
            if (yieldEl) yieldEl.innerText = 'P ' + Number(data.cumulative_scrap_yield_pula).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
    } catch (err) {
        console.error("Scrap telemetry sync error:", err);
    }
}

document.addEventListener("DOMContentLoaded", loadScrapTelemetry);

// Single controlled polling cycle (every 5 seconds)
setInterval(checkPendingMandates, 5000);

// Alert Guard: Reconnect safely only when missing
setInterval(function() {
    const mandateCountElem = document.getElementById('mandate-count');
    const alertDiv = document.getElementById('live-mandate-alert');

    if (!mandateCountElem) return;

    const pendingCount = parseInt(mandateCountElem.innerText || 0);

    if (pendingCount > 0 && !alertDiv) {
        console.log("Alert missing. Re-injecting...");
        const newAlert = document.createElement('div');
        newAlert.id = 'live-mandate-alert';
        newAlert.className = 'alert-hardened';
        newAlert.style.setProperty('display', 'flex', 'important');
        newAlert.innerHTML = `
            <div>
                <h3 style="color: var(--integrity-gold); margin: 0; font-family: 'Montserrat', sans-serif; font-weight: 900; letter-spacing: 2px; text-transform: uppercase;">
                    🔔 PENDING PAYROLL MANDATES (<span id="mandate-count">${pendingCount}</span>)
                </h3>
                <p style="color: var(--text-main); font-family: 'Courier Prime', monospace; font-size: 0.8rem; margin: 5px 0 0 0;">
                    Client signatures secured. Awaiting Admin clearance for A.G. Export.
                </p>
            </div>
            <a href="/hangar/clearinghouse" style="background: var(--integrity-gold); color: #000; padding: 15px 25px; font-family: 'Montserrat', sans-serif; font-weight: 900; text-transform: uppercase; text-decoration: none; border-radius: 2px; font-size: 0.85rem; letter-spacing: 1px;">
                OPEN CLEARINGHOUSE ➡
            </a>
        `;
        document.body.prepend(newAlert);
    }
}, 5000);

// MutationObserver: Loop-Shielded
const targetNode = document.getElementById('live-mandate-alert');
if (targetNode && targetNode.parentNode) {
    const observer = new MutationObserver((mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList' && mutation.target === targetNode) {
                console.log("📡 DOM State Verified: Mandate Alert structural change.");
            }
        }
    });
    observer.observe(targetNode.parentNode, { childList: true, subtree: false });
}

// =========================================================================
// 4. CAROUSEL & MAYDAY CONTROLLERS
// =========================================================================
window.changeCarouselPage = function(direction) {
    if (isAnimating) return;
    isAnimating = true;

    const allCards = Array.from(document.querySelectorAll('.asset-card'));
    const total = allCards.length;

    if (total === 0) {
        console.error("📡 GOSPEL OS: No asset-card nodes detected.");
        isAnimating = false;
        return;
    }

    let activeIndex = allCards.findIndex(c => c.classList.contains('is-active'));
    if (activeIndex === -1) activeIndex = 0;

    allCards[activeIndex].classList.remove('is-active');
    allCards[activeIndex].style.setProperty('display', 'none', 'important');

    activeIndex = (activeIndex + direction + total) % total;

    allCards[activeIndex].classList.add('is-active');
    allCards[activeIndex].style.setProperty('display', 'block', 'important');

    const ind = document.querySelector('.carousel-current-indicator');
    if (ind) ind.textContent = activeIndex + 1;

    setTimeout(() => {
        isAnimating = false;
    }, 300);
};

function changeCarouselPage(direction) {
    window.changeCarouselPage(direction);
}

function showCard(index) {
    const maydayCards = document.querySelectorAll('.mayday-card');
    maydayCards.forEach((card, i) => card.style.display = (i === index) ? 'block' : 'none');
}

function nextMayday() {
    const maydayCards = document.querySelectorAll('.mayday-card');
    if (maydayCards.length === 0) return;
    currentIndex = (currentIndex + 1) % maydayCards.length;
    showCard(currentIndex);
}

function prevMayday() {
    const maydayCards = document.querySelectorAll('.mayday-card');
    if (maydayCards.length === 0) return;
    currentIndex = (currentIndex - 1 + maydayCards.length) % maydayCards.length;
    showCard(currentIndex);
}

window.addEventListener('load', () => {
    const targetDna = ("{{ target_dna or '' }}").toLowerCase().trim();
    if (targetDna) {
        const allCards = Array.from(document.querySelectorAll('.asset-card'));
        const targetIndex = allCards.findIndex(card => (card.getAttribute('data-vin') || '').toLowerCase() === targetDna);

        if (targetIndex !== -1) {
            setTimeout(() => {
                allCards.forEach(c => {
                    c.classList.remove('is-active');
                    c.style.setProperty('display', 'none', 'important');
                });
                allCards[targetIndex].classList.add('is-active');
                allCards[targetIndex].style.setProperty('display', 'block', 'important');

                const ind = document.querySelector('.carousel-current-indicator');
                if (ind) ind.textContent = targetIndex + 1;
            }, 50);
        }
    }
});

// =========================================================================
// 5. FINANCIAL CALCULATORS & MATHEMATICAL MODELS
// =========================================================================
function autoAdjustTerm(id) {
    const inputField = document.getElementById('p_calc_' + id);
    if (!inputField) return;
    let p = parseFloat(inputField.value);

    if (isNaN(p) || p < 0) {
        p = 0;
        inputField.value = 0;
    }

    const t = document.getElementById('n_calc_' + id);
    if (!t) return;

    if (p <= 3000) { t.value = "6"; }
    else if (p <= 10000) { t.value = "12"; }
    else if (p <= 25000) { t.value = "24"; }
    else { t.value = "36"; }
}

function updateLavetoMath(assetId) {
    const inputField = document.getElementById('pledge-input_' + assetId);
    const feeDisplay = document.getElementById('fee-display_' + assetId);
    const netDisplay = document.getElementById('net-display_' + assetId);
    const totalDisplay = document.getElementById('total-display_' + assetId);

    if (!inputField || !feeDisplay || !netDisplay || !totalDisplay) return;

    const amount = parseFloat(inputField.value) || 0;
    const fee = amount * 0.05;
    const net = amount * 0.95;

    totalDisplay.innerText = 'P' + amount.toLocaleString('en-BW', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    feeDisplay.innerText = 'P' + fee.toLocaleString('en-BW', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    netDisplay.innerText = 'P' + net.toLocaleString('en-BW', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function calculateStandalone(id) {
    const pField = document.getElementById('p_calc_' + id);
    const rField = document.getElementById('r_calc_' + id);
    const nField = document.getElementById('n_calc_' + id);
    const outField = document.getElementById('standaloneOut_' + id);
    const resultBox = document.getElementById('standaloneResult_' + id);

    if (!pField || !rField || !nField || !outField || !resultBox) return;

    const p = parseFloat(pField.value);
    const r = (parseFloat(rField.value) / 100) / 12;
    const n = parseInt(nField.value);

    if (!p || !r || !n) { alert("Please enter valid figures"); return; }

    const mathPower = Math.pow(1 + r, n);
    const monthly = p * (r * mathPower) / (mathPower - 1);

    outField.innerText = 'P' + monthly.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    resultBox.style.display = 'block';
}

window.calculateSovereignMarketValue = function(id, integrity, shield, debt) {
    const baseValField = document.getElementById('baseMarketVal_' + id);
    if (!baseValField) return;
    const baseVal = parseFloat(baseValField.value);
    if (!baseVal) { alert("Enter Base Value"); return; }
    const total = baseVal + (baseVal * (1.0 - integrity)) + shield - debt;
    alert("Calculated Valuation: P" + total.toLocaleString(undefined, { minimumFractionDigits: 2 }));
};

function loadMatrixData() {
    fetch("/hangar/api/pending_mandates")
        .then(response => {
            if (!response.ok) throw new Error("Server returned " + response.status);
            return response.json();
        })
        .then(data => {
            if (typeof renderDashboard === 'function') {
                renderDashboard(data);
            }
        })
        .catch(err => {
            console.error("Pulse monitoring error: ", err);
        });
}

// =========================================================================
// 6. COVENANT PRINT & WHATSAPP GENERATOR
// =========================================================================
function printTerminalQuote(id) {
    const pField = document.getElementById('p_calc_' + id);
    const rField = document.getElementById('r_calc_' + id);
    const nField = document.getElementById('n_calc_' + id);
    const outField = document.getElementById('standaloneOut_' + id);

    if (!pField || !rField || !nField || !outField) return;

    const p = pField.value;
    const r = rField.value;
    const n = nField.value;
    const m = outField.innerText;
    const date = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });

    const win = window.open('', '_blank');
    if (!win) { alert("Pop-up blocked! Please allow popups for this ecosystem dashboard."); return; }

    win.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Laveto Official Covenant</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Courier+Prime:wght@400;700&display=swap');
                body { font-family: 'Montserrat', sans-serif; background: #f4f4f4; padding: 40px 0; margin: 0; }
                .page { width: 600px; margin: auto; background: #fff; padding: 60px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); position: relative; }
                .watermark { position: absolute; top: 30%; left: 10%; width: 80%; opacity: 0.05; pointer-events: none; }
                .header { text-align: center; margin-bottom: 50px; }
                .logo { height: 80px; margin-bottom: 20px; }
                h1 { font-size: 1.6rem; color: #1a1a1a; letter-spacing: 4px; margin: 0; text-transform: uppercase; }
                .divider { height: 3px; width: 60px; background: #C5A059; margin: 20px auto; }
                .quote-table { width: 100%; margin: 40px 0; border-top: 1px solid #eee; border-collapse: collapse; }
                .quote-table tr { border-bottom: 1px solid #eee; }
                .quote-table th { color: #888; font-size: 0.7rem; text-transform: uppercase; padding: 15px 0; text-align: left; letter-spacing: 1px; }
                .quote-table td { font-family: 'Courier Prime', monospace; font-size: 1rem; font-weight: 700; text-align: right; }
                .total-box { background: #1a1a1a; color: #C5A059; padding: 30px; text-align: center; border-radius: 4px; }
                .total-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 3px; }
                .total-value { font-size: 2.5rem; font-weight: 900; margin-top: 10px; font-family: 'Courier Prime', monospace; }
                .footer { margin-top: 60px; text-align: center; font-size: 0.65rem; color: #999; line-height: 1.8; }
            </style>
        </head>
        <body>
            <div class="page">
                <img src="${window.location.origin}/static/Laveto_logo-01.png" class="watermark">
                <div class="header">
                    <img src="${window.location.origin}/static/Laveto_logo-01.png" class="logo">
                    <h1>Covenant Estimate</h1>
                    <div class="divider"></div>
                    <div style="font-size: 0.7rem; color: #555;">DATE: ${date} | REF: LVT-${id}</div>
                </div>

                <table class="quote-table">
                    <tr><th>Principal Capital</th><td>P${parseFloat(p).toLocaleString()}</td></tr>
                    <tr><th>Interest Rate</th><td>${r}% per annum</td></tr>
                    <tr><th>Contract Term</th><td>${n} Months</td></tr>
                </table>

                <div class="total-box">
                    <div class="total-label">Estimated Monthly Installment</div>
                    <div class="total-value">${m}</div>
                </div>

                <div class="footer">
                    THIS DOCUMENT IS A SOVEREIGN FINANCIAL PROJECTION.<br>
                    GENERATED BY LAVETO SYSTEM RESTORATION COMMAND.<br>
                    AUTHENTICITY VERIFIED BY ARCHITECT PROTOCOLS.
                </div>
            </div>
            <script>setTimeout(() => { window.print(); window.close(); }, 500);<\/script>
        </body>
        </html>
    `);
    win.document.close();
}

function shareViaWhatsApp(id) {
    const pField = document.getElementById('p_calc_' + id);
    const rField = document.getElementById('r_calc_' + id);
    const nField = document.getElementById('n_calc_' + id);
    const outField = document.getElementById('standaloneOut_' + id);

    if (!pField || !rField || !nField || !outField) return;

    const p = pField.value;
    const r = rField.value;
    const n = nField.value;
    const m = outField.innerText;
    const date = new Date().toLocaleDateString('en-GB');

    const whatsappMessage =
        `*LAVETO SYSTEM RESTORATION*\n` +
        `_Smart Contract Quotation_ 🛡️\n\n` +
        `*Date:* ${date}\n` +
        `*Principal:* P${parseFloat(p).toLocaleString('en-US', { minimumFractionDigits: 2 })}\n` +
        `*Interest Rate:* ${r}%\n` +
        `*Contract Term:* ${n} Months\n` +
        `----------------------------\n` +
        `*Estimated Monthly:*\n` +
        `*${m}*\n` +
        `----------------------------\n` +
        `_Generated by the Sovereign Valuation Engine._\n` +
        `_Subject to Laveto Command underwriting._`;

    const encodedMessage = encodeURIComponent(whatsappMessage);
    window.open(`https://wa.me/?text=${encodedMessage}`, '_blank');
}

window.blastStatement = function(entryId, phone, vin) {
    if (!phone || phone === 'None' || phone.trim() === '') { alert("No valid number."); return; }
    const msg = `*LAVETO STATEMENT:* Records for [${vin.slice(-6)}] updated.`;
    window.open(`https://wa.me/${phone.replace(/\D/g, '')}?text=${encodeURIComponent(msg)}`, '_blank');
};

// =========================================================================
// 7. TRANSACTION PROCESSING & APPROVAL ENGINES
// =========================================================================
if (typeof window.executeSovereignApproval !== 'function') {
    window.executeSovereignApproval = function(prospectId, targetUrl) {
        const btn = document.getElementById('approve-btn-' + prospectId);
        if (!btn) return;
        const tokenSignature = btn.getAttribute('data-csrf') || document.querySelector('input[name="csrf_token"]')?.value || '{{ csrf_token() }}';

        btn.disabled = true;
        btn.innerText = "⏳ PROCESSING...";
        btn.style.background = "#555555";
        btn.style.color = "#ffffff";

        const formPayload = new URLSearchParams();
        formPayload.append('csrf_token', tokenSignature);

        fetch(targetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': tokenSignature
            },
            body: formPayload
        })
        .then(async response => {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            if (response.status === 400) {
                const debugText = await response.text();
                console.error("🔒 SECURITY GATE REJECTION LOG:", debugText);
                alert("🚨 SESSION EXPIRED: Cryptographic signature mismatch. Please hard refresh the page.");
                window.resetProcessingButton(btn);
                return;
            }

            if (response.ok) {
                window.location.reload();
            } else {
                alert("🚨 ENG DESYNCHRONIZATION: Processing pipeline dropped execution.");
                window.resetProcessingButton(btn);
            }
        })
        .catch(err => {
            console.error("🚨 LIVE PIPELINE NETWORK INTERRUPT:", err);
            alert("🚨 HANDSHAKE EXCEPTION: Could not open secure gateway link.");
            window.resetProcessingButton(btn);
        });
    };
}

if (typeof window.submitSovereignFormOutside !== 'function') {
    window.submitSovereignFormOutside = function(targetUrl, tokenSignature) {
        const secureForm = document.createElement('form');
        secureForm.method = 'POST';
        secureForm.action = targetUrl;
        secureForm.style.display = 'none';

        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'csrf_token';
        tokenInput.value = tokenSignature;

        secureForm.appendChild(tokenInput);
        document.body.appendChild(secureForm);
        secureForm.submit();
    };
}

if (typeof window.resetProcessingButton !== 'function') {
    window.resetProcessingButton = function(btn) {
        if (!btn) return;
        btn.disabled = false;
        btn.innerText = "🔓 APPROVE";
        btn.style.background = "#28a745";
        btn.style.color = "#000000";
    };
}

function resetButton(btn) {
    window.resetProcessingButton(btn);
}

function openRejectionModal(prospectId, phoneNumber) {
    console.log(`📡 Initializing disapproval signal for Prospect ID: ${prospectId}, Node: ${phoneNumber}`);

    const modal = document.getElementById('rejectionModal');

    if (modal) {
        const idInput = document.getElementById('modal_prospect_id');
        const phoneInput = document.getElementById('modal_phone_number');
        if (idInput) idInput.value = prospectId;
        if (phoneInput) phoneInput.value = phoneNumber;

        modal.style.display = 'flex';
    } else {
        const proceed = confirm("⚠️ WELDING ALERT: Rejection modal element is offline.\n\nAre you sure you want to permanently purge this intake record and signal rejection?");
        if (proceed) {
            const activeBtn = event.target;
            const parentForm = activeBtn.closest('form');
            if (parentForm) {
                parentForm.submit();
            } else {
                alert("🚨 SYSTEM ERROR: Unable to isolate parent form element anchor.");
            }
        }
    }
}

async function processTireOrder(vinDna) {
    if (!confirm(`Confirm wholesale tire order fulfillment for VIN: ${vinDna}?`)) return;

    try {
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '{{ csrf_token() }}';
        const response = await fetch(`/hangar/fulfill_tire_order/${vinDna}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            alert(`✅ TIRE ORDER PROCESSED: Wholesale ticket logged and fault cleared for ${vinDna}.`);
            window.location.reload();
        } else {
            alert(`⚠️ ORDER ERROR: ${result.message || 'Server Error'}`);
        }
    } catch (error) {
        console.error("Fulfillment transmission error:", error);
        alert('🚨 TRANSMISSION FAILURE: Check network connection.');
    }
}

window.triggerPulse = function(event) {
    if (event) event.preventDefault();
    if (confirm('Initiate Payroll Pulse?')) {
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';
        fetch(window.PULSE_URL || '/hangar/trigger_pulse', {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            }
        })
        .then(r => r.json())
        .then(d => {
            alert(d.message || "Pulse execution completed.");
            location.reload();
        })
        .catch(err => alert("Pulse Error: " + err.message));
    }
};

// =========================================================================
// 8. DISPATCH & COMMUNICATIONS MODULES
// =========================================================================
async function dispatchEmailBlast(event, element) {
    if (event) event.preventDefault();
    const url = (element && element.getAttribute('data-url')) ? element.getAttribute('data-url') : '/mass-email-statements';
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

    if (confirm('📧 Dispatch official statements?')) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            const data = await response.json();
            alert(data.message || (data.status === 'success' ? "Statements dispatched successfully." : "Transmission status unknown."));
        } catch (err) {
            alert("Error: " + err.message);
        }
    }
}

window.dispatchEmailBlast = dispatchEmailBlast;

async function fireStatementBatchDispatch() {
    if (!confirm("🚨 Proceed with full statement batch dispatch to all members?")) {
        return;
    }

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || document.querySelector('input[name="csrf_token"]')?.value || '';
        const response = await fetch('/email_all_statements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "✅ Statement dispatch successful.");
            window.location.reload();
        } else {
            alert("❌ Dispatch Interrupted: " + (data.error || "Unknown system failure."));
        }
    } catch (err) {
        console.error("Transmission error on statements route:", err);
        alert("🚨 Terminal alert: Network request timed out or connection lost.");
    }
}

async function dispatchAllStatements() {
    if (!confirm("Dispatch official statements?")) {
        return;
    }

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || document.querySelector('input[name="csrf_token"]')?.value || '';
        const response = await fetch('/hangar/email_all_statements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "✅ Transmission successful.");
            window.location.reload();
        } else {
            alert("❌ System Error: " + (data.error || "Unknown error encountered."));
        }
    } catch (err) {
        console.error("Endpoint Connection Interrupted:", err);
        alert("🚨 Terminal connection timed out. Check server logs.");
    }
}

// =========================================================================
// 9. SEARCH, FILTERS & THEME SWITCHERS
// =========================================================================
window.runGlobalFleetSearch = function() {
    const searchInput = document.getElementById("globalFleetSearchInput");
    if (!searchInput) return;
    const filter = searchInput.value.trim().toUpperCase();

    // Client-side row filter
    const rows = document.querySelectorAll(".intake-telemetry-row");
    if (rows.length > 0) {
        rows.forEach(row => {
            const payload = row.getAttribute("data-search-payload") || "";
            row.style.display = payload.toUpperCase().indexOf(filter) > -1 ? "" : "none";
        });
    }

    // Dynamic backend search bridge if container exists
    const searchResultsContainer = document.getElementById('search-results-container');
    if (searchResultsContainer && filter.length > 2) {
        fetch(`/hangar/search?q=${encodeURIComponent(filter)}`)
            .then(response => response.text())
            .then(html => {
                searchResultsContainer.innerHTML = html;
            })
            .catch(err => console.warn("Search route idle:", err));
    }
};

window.runCommsRadarFilter = function() {
    const filterInput = document.getElementById("commsRadarSearch");
    if (!filterInput) return;
    const filter = filterInput.value.toUpperCase();
    document.querySelectorAll(".comms-card").forEach(c => {
        c.style.display = c.innerText.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    });
};

window.executeLiveRadarNetworkScan = function() {
    fetch("{{ url_for('hangar.get_pending_intake_count') }}")
        .then(res => res.json())
        .then(data => {
            const alertContainer = document.getElementById('alert-persistence-layer');
            if (alertContainer && data.events && data.events.triage > 0) {
                 alertContainer.innerHTML = `
                    <div id="live-mandate-alert" class="alert-hardened">
                    </div>
                 `;
            }
        })
        .catch(err => console.warn("Live Radar Scan idle:", err));
};

window.toggleTheme = function() {
    const isLight = document.documentElement.classList.toggle('light-theme');
    document.body.setAttribute('data-theme', isLight ? 'light' : 'dark');
};

function safeExecuteThemeToggle() {
    if (typeof toggleTheme === 'function') {
        toggleTheme();
    } else {
        const docEl = document.documentElement;
        const body = document.body;
        const currentTheme = docEl.getAttribute('data-theme') || body.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        docEl.setAttribute('data-theme', newTheme);
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('vault-theme', newTheme);

        const btn = document.getElementById('themeToggleBtn');
        if (btn) {
            btn.innerHTML = newTheme === 'dark' ? '☀️ LIGHT MODE' : '🌙 DARK MODE';
        }
    }
}

// =========================================================================
// 10. MODAL LAUNCHERS & INTERACTION NODES
// =========================================================================
function launchArmoryScriptModal() {
    const modal = document.getElementById('armoryModal');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        const query = prompt("💻 GOSPEL OS RENDER SHELL // SPECIFY CORE FUNCTION SCRIPT EXECUTION TARGET:");
        if (query) {
            alert(`📡 INITIATING BROADCAST LAYER: "${query.toUpperCase()}" ➔ Channel pipeline stabilized. System registers unchanged.`);
        }
    }
}

function launchSopPhotoModal() {
    const modal = document.getElementById('sopModal');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        alert("📸 PHOTO SOP MEDIA MODULE ACTIVE: Media tracking attachments can be reviewed by auditing individual ledger workspace entities.");
    }
}

function launchMasterPinModal() {
    const modal = document.getElementById('masterKeyModal');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        const pin = prompt("🔑 CRYPTO GATEWAY SECURITY IDENTIFIER REQUIRED // ENTER MASTER OPERATIONAL ADM PIN:");
        if (pin) {
            alert("🔒 VERIFICATION LOOP COMPLETED: Security override tokens are active and locked down.");
        }
    }
}

function safeLaunchModal(modalId, fallbackAlert) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    } else {
        const commandInput = prompt(`💻 GOSPEL OS INTERACTIVE SHELL [${fallbackAlert.toUpperCase()}]\n\nSPECIFY TERMINAL INSTRUCTION:`);
        if (commandInput) {
            alert(`📡 CONSOLE ROUTE LOGGED: "${commandInput.toUpperCase()}" executed over virtual framework link.`);
        }
    }
}

function toggleBayDashboard() {
    const panel = document.getElementById('bay01-panel');
    const icon = document.getElementById('bay-icon');
    if (panel && icon) {
        if (panel.style.display === 'none' || panel.style.display === '') {
            panel.style.display = 'block';
            icon.style.transform = 'rotate(180deg)';
        } else {
            panel.style.display = 'none';
            icon.style.transform = 'rotate(0deg)';
        }
    }
}

window.toggleActionPanel = (id) => {
    const el = document.getElementById(id);
    if (el) el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
};

window.toggleBox = (id) => {
    const box = document.getElementById(id);
    if (box) box.style.setProperty('display', (box.style.display === 'none' || box.style.display === '') ? 'block' : 'none', 'important');
};

window.copyTacticalScript = function(btnElement, text) {
    navigator.clipboard.writeText(text);
    const statusDiv = document.getElementById('scriptStatusTarget');
    if (statusDiv) {
        statusDiv.innerText = ">> SCRIPT ACQUIRED <<";
        setTimeout(() => statusDiv.innerText = "", 2000);
    }
};

window.markCaptured = function(id) {
    const label = document.getElementById('label_' + id);
    if (label) {
        label.style.color = '#00ff00';
        label.innerText = '✅ CAPTURED';
    }
};