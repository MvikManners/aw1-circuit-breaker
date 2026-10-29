# ==========================================
# 🏦 LAVETO GOSPEL OS - YIELD ENGINE
# ==========================================
import os
from datetime import datetime
from sqlalchemy import text

# Import the Master Core (This triggers your secure .env override automatically)
from app import app, db 

# The Bank Math: Laveto earns 0.5% monthly interest off the master float
MONTHLY_YIELD_RATE = 0.005 

def execute_monthly_yield():
    print(f"[{datetime.now()}] ⚙️ IGNITING YIELD ENGINE...")

    # THE TIME LOCK: Only execute on the 1st day of the month
    if datetime.today().day != 1:
        print("⏸️ Time Lock Active: Today is not the 1st of the month. Going back to sleep.")
        return

    with app.app_context():
        try:
            # 1. Scan the Ledger: How much total fiat is sitting in the Shield Reservoir?
            # (We use raw SQL here to guarantee it finds your table flawlessly)
            float_query = text("SELECT SUM(shield_reservoir_fiat) FROM sovereign_ledger")
            total_float = db.session.execute(float_query).scalar() or 0.00

            if total_float <= 0:
                print("⏸️ Shield Reservoir is empty. No yield to harvest.")
                return

            # 2. Calculate Laveto's Profit
            laveto_profit = float(total_float) * MONTHLY_YIELD_RATE

            # 3. Route the Profit to the Laveto Treasury
            # (Assuming you have a 'treasury' table. If not, we will need to build it!)
            treasury_update = text("UPDATE treasury SET revenue_balance = revenue_balance + :profit")
            db.session.execute(treasury_update, {"profit": laveto_profit})

            # 4. Seal the Vault
            db.session.commit()
            print(f"✅ YIELD SECURED: P{laveto_profit:.2f} routed to Laveto Master Treasury.")
            print(f"📊 Total Master Float Generating Yield: P{total_float:.2f}")

        except Exception as e:
            db.session.rollback()
            print(f"🚨 CRITICAL FAULT IN YIELD ENGINE: {e}")

if __name__ == '__main__':
    execute_monthly_yield()