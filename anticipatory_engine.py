import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import MemberAsset, SourcingQueue, db # Adjust import based on your app structure

# Configuration
GABORONE_STRESS_FACTOR = 1.4
BIG_10_OEM_LIFESPANS = {
    'Timing Belt': 100000,
    'Water Pump': 120000,
    'Spark Plugs': 80000,
    'Brake Pads': 50000,
    'Transmission Fluid': 60000,
    'Control Arm Bushings': 90000,
    'Shock Absorbers': 80000,
    'Wheel Bearings': 120000,
    'Alternator': 150000,
    'Fuel Pump': 150000
}
WARNING_THRESHOLD_KM = 10000

def run_anticipatory_scan():
    print(f"[{datetime.utcnow()}] 🛰️ INITIALIZING SENTINEL-A ANTICIPATORY ENGINE...")
    
    # Fetch all active fleet assets
    assets = MemberAsset.query.filter_by(status='ACTIVE').all()
    ghost_orders_generated = 0

    for asset in assets:
        if not asset.current_odometer:
            continue
            
        # The Sentinel Formula
        calculated_wear = asset.current_odometer * GABORONE_STRESS_FACTOR
        
        for component, oem_lifespan in BIG_10_OEM_LIFESPANS.items():
            # Check if component is approaching failure window
            if (oem_lifespan - calculated_wear) <= WARNING_THRESHOLD_KM:
                
                # Check if a ghost order already exists to prevent duplicates
                existing_order = SourcingQueue.query.filter_by(
                    vin_dna=asset.vin_dna, 
                    component_name=component,
                    status='PENDING ADMIN APPROVAL'
                ).first()
                
                if not existing_order:
                    # Generate Ghost Order
                    ghost_order = SourcingQueue(
                        vin_dna=asset.vin_dna,
                        component_name=component,
                        calculated_wear_km=calculated_wear
                    )
                    db.session.add(ghost_order)
                    ghost_orders_generated += 1
                    print(f"⚠️ PREDICTIVE FAILURE DETECTED: {asset.vin_dna} | {component} at {calculated_wear}km wear. Ghost Order forged.")

    if ghost_orders_generated > 0:
        db.session.commit()
        print(f"[{datetime.utcnow()}] ✅ SCAN COMPLETE. {ghost_orders_generated} Ghost Orders pushed to Sourcing Queue.")
    else:
        print(f"[{datetime.utcnow()}] ✅ SCAN COMPLETE. No immediate fleet threats detected.")

if __name__ == "__main__":
    # Ensure application context is loaded here if needed by Flask-SQLAlchemy
    run_anticipatory_scan()