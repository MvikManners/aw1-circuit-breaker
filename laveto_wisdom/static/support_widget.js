/**
 * ===================================================================================
 * LAVETO WISDOM (AW-1) — 4-NOTEBOOK SUPPORT & FLOATING APP HUD WIDGET (STABLE V19 - LEFT DOCKED)
 * ===================================================================================
 */

(function () {
    if (window.LavetoSupportWidgetV19Loaded) return;
    window.LavetoSupportWidgetV19Loaded = true;

    // Remove any stale or duplicate instances on startup to prevent overlap
    ['laveto-chat-widget-button', 'laveto-chat-window', 'laveto-hud-launcher', 'laveto-hud-modal'].forEach(id => {
        const existing = document.getElementById(id);
        if (existing) existing.remove();
    });

    // Inject Maximum-Contrast CSS Styles Safely
    if (!document.getElementById('laveto-widget-styles')) {
        const style = document.createElement('style');
        style.id = 'laveto-widget-styles';
        style.innerHTML = `
            #laveto-chat-widget-button {
                position: fixed !important; bottom: 24px !important; right: 24px !important; width: 60px !important; height: 60px !important;
                border-radius: 50% !important; background: linear-gradient(135deg, #10B981 0%, #047857 100%) !important;
                box-shadow: 0 10px 35px rgba(16, 185, 129, 0.7), 0 0 0 3px rgba(52, 211, 153, 0.5) !important; cursor: pointer !important; z-index: 999999 !important;
                display: flex !important; align-items: center !important; justify-content: center !important; transition: transform 0.2s ease !important;
            }
            #laveto-chat-widget-button:hover { transform: scale(1.08) !important; }
            #laveto-chat-widget-button svg { width: 28px !important; height: 28px !important; fill: #ffffff !important; }

            #laveto-chat-window {
                position: fixed !important; bottom: 96px !important; right: 24px !important; width: 420px !important; max-width: calc(100vw - 32px) !important;
                height: 600px !important; max-height: calc(100vh - 120px) !important; background: #030712 !important;
                border: 2px solid #3B82F6 !important; border-radius: 16px !important; box-shadow: 0 30px 90px rgba(0, 0, 0, 0.98), 0 0 50px rgba(59, 130, 246, 0.3) !important;
                z-index: 999999 !important; display: none; flex-direction: column !important; overflow: hidden !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; color: #f8fafc !important;
            }

            /* High-Contrast Floating App HUD Launcher (Anchored Bottom-Left) */
            #laveto-hud-launcher {
                position: fixed !important; bottom: 24px !important; left: 24px !important;
                background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%) !important;
                color: #030712 !important; font-weight: 900 !important; padding: 12px 20px !important;
                border-radius: 30px !important; cursor: pointer !important; z-index: 999998 !important;
                box-shadow: 0 10px 35px rgba(245,158,11,0.7), 0 0 0 3px rgba(251,191,36,0.5) !important; display: flex !important; align-items: center !important; gap: 8px !important;
                font-size: 0.85rem !important; transition: transform 0.2s ease !important;
            }
            #laveto-hud-launcher:hover { transform: scale(1.05) !important; }

            /* Sovereign Dossier Interrogation Modal DOCKED ON THE LEFT DIRECTLY ABOVE LAUNCHER */
            #laveto-hud-modal {
                position: fixed !important; bottom: 84px !important; left: 24px !important; right: auto !important;
                width: 440px !important; max-width: calc(100vw - 32px) !important; height: 590px !important; max-height: calc(100vh - 110px) !important;
                background: #030712 !important; border: 2px solid #F59E0B !important; border-radius: 16px !important;
                box-shadow: 0 35px 100px rgba(0, 0, 0, 0.99), 0 0 60px rgba(217,119,6,0.35) !important; z-index: 9999999 !important; display: none; flex-direction: column !important; overflow: hidden !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; color: #f8fafc !important;
            }

            .laveto-chat-header { background: #0B132B !important; padding: 12px 16px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; border-bottom: 2px solid #334155 !important; }
            .laveto-chat-header-title { display: flex !important; align-items: center !important; gap: 10px !important; font-weight: 800 !important; font-size: 14px !important; }
            .laveto-status-dot { width: 10px !important; height: 10px !important; border-radius: 50% !important; background: #10B981 !important; box-shadow: 0 0 12px #10B981 !important; }

            .laveto-mode-bar { background: #070B14 !important; padding: 8px 12px !important; display: flex !important; gap: 6px !important; overflow-x: auto !important; border-bottom: 1px solid #1E293B !important; }
            .laveto-mode-pill {
                background: #111827 !important; color: #94A3B8 !important; border: 1px solid #475569 !important; padding: 5px 12px !important;
                border-radius: 12px !important; font-size: 11px !important; font-weight: 700 !important; cursor: pointer !important; white-space: nowrap !important;
            }
            .laveto-mode-pill.active { background: #059669 !important; color: #ffffff !important; border-color: #34D399 !important; box-shadow: 0 0 12px rgba(5, 150, 105, 0.6) !important; }

            .laveto-chat-messages { flex: 1 !important; padding: 14px !important; overflow-y: auto !important; display: flex !important; flex-direction: column !important; gap: 10px !important; background: #020408 !important; }
            .laveto-msg { max-width: 90% !important; padding: 10px 12px !important; border-radius: 12px !important; font-size: 13px !important; line-height: 1.45 !important; word-break: break-word !important; }
            .laveto-msg-bot { align-self: flex-start !important; background: #0F172A !important; color: #f8fafc !important; border: 1px solid #475569 !important; box-shadow: 0 4px 16px rgba(0,0,0,0.6) !important; }
            .laveto-msg-user { align-self: flex-end !important; background: #047857 !important; color: #ffffff !important; font-weight: 600 !important; box-shadow: 0 4px 16px rgba(4,120,87,0.4) !important; }
            .laveto-dossier-tag { display: block !important; margin-top: 6px !important; font-size: 10px !important; font-family: monospace !important; color: #FBBF24 !important; background: rgba(0, 0, 0, 0.7) !important; padding: 4px 6px !important; border-radius: 4px !important; border: 1px solid #475569 !important; }

            .laveto-chat-input-area { padding: 10px 14px !important; background: #0B132B !important; border-top: 2px solid #334155 !important; display: flex !important; gap: 8px !important; }
            .laveto-chat-input { flex: 1 !important; background: #020408 !important; border: 1px solid #64748B !important; border-radius: 8px !important; padding: 8px 10px !important; color: #ffffff !important; font-size: 13px !important; outline: none !important; }
            .laveto-chat-input:focus { border-color: #34D399 !important; box-shadow: 0 0 10px rgba(52, 211, 153, 0.5) !important; }
            .laveto-chat-send { background: #059669 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0 14px !important; font-weight: 800 !important; cursor: pointer !important; }
        `;
        document.head.appendChild(style);
    }

    function initWidget() {
        if (document.getElementById('laveto-chat-widget-button')) return;

        // 1. Render Floating Support Chat Button & Window (Right Side)
        const button = document.createElement('div');
        button.id = 'laveto-chat-widget-button';
        button.innerHTML = `<svg viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.477 2 12c0 1.821.487 3.53 1.338 5L2.5 21.5l4.5-.838A9.955 9.955 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2z"/></svg>`;
        document.body.appendChild(button);

        const windowEl = document.createElement('div');
        windowEl.id = 'laveto-chat-window';
        windowEl.innerHTML = `
            <div class="laveto-chat-header">
                <div class="laveto-chat-header-title">
                    <span class="laveto-status-dot"></span>
                    <span>Laveto Wisdom (4-Notebook Hub)</span>
                </div>
                <button style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:20px;" id="laveto-close-btn">&times;</button>
            </div>

            <div class="laveto-mode-bar" id="laveto-mode-selector">
                <button class="laveto-mode-pill active" data-mode="gospel">🛡️ 1. Gospel OS</button>
                <button class="laveto-mode-pill" data-mode="investment">🇧🇼 2. Investment</button>
                <button class="laveto-mode-pill" data-mode="village">📒 3. Village Ledgers</button>
                <button class="laveto-mode-pill" data-mode="tokenomics">⚙️ 4. Tokenomics & API</button>
            </div>

            <div class="laveto-chat-messages" id="laveto-chat-msg-container">
                <div class="laveto-msg laveto-msg-bot">
                    Dumela! Welcome to <b>p20.laveto.net</b>.<br><br>
                    Select your notebook focus above, ask a question, and receive guided recommendations!
                </div>
            </div>

            <div class="laveto-chat-input-area">
                <input type="text" class="laveto-chat-input" id="laveto-chat-input-field" placeholder="Ask anything in selected notebook..." />
                <button class="laveto-chat-send" id="laveto-chat-send-btn">Send</button>
            </div>
        `;
        document.body.appendChild(windowEl);

        // 2. Render Floating App HUD Launcher & Interactive Dialogue Modal (Left Side)
        const hudLauncher = document.createElement('div');
        hudLauncher.id = 'laveto-hud-launcher';
        hudLauncher.innerHTML = `<span>🛡️ Open AW App HUD</span>`;
        document.body.appendChild(hudLauncher);

        const hudModal = document.createElement('div');
        hudModal.id = 'laveto-hud-modal';
        hudModal.innerHTML = `
            <div class="laveto-chat-header" style="background: #0B132B !important;">
                <div class="laveto-chat-header-title">
                    <span class="laveto-status-dot" style="background: #FBBF24; box-shadow: 0 0 12px #FBBF24;"></span>
                    <span style="color: #FBBF24; font-weight: 900; letter-spacing: 0.3px;">Sovereign Dossier Interrogation HUD</span>
                </div>
                <button style="background:none;border:none;color:#F8FAFC;cursor:pointer;font-size:22px;font-weight:bold;" id="laveto-hud-close-btn">&times;</button>
            </div>

            <!-- Dynamic Dossier Search Directory Tray -->
            <div style="background: #070B14; padding: 8px 14px; border-bottom: 2px solid #334155; position: relative;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 0.72rem; color: #FBBF24; font-weight: 900; white-space: nowrap;">DOSSIER:</span>
                    <input type="text" id="dossier-search-input" placeholder="Search any company, ID, or portfolio..." style="flex: 1; background: #020408; border: 1px solid #64748B; color: #FFF; padding: 5px 8px; border-radius: 6px; font-size: 0.75rem; outline: none;" oninput="filterDossiers(this.value)" />
                </div>
                <div id="dossier-dropdown-results" style="position: absolute; top: 100%; left: 14px; right: 14px; background: #0B132B; border: 2px solid #475569; border-radius: 0 0 6px 6px; max-height: 140px; overflow-y: auto; display: none; font-size: 0.75rem; z-index: 10; box-shadow: 0 20px 40px rgba(0,0,0,0.95);"></div>
            </div>

            <!-- Dynamic Interrogation Chat Stream -->
            <div id="aw-chat-stream" style="padding: 12px 14px; max-height: 150px; overflow-y: auto; font-size: 0.82rem; display: flex; flex-direction: column; gap: 10px; background: #020408;">
                <div style="background: #0F172A; padding: 10px 12px; border-radius: 8px; border-left: 4px solid #F59E0B; color: #f8fafc; box-shadow: 0 4px 16px rgba(0,0,0,0.6);">
                    <strong style="color: #FBBF24; display: block; margin-bottom: 3px;">🤖 AW-1 Assistant</strong>
                    Audit active for enterprise portfolio.<br>
                    • Use the search bar above or click <b>Past Audits</b> to queue records.
                </div>
            </div>

            <!-- Quick-Action Preset Chips -->
            <div style="padding: 6px 14px; background: #070B14; border-top: 1px solid #334155; display: flex; gap: 6px; flex-wrap: wrap;">
                <button onclick="sendHudPresetQuery('Unpack Pass 2 Risk')" style="background: #111827; border: 1px solid #475569; color: #F1F5F9; font-size: 0.7rem; padding: 4px 8px; border-radius: 6px; cursor: pointer; font-weight: 700;">🔍 Unpack Pass 2 Risk</button>
                <button onclick="sendHudPresetQuery('Simulate 50% CEE Compliance')" style="background: #111827; border: 1px solid #475569; color: #F1F5F9; font-size: 0.7rem; padding: 4px 8px; border-radius: 6px; cursor: pointer; font-weight: 700;">⚡ Simulate CEE Fix</button>
                <button onclick="sendHudPresetQuery('Draft Board Defense Brief')" style="background: #111827; border: 1px solid #475569; color: #F1F5F9; font-size: 0.7rem; padding: 4px 8px; border-radius: 6px; cursor: pointer; font-weight: 700;">📋 Prepare Board Brief</button>
            </div>

            <!-- Interactive Dialogue Input Bar -->
            <div style="padding: 8px 14px; background: #030712; border-top: 2px solid #334155; display: flex; gap: 8px;">
                <input type="text" id="aw-chat-input" placeholder="Ask AW to unpack risks or simulate changes..." style="flex: 1; background: #020408; border: 1px solid #64748B; color: #FFF; padding: 7px 10px; border-radius: 6px; font-size: 0.8rem; outline: none;" />
                <button id="aw-chat-send-btn" style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: #030712; font-weight: 900; border: none; padding: 7px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; box-shadow: 0 4px 15px rgba(245,158,11,0.5);">Send</button>
            </div>

            <!-- Platform Navigation Footer -->
            <div style="padding: 6px 14px; background: #070B14; border-top: 1px solid #334155;">
                <div style="font-size: 0.65rem; color: #FBBF24; font-weight: 900; text-transform: uppercase; margin-bottom: 3px; letter-spacing: 0.5px;">Platform Navigation</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                    <a href="/wisdom/" target="_blank" style="background: #111827; border: 1px solid #475569; color: #60A5FA; text-align: center; padding: 4px; border-radius: 6px; font-size: 0.7rem; text-decoration: none; font-weight: 700;">Assurance Console</a>
                    <a href="/wisdom/sandbox" target="_blank" style="background: #111827; border: 1px solid #475569; color: #60A5FA; text-align: center; padding: 4px; border-radius: 6px; font-size: 0.7rem; text-decoration: none; font-weight: 700;">Policy Simulator</a>
                    <a href="/wisdom/analytics" target="_blank" style="background: #111827; border: 1px solid #475569; color: #60A5FA; text-align: center; padding: 4px; border-radius: 6px; font-size: 0.7rem; text-decoration: none; font-weight: 700;">Executive Analytics</a>
                    <a href="/wisdom/generate" target="_blank" style="background: #111827; border: 1px solid #475569; color: #FBBF24; text-align: center; padding: 4px; border-radius: 6px; font-size: 0.7rem; text-decoration: none; font-weight: 700;">Idea Incubator</a>
                </div>
            </div>
        `;
        document.body.appendChild(hudModal);

        // Global Active Dossier State & Dynamic Search Handler
        window.activeDossierHash = '0xa96f0ebb1f43...';
        window.hudCitations = {};

        window.filterDossiers = async function(query) {
            const resultsBox = document.getElementById('dossier-dropdown-results');
            if (!resultsBox) return;

            if (!query.trim()) {
                resultsBox.style.display = 'none';
                return;
            }

            try {
                const res = await fetch('/wisdom/api/v1/dossiers/search?q=' + encodeURIComponent(query));
                const data = await res.json();
                
                if (data.results && data.results.length > 0) {
                    let html = '';
                    data.results.forEach(d => {
                        html += `<div onclick="switchDossier('${d.hash}', '${d.id}', '${d.name}')" style="padding: 7px 10px; cursor: pointer; border-bottom: 1px solid #334155; color: #F8FAFC;" onmouseover="this.style.background='#1E293B'" onmouseout="this.style.background='transparent'">
                            <strong style="color: #60A5FA;">#${d.id}</strong> — <span style="color: #E2E8F0;">${d.name}</span>
                        </div>`;
                    });
                    resultsBox.innerHTML = html;
                    resultsBox.style.display = 'block';
                } else {
                    resultsBox.innerHTML = `<div style="padding: 7px 10px; color: #94A3B8;">No matching dossiers found.</div>`;
                    resultsBox.style.display = 'block';
                }
            } catch (err) {
                console.error('Dossier search error:', err);
            }
        };

        window.switchDossier = async function(hash, dossierId, companyName) {
            window.activeDossierHash = hash;
            
            const searchInput = document.getElementById('dossier-search-input');
            const resultsBox = document.getElementById('dossier-dropdown-results');
            if (searchInput) searchInput.value = `#${dossierId} (${companyName})`;
            if (resultsBox) resultsBox.style.display = 'none';

            const stream = document.getElementById('aw-chat-stream');
            if (stream) {
                const loadingMsg = document.createElement('div');
                loadingMsg.style.cssText = 'background: #0F172A; padding: 8px 12px; border-radius: 8px; font-size: 0.75rem; color: #FBBF24; font-family: monospace; border: 1px solid #334155;';
                loadingMsg.textContent = `⚡ Querying live state for dossier #${dossierId} (${companyName})...`;
                stream.appendChild(loadingMsg);
                stream.scrollTop = stream.scrollHeight;

                try {
                    const res = await fetch('/wisdom/api/v1/dossier/' + encodeURIComponent(hash));
                    const data = await res.json();
                    loadingMsg.remove();

                    const dossier = data.dossier;
                    const statusColor = dossier.status === 'APPROVED' ? '#10B981' : '#F59E0B';

                    const infoBubble = document.createElement('div');
                    infoBubble.style.cssText = `background: #0F172A; padding: 10px 12px; border-radius: 8px; border-left: 4px solid ${statusColor}; color: #f8fafc; font-size: 0.82rem; box-shadow: 0 4px 16px rgba(0,0,0,0.6);`;
                    infoBubble.innerHTML = `
                        <strong style="color: ${statusColor}; display: block; margin-bottom: 3px;">📂 Active Dossier: #${dossier.id}</strong>
                        ${dossier.title}<br>
                        • Wisdom Quotient (W): ${dossier.w_score} (${dossier.status})<br>
                        • Note: ${dossier.warning}
                    `;
                    stream.appendChild(infoBubble);
                    stream.scrollTop = stream.scrollHeight;
                } catch (err) {
                    loadingMsg.textContent = `⚡ Switched context to #${dossierId} (Offline mode)`;
                }
            }
        };

        // Silently update active dossier state when clicking top "Past Audits" without blocking screen view
        const pastAuditsBtn = Array.from(document.querySelectorAll('button, a')).find(el => el.textContent.includes('Past Audits'));
        if (pastAuditsBtn) {
            pastAuditsBtn.addEventListener('click', () => {
                window.activeDossierHash = '0xa96f0ebb1f43...';
                const searchInput = document.getElementById('dossier-search-input');
                if (searchInput) {
                    searchInput.value = '#CEDA-8921 (Commercial Solar Cold-Chain Storage)';
                }
            });
        }

        window.toggleStatuteDrawer = function(citId) {
            const drawer = document.getElementById('statute-drawer');
            const cit = window.hudCitations[citId];
            if (drawer && cit) {
                drawer.style.display = drawer.style.display === 'block' ? 'none' : 'block';
                drawer.innerHTML = `<strong style="color: #FBBF24;">${cit.title}:</strong> ${cit.text}`;
            }
        };

        // Chat Widget Event Listeners
        let currentMode = 'gospel';
        const msgContainer = document.getElementById('laveto-chat-msg-container');
        const inputField = document.getElementById('laveto-chat-input-field');
        const sendBtn = document.getElementById('laveto-chat-send-btn');
        const closeBtn = document.getElementById('laveto-close-btn');
        const modePills = windowEl.querySelectorAll('.laveto-mode-pill');

        button.addEventListener('click', () => { windowEl.style.display = windowEl.style.display === 'flex' ? 'none' : 'flex'; });
        closeBtn.addEventListener('click', () => { windowEl.style.display = 'none'; });

        // App HUD Interrogation Modal Event Listeners
        const hudCloseBtn = document.getElementById('laveto-hud-close-btn');
        const hudInput = document.getElementById('aw-chat-input');
        const hudSendBtn = document.getElementById('aw-chat-send-btn');
        const hudStream = document.getElementById('aw-chat-stream');

        hudLauncher.addEventListener('click', () => { hudModal.style.display = hudModal.style.display === 'flex' ? 'none' : 'flex'; });
        hudCloseBtn.addEventListener('click', () => { hudModal.style.display = 'none'; });

        window.sendHudPresetQuery = function(text) {
            if (hudInput) {
                hudInput.value = text;
                executeHudQuery();
            }
        };

        async function executeHudQuery() {
            const query = hudInput.value.trim();
            if (!query) return;

            hudInput.value = '';

            const userBubble = document.createElement('div');
            userBubble.style.cssText = 'background: #1E3A8A; padding: 8px 12px; border-radius: 8px; align-self: flex-end; max-width: 85%; color: #f8fafc; font-size: 0.82rem; box-shadow: 0 4px 12px rgba(0,0,0,0.4);';
            userBubble.innerHTML = `<strong style="display: block; font-size: 0.7rem; color: #93C5FD; margin-bottom: 2px;">👤 Loan Officer</strong>${query}`;
            hudStream.appendChild(userBubble);

            const loadingBubble = document.createElement('div');
            loadingBubble.id = 'aw-hud-loading';
            loadingBubble.style.cssText = 'background: #0F172A; padding: 8px 12px; border-radius: 8px; align-self: flex-start; color: #94A3B8; font-style: italic; font-size: 0.82rem; border: 1px solid #334155;';
            loadingBubble.innerHTML = '🤖 AW-1 Assistant is running multi-pass re-simulation...';
            hudStream.appendChild(loadingBubble);
            hudStream.scrollTop = hudStream.scrollHeight;

            try {
                const res = await fetch('/wisdom/api/v1/dialogue', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dossier_hash: window.activeDossierHash, user_query: query })
                });
                const data = await res.json();
                
                const loader = document.getElementById('aw-hud-loading');
                if (loader) loader.remove();

                const awBubble = document.createElement('div');
                awBubble.style.cssText = 'background: #0F172A; padding: 10px 12px; border-radius: 8px; align-self: flex-start; max-width: 90%; border-left: 4px solid #10B981; color: #f8fafc; font-size: 0.82rem; box-shadow: 0 4px 16px rgba(0,0,0,0.6);';
                
                const formattedText = (data.response_markdown || '').replace(/\n/g, '<br>');
                let htmlContent = `<strong style="color: #10B981; display: block; margin-bottom: 3px;">🤖 AW-1 Assistant</strong>${formattedText}`;
                
                if (data.citations && data.citations.length > 0) {
                    htmlContent += `<div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px;">`;
                    data.citations.forEach((cit, idx) => {
                        const citId = 'cit-' + Date.now() + '-' + idx;
                        window.hudCitations[citId] = cit;
                        htmlContent += `<button onclick="toggleStatuteDrawer('${citId}')" style="background: #030712; border: 1px solid #3B82F6; color: #60A5FA; font-size: 0.68rem; padding: 3px 6px; border-radius: 4px; cursor: pointer; font-weight: 700;">📜 ${cit.title}</button>`;
                    });
                    htmlContent += `</div><div id="statute-drawer" style="display: none; margin-top: 6px; background: #020408; border: 1px solid #334155; padding: 8px; border-radius: 6px; font-size: 0.75rem; color: #E2E8F0;"></div>`;
                }

                if (data.suggested_fix && data.action_label) {
                    window.latestSuggestedFix = data.suggested_fix;
                    htmlContent += `<div style="margin-top: 8px;"><button onclick="applySuggestedFix()" style="background: #D97706; color: #030712; border: none; padding: 6px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 900; cursor: pointer; box-shadow: 0 4px 12px rgba(217,119,6,0.6);">${data.action_label}</button></div>`;
                }

                awBubble.innerHTML = htmlContent;
                hudStream.appendChild(awBubble);
                hudStream.scrollTop = hudStream.scrollHeight;

            } catch (err) {
                const loader = document.getElementById('aw-hud-loading');
                if (loader) loader.remove();

                const errBubble = document.createElement('div');
                errBubble.style.cssText = 'background: #0F172A; padding: 8px 12px; border-radius: 8px; align-self: flex-start; color: #EF4444; font-size: 0.82rem; border: 1px solid #7F1D1D;';
                errBubble.textContent = 'Evaluation error occurred during dialogue simulation.';
                hudStream.appendChild(errBubble);
                hudStream.scrollTop = hudStream.scrollHeight;
            }
        }

        hudSendBtn.addEventListener('click', executeHudQuery);
        hudInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') executeHudQuery(); });

        window.applySuggestedFix = function() {
            var proposalInput = document.getElementById('proposal-textarea');
            if (proposalInput && window.latestSuggestedFix) {
                proposalInput.value = window.latestSuggestedFix;
                proposalInput.style.borderColor = '#10B981';
                setTimeout(() => proposalInput.style.borderColor = '#334155', 1500);
            }
        };

        modePills.forEach(pill => {
            pill.addEventListener('click', () => {
                modePills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                currentMode = pill.getAttribute('data-mode');
                
                const modeNames = { 
                    gospel: "System Restoration: The Gospel OS", 
                    investment: "Botswana Strategic Investment Report", 
                    village: "P20 Digital Village Ledger", 
                    tokenomics: "Digital Entrepreneurship & Tokenomics" 
                };
                const notifyMsg = document.createElement('div');
                notifyMsg.className = 'laveto-msg laveto-msg-bot';
                notifyMsg.style.fontStyle = 'italic';
                notifyMsg.textContent = `Switched notebook focus to: ${modeNames[currentMode]}. What would you like to explore?`;
                msgContainer.appendChild(notifyMsg);
                msgContainer.scrollTop = msgContainer.scrollHeight;
            });
        });

        async function handleSend() {
            const text = inputField.value.trim();
            if (!text) return;

            const userMsg = document.createElement('div');
            userMsg.className = 'laveto-msg laveto-msg-user';
            userMsg.textContent = text;
            msgContainer.appendChild(userMsg);
            inputField.value = '';
            msgContainer.scrollTop = msgContainer.scrollHeight;

            try {
                const res = await fetch('/wisdom/api/v1/support/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, chat_mode: currentMode })
                });

                const data = await res.json();
                const botMsg = document.createElement('div');
                botMsg.className = 'laveto-msg laveto-msg-bot';

                const replyText = data.reply || "Let's align that with our records.";
                const sourceCitation = data.signed_dossier?.source_citation || "Unified Knowledge Corpus";

                let linksHtml = '';
                if (data.suggested_files && data.suggested_files.length > 0) {
                    linksHtml = '<div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">';
                    data.suggested_files.forEach(link => {
                        linksHtml += `<a href="${link.url}" target="_blank" style="background: #059669; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">🔗 ${link.label}</a>`;
                    });
                    linksHtml += '</div>';
                }

                botMsg.innerHTML = `
                    ${replyText}
                    ${linksHtml}
                    <span class="laveto-dossier-tag">📚 Source: ${sourceCitation} [Notebook: ${currentMode.toUpperCase()}]</span>
                `;

                msgContainer.appendChild(botMsg);
                msgContainer.scrollTop = msgContainer.scrollHeight;

            } catch (err) {
                const botMsg = document.createElement('div');
                botMsg.className = 'laveto-msg laveto-msg-bot';
                botMsg.textContent = "I'm here with you. Let's keep working through that!";
                msgContainer.appendChild(botMsg);
                msgContainer.scrollTop = msgContainer.scrollHeight;
            }
        }

        sendBtn.addEventListener('click', handleSend);
        inputField.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
})();