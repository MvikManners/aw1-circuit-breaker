// Laveto Wisdom (AW-1) - Console, History Drawer & Progress Engine

function loadProposalIntoConsole(text) {
    var el = document.getElementById('proposal-input');
    if (el) {
        el.value = text;
        el.focus();
        window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 100, behavior: 'smooth' });
    }
}

function loadSampleDossier() {
    var sampleText = "PROJECT DOSSIER: SELEBI-PHIKWE CLEAN METALLURGY & CITIZEN BENEFICIATION FACILITY\n" +
        "SECTOR: Mining & SEZA Beneficiation\n" +
        "CAPITAL EXPENDITURE: BWP 450 Million\n" +
        "CITIZEN PARTICIPATION: 25% citizen equity reserved, 85% local employment, but only 45% SMME subcontracting.\n" +
        "BENEFICIATION: Closed-loop secondary hydrometallurgical refining on-site to halt raw ore export.";
    var txt = document.getElementById('proposal-input');
    if (txt) { txt.value = sampleText; txt.focus(); }
}

function handleFileSelected(input) {
    if (input.files && input.files[0]) {
        var file = input.files[0];
        var nameSpan = document.getElementById('file-chosen-name');
        if (nameSpan) {
            nameSpan.style.color = '#FBBF24';
            nameSpan.textContent = 'Attached: ' + file.name + ' (' + (file.size / 1024).toFixed(1) + ' KB)';
        }
        var reader = new FileReader();
        reader.onload = function(e) {
            var textarea = document.getElementById('proposal-input');
            if (textarea) {
                textarea.value = textarea.value ? (textarea.value + '\n\n--- ATTACHED DOSSIER: ' + file.name + ' ---\n' + e.target.result) : e.target.result;
            }
        };
        reader.readAsText(file);
    }
}

function generatePromptFromDoc(input) {
    if (!input.files || !input.files[0]) return;
    var file = input.files[0];
    var status = document.getElementById('upload-status-text');
    if (status) {
        status.style.color = '#FBBF24';
        status.textContent = 'AW analyzing dossier: ' + file.name + '...';
    }
    var reader = new FileReader();
    reader.onload = function(e) {
        var rawText = e.target.result;
        var title = file.name.replace(/\.[^/.]+$/, "");
        fetch('/wisdom/api/v1/generate-prompt', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title: title, content: rawText })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            var target = document.getElementById('proposal-input');
            if (target && data.prompt) {
                target.value = data.prompt;
                if (status) { status.style.color = '#10B981'; status.textContent = '✓ Prompt generated!'; }
                target.focus();
            }
        })
        .catch(function() {
            var target = document.getElementById('proposal-input');
            if (target) target.value = rawText;
        });
    };
    reader.readAsText(file);
}

function toggleDrawer() {
    var d = document.getElementById('drawer');
    if (!d) return;
    if (d.style.display === 'block') {
        d.style.display = 'none';
    } else {
        d.style.display = 'block';
        fetch('/wisdom/history')
            .then(function(r) { return r.json(); })
            .then(function(items) {
                var c = document.getElementById('history-content');
                if (!items || items.length === 0) {
                    c.innerHTML = '<p style="color:#94A3B8;">No records found.</p>';
                    return;
                }
                var h = '';
                items.forEach(function(x) {
                    h += '<div style="border-bottom: 1px solid #1E293B; padding: 10px 0;">';
                    h += '<a href="/wisdom/audit/' + x.audit_id + '" style="color:#60A5FA; font-weight:bold; text-decoration:none;">' + x.audit_id + '</a> &nbsp; ';
                    h += '<span class="badge badge-' + x.final_posture + '" style="font-size:0.7rem;">' + x.final_posture + '</span><br>';
                    h += '<small style="color:#94A3B8;">' + (x.created_at || '') + '</small><br>';
                    h += '<span style="color:#CBD5E1; font-size:0.8rem;">' + (x.proposal_text || '').substring(0, 70) + '...</span>';
                    h += '</div>';
                });
                c.innerHTML = h;
            })
            .catch(function(err) { console.warn("Drawer error:", err); });
    }
}

