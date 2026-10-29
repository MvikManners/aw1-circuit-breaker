from app import app, db

with app.app_context():
    print("🚨 Wiping old database structure...")
    db.drop_all()
    print("🏗️ Forging new SovereignLedger tables with Agent Bounty Engine...")
    db.create_all()
    print("✅ Database Reset Complete. Ready for Operation.")