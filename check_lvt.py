from app import app, db, SovereignLedger; from sqlalchemy import func; 
with app.app_context(): 
    print(f'TOTAL LVT: {db.session.query(func.sum(SovereignLedger.lvt_balance)).scalar()}')
