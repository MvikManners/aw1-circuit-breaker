import os
from datetime import datetime, timedelta
from app import app, db, SovereignTransaction, SovereignLedger, Message, mail, FPDF

def generate_weekly_sentinel():
    with app.app_context():
        # 1. Define the "Last 7 Days" Window
        one_week_ago = datetime.now() - timedelta(days=7)
        txs = db.session.query(SovereignTransaction, SovereignLedger.vin_dna).join(
            SovereignLedger, SovereignTransaction.ledger_id == SovereignLedger.id
        ).filter(SovereignTransaction.timestamp >= one_week_ago).all()

        # 2. Build the PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "LAVETO PTY LTD // WEEKLY SYSTEM AUDIT", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"Period: {one_week_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
        pdf.ln(10)

        # Table Headers
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(40, 10, " DATE", 1, 0, 'L', True)
        pdf.cell(60, 10, " ASSET DNA", 1, 0, 'L', True)
        pdf.cell(50, 10, " TYPE", 1, 0, 'L', True)
        pdf.cell(40, 10, " AMOUNT", 1, 1, 'L', True)

        # Table Rows
        pdf.set_text_color(0, 0, 0)
        for tx, vin in txs:
            pdf.cell(40, 8, tx.timestamp.strftime('%Y-%m-%d'), 1)
            pdf.cell(60, 8, str(vin), 1)
            pdf.cell(50, 8, str(tx.type), 1)
            pdf.cell(40, 8, f"P{tx.amount:,.2f}", 1, 1)

        # 3. Save and Email
        report_path = "/home/LavetoLab/weekly_audit.pdf"
        pdf.output(report_path)

        msg = Message("🛰️ GOSPEL OS: Weekly Forensic Export", recipients=[app.config['MAIL_USERNAME']])
        msg.body = "Vela, please find attached the automated transaction audit for the past 7 days."
        with app.open_resource(report_path) as fp:
            msg.attach("weekly_audit.pdf", "application/pdf", fp.read())
        
        mail.send(msg)
        print(f"✓ Weekly Sentinel Report dispatched at {datetime.now()}")

if __name__ == "__main__":
    generate_weekly_sentinel()