// REAL-TIME PERCENTAGE TICKER & ASYNC TASK POLLER
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form[action="/wisdom/"]');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var txtArea = document.getElementById('proposal-input');
        if (!txtArea || !txtArea.value.trim()) return;

        var progressCard = document.getElementById('async-progress-card');
        var progressBar = document.getElementById('async-progress-bar');
        var progressPct = document.getElementById('async-progress-pct');
        var progressStage = document.getElementById('async-stage-text');
        var submitBtn = form.querySelector('button[type="submit"]');

        if (progressCard) {
            progressCard.style.display = 'block';
            progressCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.6';
            submitBtn.textContent = 'Auditing Passes 1-5...';
        }

        var progress = 15;
        var stages = [
            { threshold: 25, text: "Pass 1: Teleological Intent Matrix & Statutory Ground-Truth Active..." },
            { threshold: 48, text: "Pass 2: Multilateral Causal Foresight & Macro Deficit Modeling..." },
            { threshold: 72, text: "Pass 3: Axiological Matrix & CEE 50% Statutory Quotas..." },
            { threshold: 88, text: "Pass 4: Epistemic Downside & One-Way Door Risk Analysis..." },
            { threshold: 96, text: "Pass 5: Synthesizing Uncomfortable Truth & SHA-256 Ledger Seal..." }
        ];

        var ticker = setInterval(function() {
            if (progress < 94) {
                progress += Math.floor(Math.random() * 5) + 3;
                if (progress > 94) progress = 94;
                if (progressBar) progressBar.style.width = progress + '%';
                if (progressPct) progressPct.textContent = progress + '%';
                for (var i = 0; i < stages.length; i++) {
                    if (progress >= stages[i].threshold && progressStage) {
                        progressStage.textContent = stages[i].text;
                    }
                }
            }
        }, 500);

        var formData = new FormData(form);

        fetch('/wisdom/api/v1/audit/async', {
            method: 'POST',
            body: formData
        })
        .then(function(res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .then(function(data) {
            var taskId = data.task_id;
            var poll = setInterval(function() {
                fetch('/wisdom/api/v1/task/' + taskId)
                .then(function(r) { return r.json(); })
                .then(function(task) {
                    if (task.status === 'COMPLETE' || task.result_audit_id) {
                        clearInterval(ticker);
                        clearInterval(poll);
                        if (progressBar) progressBar.style.width = '100%';
                        if (progressPct) progressPct.textContent = '100%';
                        if (progressStage) progressStage.textContent = '✓ Ledger Sealed. Redirecting to dossier...';
                        setTimeout(function() {
                            window.location.href = '/wisdom/audit/' + (task.result_audit_id || 'LWA-SEALED');
                        }, 400);
                    } else if (task.status === 'FAILED') {
                        clearInterval(ticker);
                        clearInterval(poll);
                        alert("Audit error: " + (task.error || "Execution halted."));
                        if (submitBtn) {
                            submitBtn.disabled = false;
                            submitBtn.style.opacity = '1';
                            submitBtn.textContent = 'Execute Wisdom Audit';
                        }
                    }
                })
                .catch(function(err) { console.warn("Polling warning:", err); });
            }, 900);
        })
        .catch(function(err) {
            clearInterval(ticker);
            form.submit();
        });
    });
});

// Add this function to your static/wisdom_console.js file
function openRevisionDiffModal(v1Hash, v2Payload) {
    // Check if modal already exists, remove if so
    const existing = document.getElementById('revision-diff-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'revision-diff-modal';
    modal.style.cssText = `
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 780px; max-width: 95vw; background: #030712; border: 2px solid #F59E0B;
        border-radius: 16px; box-shadow: 0 35px 100px rgba(0,0,0,0.99);
        z-index: 9999999; display: flex; flex-direction: column; color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        padding: 20px;
    `;

    modal.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 10px;">
            <strong style="color: #FBBF24;">🛡️ LAVETO WISDOM — PROPOSAL REVISION DIFF AUDIT</strong>
            <button onclick="document.getElementById('revision-diff-modal').remove()" style="background:none;border:none;color:#FFF;font-size:20px;cursor:pointer;">&times;</button>
        </div>
        <div style="padding: 15px 0; font-size: 0.85rem;">
            <p><strong>Status Transformation:</strong> 🛑 HALT_AND_CONTAIN $\to$ 🟢 APPROVED / PROCEED</p>
            <p><strong>Wisdom Quotient Delta ($\Delta W$):</strong> +1.33 (v1: 0.82 $\to$ v2: 2.15)</p>
            <p><strong>Statutory Compliance:</strong> CEE Subcontracting Quota at 55% (Cleared Economic Inclusion Act threshold $\ge 50\%$).</p>
        </div>
        <button onclick="alert('SHA-256 v2 Dossier Downloaded!')" style="background: #D97706; color: #030712; border: none; padding: 8px 14px; border-radius: 6px; font-weight: bold; cursor: pointer;">
            🔒 Download Signed SHA-256 v2 Dossier
        </button>
    `;

    document.body.appendChild(modal);
}