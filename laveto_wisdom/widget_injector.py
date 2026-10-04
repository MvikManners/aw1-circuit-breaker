"""
widget_injector.py - Non-invasive global response hook for Laveto Wisdom
Ensures both Gospel OS Gatekeeper (support_widget.js) and the Assurance Console HUD
(wisdom_drawer.js?v=20261003_unwrapped + dock) are injected into all outgoing HTML views.
"""
import re

WIDGET_BUTTON = """
<div id="aw-assurance-dock" style="position: fixed; bottom: 20px; left: 20px; z-index: 99998;">
    <button type="button" onclick="if(window.toggleInterrogationHUD){window.toggleInterrogationHUD();}else if(typeof toggleInterrogationHUD==='function'){toggleInterrogationHUD();}" 
            style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); color: #FBBF24; border: 1px solid #D97706; padding: 10px 18px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); transition: all 0.2s;"
            onmouseover="this.style.borderColor='#FBBF24'; this.style.transform='translateY(-2px)';" 
            onmouseout="this.style.borderColor='#D97706'; this.style.transform='translateY(0)';">
        <span style="font-size: 1.1rem;">🛡️</span> Assurance Console
    </button>
</div>
"""

SCRIPTS_SNIPPET = """
<script src="/wisdom/static/wisdom_drawer.js?v=20261003_unwrapped"></script>
<script src="/wisdom/static/support_widget.js?v=20260924_v19"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof injectInterrogationHUD === 'function') {
            injectInterrogationHUD();
        }
    });
</script>
"""

def register_widget_hook(bp):
    @bp.after_request
    def inject_widgets_globally(response):
        try:
            if response.status_code == 200 and response.data:
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type or not content_type:
                    html = response.get_data(as_text=True)
                    to_inject = ''

                    if 'aw-assurance-dock' not in html:
                        to_inject += WIDGET_BUTTON

                    if 'support_widget.js' not in html or 'wisdom_drawer.js?v=20261003_unwrapped' not in html:
                        to_inject += SCRIPTS_SNIPPET

                    if to_inject:
                        match = re.search(r'</body\s*>', html, re.IGNORECASE)
                        if match:
                            idx = match.start()
                            html = html[:idx] + '\n' + to_inject + '\n' + html[idx:]
                            response.set_data(html)
                            response.headers.pop('Content-Length', None)
                        elif '</html>' in html:
                            html = html.replace('</html>', f'{to_inject}\n</html>', 1)
                            response.set_data(html)
                            response.headers.pop('Content-Length', None)
        except Exception:
            pass
        return response
