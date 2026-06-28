# Laveto MAF - Manual Account Aging Tool
from app import app, db, SovereignLedger

print("--- ⏳ Initiating Time Travel Protocol ---")

target_vin = "TEST-V001-A456HAB3"  # <--- PUT YOUR TEST VIN HERE

with app.app_context():
    try:
        # Find the test car in the SovereignLedger
        car = SovereignLedger.query.filter_by(vin_dna=target_vin).first()
        
        if car:
            print(f"ASSET FOUND: {car.vin_dna}")
            print(f"CURRENT MATURITY: {car.months_in_green} Months")
            
            # Manually bump the account past the 24-month Diamond Gate
            car.months_in_green = 25 
            db.session.commit()
            
            print("✅ OVERRIDE SUCCESSFUL: Asset maturity upgraded to 25 Months.")
        else:
            print(f"❌ ERROR: Could not find asset with VIN {target_vin}")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")