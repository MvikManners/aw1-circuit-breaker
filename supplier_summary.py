import csv
import sys

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")
if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED.")
    sys.exit()

# Laveto MAF - Supplier Volume Summary v1.0
print("\n" + "="*50)
print("      SYSTEM RESTORATION: SUPPLIER VOLUME      ")
print("="*50)
print(f"{'SUPPLIER NAME':<25} | {'TOTAL SPEND'}")
print("-" * 50)

supplier_data = {}
total_empire_spend = 0.0

try:
    # 1. SCAN TRANSACTIONS FOR SETTLEMENTS
    with open('transactions.csv', mode='r') as file:
        reader = csv.reader(file)
        # Skip header if it exists
        header = next(reader)
        
        for row in reader:
            # We assume settlements are logged as: Date, Member, Type, Amount, Supplier
            # Since our basic log didn't have Supplier column yet, we'll look for 
            # 'SETTLEMENT' types and sum them by member for now, 
            # or update the logic to track who was paid.
            if len(row) >= 4 and row[2] == "SETTLEMENT":
                amount = float(row[3])
                # For this prototype, we assign the spend to our primary Tier-1
                # In v2.0, we will add a 'Supplier' column to transactions.csv
                wholesaler = "Masterparts / Goldwagen" 
                
                supplier_data[wholesaler] = supplier_data.get(wholesaler, 0.0) + amount
                total_empire_spend += amount

    for name, spend in supplier_data.items():
        print(f"{name:<25} | P{spend:>10.2f}")

    print("-" * 50)
    print(f"TOTAL SETTLED THIS MONTH:      P{total_empire_spend:.2f}")
    print(f"ESTIMATED MARGIN CAPTURED:     P{total_empire_spend * 0.22:.2f}") # Based on Doc 133
    print("="*50 + "\n")

except Exception as e:
    print(f"⚠️ Error: {e}")
