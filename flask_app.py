from flask import Flask, render_template, request, redirect, url_for, flash

# THE SIGNAL STATION IMPORT [cite: 2026-03-04]
from notifications import send_forensic_decree


from aw1.api_routes import compliance_bp
app = Flask(__name__)
app.secret_key = 'restoration_secret_key'

# --- 1. THE MAIN HANGAR (HOME) --- [cite: 2026-03-04]
@app.route('/')
def index():
    """Matches the 'index' endpoint in your HTML."""
    return render_template('index.html')

# --- 2. THE FOUNDER PORTAL --- [cite: 2026-03-04]
@app.route('/member-check', methods=['GET', 'POST'])
def member_check():
    access_granted = False
    results = []
    query = ""

    if request.method == 'POST':
        query = request.form.get('vin')
        key = request.form.get('fleet_key')

        # Test Logic for Sovereign Access [cite: 2026-03-04]
        if key == "MASTER123":
            access_granted = True
            results = [{
                'vin_dna': query,
                'sovereign_key': "SR-ALPHA-99",
                'diagnosis': "Suspension Sanctified - Phase 01 Complete",
                'shield_reservoir': 4000.00,
                'yield_engine': 6000.00,
                'drive_link': "https://drive.google.com"
            }]

    # Using 'member_view.html' as seen in your directory
    return render_template('member_view.html',
                           access_granted=access_granted,
                           results=results,
                           query=query,
                           maturity=25,
                           traffic={'color': '#C5A059', 'label': 'HARDENING', 'msg': 'Execute Phase 02 Protocols.'})

# --- 3. COMMAND ACCESS (ADMIN) --- [cite: 2026-03-04]
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "GospelOS2026":
            return "<h1>COMMAND ACCESS GRANTED</h1><p>Sovereign 500 Ledger: ACTIVE</p>"
        else:
            flash("ACCESS DENIED.")
            return redirect(url_for('admin_login'))
    return render_template('login.html')

# --- 4. SAFETY ROUTES (Prevents BuildErrors) --- [cite: 2026-03-04]
@app.route('/request-bridge/<vin>')
def request_bridge(vin):
    return f"Bridge Loan Audit initiated for VIN: {vin}"

@app.route('/charter')
def fetch_charter():
    return "<h1>SOVEREIGN CHARTER</h1><p>System Restoration Protocol Document.</p>"

    # 🚀 TEMPORARY CORE FORGE TRIGGER
@app.route('/forge_core')
def forge_core():
    try:
        db.create_all()
        return "✅ CORE FORGED: MySQL Tables Generated Successfully! You can now close this tab."
    except Exception as e:
        return f"🚨 ENGINE FAILURE: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
app.register_blueprint(compliance_bp)
