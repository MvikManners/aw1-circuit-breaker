import os
import sys
from sqlalchemy import text

# Map the path so it can find your main Flask application
sys.path.append('/home/LavetoLab')
from app import app

# DIRECT IMPORT FROM CORE: Matches your internal architecture
from core import db  

def execute_zero_state_protocol():
    with app.app_context():
        try:
            print("INITIATING SYSTEM ZERO-STATE PROTOCOL...")

            # 1. Disable Foreign Key Checks temporarily to prevent constraint blocks
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

            # 2. Define operational tables to wipe
            # EXCLUDED: user, users, system_config, system_settings, alembic_version, warden, supplier, hub_partners
            tables_to_wipe = [
                'access_log', 'access_logs', 'audit_log', 'flicker_alert',
                'forensic_evidence', 'ghost_order', 'liquidation_record',
                'lvt_order_book', 'payroll_mandate', 'priority_alert',
                'priority_alerts', 'prospect', 'silk_road_ledger',
                'silk_road_quote', 'sourcing_queue', 'sovereign_ledger',
                'sovereign_transaction', 'staggered_payout_queue',
                'stop_order_mandate', 'transaction_log', 'vault_transaction',
                'vault_transactions', 'treasury', 'corporate_treasury'
            ]

            # 3. Truncate each table (Deletes data AND resets auto-increment IDs to 1)
            for table in tables_to_wipe:
                print(f"-> Purging table and resetting IDs: {table}")
                db.session.execute(text(f"TRUNCATE TABLE {table};"))

            # 4. Re-enable Foreign Key Checks to restore database security
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

            db.session.commit()
            print("==================================================")
            print("SYSTEM ZERO-STATE ACHIEVED.")
            print("All operational data purged. IDs reset to 1.")
            print("System is ready for production deployment.")
            print("==================================================")

        except Exception as e:
            db.session.rollback()
            # Ensure foreign keys are turned back on even in the event of a failure
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            db.session.commit()
            print(f"🚨 CRITICAL FAILURE: {str(e)}")

if __name__ == "__main__":
    print("WARNING: This will PERMANENTLY DELETE all operational transactions, assets, and logs.")
    print("Your admin users, system settings, and warden configurations will remain intact.")
    
    # Security lock to prevent accidental execution
    confirmation = input("Type 'CONFIRM' to execute the wipe: ")
    
    if confirmation == 'CONFIRM':
        execute_zero_state_protocol()
    else:
        print("Protocol aborted. No data was modified.")