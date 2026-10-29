import time
from app import app, db, SovereignLedger, DispatchQueue, generate_decree_pdf, mail, Message

def run_dispatch_engine():
    print("🛰️ Sentinel Worker Engine Started...")
    
    # We use app_context to securely access the database
    with app.app_context():
        # Find all emails waiting to be sent
        pending_jobs = DispatchQueue.query.filter_by(status='PENDING').all()
        
        if not pending_jobs:
            print("✓ Queue is empty. Entering sleep state.")
            return

        print(f"📦 Found {len(pending_jobs)} pending dispatches. Engaging...")
        
        for job in pending_jobs:
            record = SovereignLedger.query.get(job.ledger_id)
            if record:
                try:
                    # 1. Generate the fresh PDF
                    path = generate_decree_pdf(record, is_update=True)
                    
                    # 2. Package the Email
                    msg = Message(f"GOSPEL OS: Audit Update - {record.vin_dna}", recipients=[record.member_email])
                    msg.body = "Vela here. Attached is your latest Sovereign Decree."
                    with app.open_resource(path) as fp:
                        msg.attach(f"Decree_Update_{record.vin_dna}.pdf", "application/pdf", fp.read())
                    
                    # 3. Send and mark as DONE
                    mail.send(msg)
                    job.status = 'SENT'
                    db.session.commit()
                    
                    print(f"✅ DELIVERED: {record.vin_dna}")
                    
                    # Pause for 2 seconds to avoid Gmail spam filters
                    time.sleep(2) 
                    
                except Exception as e:
                    job.status = 'FAILED'
                    db.session.commit()
                    print(f"❌ ERROR: {record.vin_dna} | {str(e)}")

        print("🏁 All queued dispatches completed.")

if __name__ == '__main__':
    run_dispatch_engine()