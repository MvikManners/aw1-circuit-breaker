# --- 🛰️ SYSTEM TIMESTAMP: 2026-03-18 10:45 CAT ---
# --- 🏆 MODULE: SENTINEL-A ANTICIPATORY ENGINE (DOC 205) ---

import json
from datetime import datetime
from core.models.vehicles import SovereignLedger, GhostOrder, AccessLog
from app import db  # Assumes standard Laveto imports
from app import send_telegram_alert

class SentinelEngine:
    # THE GABORONE CONSTANT
    K_ENV = 1.4

    @staticmethod
    def calculate_failure_probability(current_km, last_restoration_km, oem_lifespan, trauma_delta, is_tier_1):
        """
        Executes Doc 205 Entropy Math.
        Punishes non-OEM 'Shark' parts by halving their lifespan (Integrity Multiplier).
        """
        km_driven = current_km - last_restoration_km
        integrity_multiplier = 1.0 if is_tier_1 else 0.5
        
        # The Entropy Formula
        pf = ((km_driven * SentinelEngine.K_ENV) + (trauma_delta * 10000)) / (oem_lifespan * integrity_multiplier)
        
        return min(max(pf, 0.0), 1.0)  # Constrain between 0% and 100%

    @staticmethod
    def evaluate_suspension_node(ledger_id, current_km, component_data):
        """
        Evaluates a specific component and triggers the Silk Road Data Bridge if necessary.
        component_data dict expects: {'name': str, 'last_km': int, 'lifespan': int, 'trauma': float, 'is_tier_1': bool, 'oem_number': str}
        """
        ledger = SovereignLedger.query.get(ledger_id)
        if not ledger:
            return

        pf = SentinelEngine.calculate_failure_probability(
            current_km, 
            component_data['last_km'], 
            component_data['lifespan'], 
            component_data['trauma'], 
            component_data['is_tier_1']
        )

        # 🟢 TIER I: SANCTIFIED
        if pf < 0.40:
            return {"status": "SANCTIFIED", "pf": pf}

        # 🟡 TIER II: THE HORIZON (Ghost Prep)
        elif 0.40 <= pf < 0.70:
            # Check if prep order already exists to prevent duplicates
            existing = GhostOrder.query.filter_by(ledger_id=ledger.id, component_name=component_data['name']).first()
            if not existing:
                ghost = GhostOrder(
                    ledger_id=ledger.id,
                    component_name=component_data['name'],
                    grade=3, # Warning Grade
                    oem_part_number=component_data['oem_number'],
                    status='PENDING PAYLOAD'
                )
                db.session.add(ghost)
                db.session.commit()
            return {"status": "WARNING", "pf": pf}

        # 🔴 TIER III: RED SOIL (Tactical Sourcing Triggered)
        else:
            # Generate the Procurement JSON Payload (Doc 205)
            payload = {
                "trigger_id": f"LVT-AUTO-{datetime.utcnow().strftime('%Y%m%d-%H%M')}",
                "vin_dna": ledger.vin_dna,
                "member_id": ledger.job_start_code,
                "nodes_required": [
                    {
                        "part_type": component_data['name'], 
                        "brand_mandate": "Lemförder" if component_data['is_tier_1'] else "OEM Strict"
                    }
                ],
                "anchor_price_target": "Retail_Price * 0.80",
                "priority": "RED_SOIL"
            }

            # Log the entropy and notify the Command Wall
            db.session.add(AccessLog(vin_dna=ledger.vin_dna, action=f"🔴 RED SOIL PREDICTION: {component_data['name']} at {pf*100:.1f}%"))
            db.session.commit()

            # Push notification to Architect's Pocket
            alert_msg = f"🔴 *RED SOIL TRIGGER*\n\nVIN: {ledger.vin_dna}\nNode: {component_data['name']}\nFailure Prob: {pf*100:.1f}%\n\nSilk Road payload automatically generated."
            send_telegram_alert(alert_msg)

            return {"status": "RED_SOIL", "pf": pf, "payload": json.dumps(payload, indent=2)}

    @staticmethod
    def scry_fluids(current_km, last_service_km):
        """
        The Fluid Gospel Logic. 
        Returns opacity multiplier (0.0 to 1.0) and triggers Anticipatory Ghost Order at 90%.
        """
        km_driven = current_km - last_service_km
        threshold = 7500
        
        fluid_opacity = min(km_driven / threshold, 1.0)
        
        if fluid_opacity >= 0.90:
            return {
                "status": "ANTICIPATORY_DISPATCH",
                "opacity": fluid_opacity,
                "nodes_required": ["Synthetic Grade Oil", "OEM Filter kit"]
            }
            
        return {"status": "STABLE", "opacity": fluid_opacity}

    @staticmethod
    def audit_sovereign_seal(ledger_id, days_to_expiry, yield_earned):
        """
        Checks Licensing Expiry and funds it via the Gospel Yield if within 30 days.
        """
        license_cost = 250.00 # Standard Gaborone Rate
        
        if days_to_expiry <= 30:
            if yield_earned >= license_cost:
                return "STATUS: FUNDED BY THE GOSPEL"
            else:
                return "STATUS: SUBSIDIZED BY THE GOSPEL (INSUFFICIENT YIELD)"
        
        return "STATUS: SEAL ACTIVE"