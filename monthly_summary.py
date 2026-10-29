import csv
import sys

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")
if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED.")
    sys.exit()

# Laveto MAF - Monthly Executive Summary v1.4
print("\n" + "="*55)
print("       SYSTEM RESTORATION: EXECUTIVE SUMMARY       ")
print("="*55)
print(f"{'MEMBER NAME':<18} | {'TIER':<8} | {'FUND':<8} | {'STATUS'}")
print("-" * 55)

BONUS_TARGET = 250.0
total_members, loyalty_stars, total_pool_value = 0, 0, 0.0

try:
    # 1. MEMBER AND FINANCIAL OVERVIEW
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name, tier = row['Member Name'], row['Tier']
            # Cleaning the 'P' and calculating total pool
            fund = float(row['Net Fund'].replace('P', ''))
            total_pool_value += fund
            status = "🌟 LOYALTY" if fund >= BONUS_TARGET else "⏳ Pending"
            if fund >= BONUS_TARGET: loyalty_stars += 1
            print(f"{name:<18} | {tier:<8} | P{fund:<7.2f} | {status}")
            total_members += 1

    # 2. ACTIVE REPAIR OVERVIEW
    print("-" * 55)
    print("🛠️  CURRENT ASSET RESTORATIONS:")
    repair_count, total_repair_cost = 0, 0.0
    try:
        with open('repairs.csv', mode='r') as r_file:
            r_reader = csv.DictReader(r_file)
            for r_row in r_reader:
                cost = float(r_row['Cost'].replace('P', ''))
                print(f"- {r_row['Member']}: {r_row['Part']} (P{cost:.2f})")
                total_repair_cost += cost
                repair_count += 1
    except FileNotFoundError: print("- No repair records found yet.")

    # 3. FINAL TOTALS
    print("-" * 55)
    print(f"Total Members Onboarded: {total_members} / 500")
    print(f"Loyalty Bonus Achievers: {loyalty_stars}")
    print(f"TOTAL POOL VALUE:        P{total_pool_value:.2f}")
    print(f"TOTAL REPAIR SPEND:     -P{total_repair_cost:.2f}")
    print("="*55 + "\n")

except Exception as e:
    print(f"⚠️ Error: {e}")
