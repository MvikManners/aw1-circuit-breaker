import random

def run_laveto_stress_test(total_assets, avg_deposit, base_fee, disaster_rate=0.2):
    """
    Simulates Laveto sustainability with:
    1. Fixed Maturity Anchor (P100-P200/month)
    2. Operational Fee (5% of the total pledge)
    3. Sourcing Margin (Wholesale parts spread)
    4. Architect Yield (25% cut of interest on loans)
    """
    treasury = 0
    fees_collected = 0
    sourcing_margin_total = 0
    architect_yield_total = 0
    
    # Constants
    WHOLESALE_DISCOUNT = 0.30
    ARCHITECT_INTEREST_CUT = 0.25
    LOAN_INTEREST_RATE = 0.12

    for i in range(total_assets):
        # Total Pledge = Base Anchor + Manual Deposit
        total_pledge = base_fee + avg_deposit
        
        # 1. 5% Operational Fee (Revenue Pillar 1)
        fee = total_pledge * 0.05
        fees_collected += fee
        net_pledge = total_pledge - fee
        
        # 2. Sourcing Margin (Revenue Pillar 2 - 40% probability)
        if random.random() < 0.4:
            sourcing_margin = (net_pledge * 0.2) * WHOLESALE_DISCOUNT
            sourcing_margin_total += sourcing_margin
            treasury += sourcing_margin
        
        # 3. Architect Yield (Revenue Pillar 3 - 30% probability)
        if random.random() < 0.3:
            interest_earned = net_pledge * LOAN_INTEREST_RATE
            yield_cut = interest_earned * ARCHITECT_INTEREST_CUT
            architect_yield_total += yield_cut
            treasury += yield_cut
            
        # 4. Stress/Disaster Logic
        if random.random() < disaster_rate:
            treasury -= (net_pledge * 2) 
        else:
            treasury += (net_pledge * 0.6)
            
    return {
        "final_treasury": treasury,
        "operational_fees": fees_collected,
        "sourcing_revenue": sourcing_margin_total,
        "architect_yield": architect_yield_total,
        "is_sustainable": treasury > 0
    }

# Run the test: Class B asset (P150 base fee) + P1000 deposit
results = run_laveto_stress_test(total_assets=500, avg_deposit=1000, base_fee=150, disaster_rate=0.2)

print("--- Laveto Gospel OS Sustainability Test (Maturity Enabled) ---")
print(f"Final Treasury Balance: P{results['final_treasury']:,.2f}")
print(f"Pillar 1 (5% Fees): P{results['operational_fees']:,.2f}")
print(f"Pillar 2 (Sourcing): P{results['sourcing_revenue']:,.2f}")
print(f"Pillar 3 (Architect Yield): P{results['architect_yield']:,.2f}")
print(f"System Sustainability: {'STABLE' if results['is_sustainable'] else 'CRITICAL FAILURE'}")