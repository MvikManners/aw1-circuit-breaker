import json
import os

# LAVETO CONSOLIDATED ENGINE V2.3
DATA_FILE = "laveto_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

members = load_data()

def add_founder(seat_no, name, tier, model, deposit):
    """Merges maf_engine tiers with Alpha-20 Wealth tracking."""
    tiers = {
        "urban": {"monthly": 300, "mult": 3},
        "explorer": {"monthly": 750, "mult": 4},
        "titan": {"monthly": 1500, "mult": 5}
    }
    
    t = tier.lower()
    loan_limit = tiers[t]["monthly"] * tiers[t]["mult"]
    
    # The Sovereign v2.3 Wealth Split
    architect_yield = deposit * 0.20
    procurement_fund = deposit * 0.80

    members[str(seat_no)] = {
        "Name": name,
        "Tier": t.capitalize(),
        "Vehicle": model,
        "Deposit": deposit,
        "Architect_Yield": architect_yield,
        "Part_Fund": procurement_fund,
        "Loan_Limit": loan_limit,
        "Status": "ACTIVE"
    }
    
    save_data(members)
    print(f"--- SEAT #{seat_no} ACTIVATED ---")
    print(f"Tier: {t.capitalize()} | Loan Limit: P{loan_limit}")
    print(f"Architect Wealth: P{architect_yield}")

print("LAVETO MASTER ENGINE READY.")
