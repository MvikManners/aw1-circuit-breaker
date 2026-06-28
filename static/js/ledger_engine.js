// ==========================================
// 1. MASTER UI INITIALIZATION
// ==========================================
document.addEventListener("DOMContentLoaded", function() {
    console.log("Laveto Ledger: Initializing...");

    // Ensure horizontal carousel visibility
    const cards = document.querySelectorAll('.asset-card');
    if (cards.length > 0) {
        cards.forEach(c => c.style.setProperty('display', 'none', 'important'));
        cards[0].classList.add('is-active');
        cards[0].style.setProperty('display', 'block', 'important');
    }

    // Scroll Fix for Pagination
    if (window.location.search.includes('page=')) {
        const registryTable = document.getElementById('fleet-registry');
        if (registryTable) {
            window.scrollTo({ top: registryTable.getBoundingClientRect().top + window.scrollY - 140, behavior: 'smooth' });
        }
    }
});

class SovereignLedger {
        constructor() {
            this.ledger = [];
            this.assetRegistry = {};
        }

        validateAndRecord(memberId, amount, telemetry) {
            // Your validation logic here
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

// ==========================================
// 2. CORE FUNCTIONS
// ==========================================
window.changeCarouselPage = function(direction) {
    const allCards = Array.from(document.querySelectorAll('.asset-card'));
    const total = allCards.length;
    if (total <= 1) return;

    // Find the currently active card
    let activeIndex = allCards.findIndex(c => c.classList.contains('is-active'));
    if (activeIndex === -1) activeIndex = 0;

    // Hide current
    allCards[activeIndex].classList.remove('is-active');
    allCards[activeIndex].style.setProperty('display', 'none', 'important');

    // Calculate next
    activeIndex = (activeIndex + direction + total) % total;

    // Show next
    allCards[activeIndex].classList.add('is-active');
    allCards[activeIndex].style.setProperty('display', 'block', 'important');

    // Update indicator
    const ind = document.querySelector('.carousel-current-indicator');
    if (ind) ind.textContent = activeIndex + 1;
};
let intakeCurrentPage = 1;

function autoAdjustTerm(id) {
    const inputField = document.getElementById('p_calc_' + id);
    if (!inputField) return;
    let p = parseFloat(inputField.value);

    // Prevent negative numbers
    if (isNaN(p) || p < 0) {
        p = 0;
        inputField.value = 0;
    }

    const t = document.getElementById('n_calc_' + id);
    if (!t) return;

    // Logic for term adjustment based on principal
    if (p <= 3000) { t.value = "6"; }
    else if (p <= 10000) { t.value = "12"; }
    else if (p <= 25000) { t.value = "24"; }
    else { t.value = "36"; }
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

    outField.innerText = 'P' + monthly.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    resultBox.style.display = 'block';
}

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
                .quote-table { width: 100%; margin: 40px 0; border-top: 1px solid #eee; }
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
        `*Principal:* P${parseFloat(p).toLocaleString('en-US', {minimumFractionDigits: 2})}\n` +
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
function checkPendingMandates() {
        // Fetch data from the background API we built earlier
        fetch("/hangar/api/pending_mandates")
            .then(res => res.json())
            .then(data => {
                let totalPending = 0;
                // Count all nodes across all cohorts
                if (data.cohorts) {
                    for (let cohort in data.cohorts) {
                        totalPending += data.cohorts[cohort].nodes;
                    }
                }

                const alertBox = document.getElementById('live-mandate-alert');
                const countSpan = document.getElementById('mandate-count');

                if (totalPending > 0) {
                    countSpan.innerText = totalPending;
                    alertBox.style.display = 'flex'; // Unhide the alert
                } else {
                    alertBox.style.display = 'none'; // Hide if queue is cleared
                }
            })
            .catch(err => console.log("Radar Scan Idle."));
    }

    // Check immediately on load, then scan every 5 seconds
    document.addEventListener('DOMContentLoaded', checkPendingMandates);
    setInterval(checkPendingMandates, 5000);

async function dispatchEmailBlast() {
    const response = await fetch('/mass-email-statements', { method: 'POST' });
    const data = await response.json();

    // Check the structure explicitly
    if (data && data.message) {
        alert(data.message);
    } else {
        alert("Transmission status unknown.");
    }
}

window.runCommsRadarFilter = function() {
    const filter = document.getElementById("commsRadarSearch").value.toUpperCase();
    document.querySelectorAll(".comms-card").forEach(c => {
        c.style.display = c.innerText.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    });
};
window.toggleTheme = function() {
    const isLight = document.documentElement.classList.toggle('light-theme');
    document.body.setAttribute('data-theme', isLight ? 'light' : 'dark');
};

window.toggleActionPanel = (id) => {
    const el = document.getElementById(id);
    if(el) el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
};

window.toggleBox = (id) => {
    const box = document.getElementById(id);
    if(box) box.style.setProperty('display', (box.style.display === 'none' || box.style.display === '') ? 'block' : 'none', 'important');
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
    if (label) { label.style.color = '#00ff00'; label.innerText = '✅ CAPTURED'; }
};

window.calculateSovereignMarketValue = function(id, integrity, shield, debt) {
    const baseVal = parseFloat(document.getElementById('baseMarketVal_' + id).value);
    if (!baseVal) { alert("Enter Base Value"); return; }
    const total = baseVal + (baseVal * (1.0 - integrity)) + shield - debt;
    alert("Calculated Valuation: P" + total.toLocaleString(undefined, {minimumFractionDigits: 2}));
};

window.blastStatement = function(entryId, phone, vin) {
    if (!phone || phone === 'None' || phone.trim() === '') { alert("No valid number."); return; }
    const msg = `*LAVETO STATEMENT:* Records for [${vin.slice(-6)}] updated.`;
    window.open(`https://wa.me/${phone.replace(/\D/g, '')}?text=${encodeURIComponent(msg)}`, '_blank');
};

window.triggerPulse = function(event) {
    event.preventDefault();
    if (confirm('Initiate Payroll Pulse?')) {
        // Use the globally injected variable
        fetch(window.PULSE_URL, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('input[name="csrf_token"]').value,
                "Content-Type": "application/json"
            }
        })
        .then(r => r.json())
        .then(d => {
            alert(d.message);
            location.reload();
        });
    }
};

window.runGlobalFleetSearch = function() {
    const filter = document.getElementById("globalFleetSearchInput").value.trim().toUpperCase();
    document.querySelectorAll(".intake-telemetry-row").forEach(row => {
        const payload = row.getAttribute("data-search-payload") || "";
        row.style.display = payload.indexOf(filter) > -1 ? "" : "none";
    });
};

window.dispatchEmailBlast = function(event, element) {
    event.preventDefault();
    const url = element.getAttribute('data-url');
    if (confirm('📧 Dispatch official statements?')) {
        fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value } })
        .then(r => r.json()).then(d => alert(d.message)).catch(err => alert("Error: " + err));
    }
};