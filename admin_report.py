import sys

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")

if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED: Incorrect Credentials.")
    sys.exit()
print("🔓 Access Granted. Loading Dashboard...")
# ------------------------
import csv

# Laveto MAF - Smart Admin Dashboard v1.6 (Security Edition)
total_savings = 0
total_fees = 0
total_loans = 0
total_repairs = 0
total_repayments = 0
member_count = 0
SAFETY_LIMIT = 500.00  # Your "Emergency Reserve"

try:
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_savings += float(row['Net Fund'])
            total_fees += float(row['Laveto Fee'])
            member_count += 1

    with open('transactions.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Type'] == 'LOAN': 
                total_loans += float(row['Amount'])
            elif row['Type'] == 'REPAIR': 
                total_repairs += float(row['Amount'])
            elif row['Type'] == 'REPAY': 
                total_repayments += float(row['Amount'])
except FileNotFoundError: pass

live_cash = total_savings - total_loans - total_repairs + total_repayments

print("\n--- 🏛️ Laveto MAF Live Command Center v1.6 ---")
print(f"Total Members: {member_count} / 500")
print(f"Total Laveto Profit: P{total_fees:.2f}")
print(f"---")
print(f"Total Member Savings: P{total_savings:.2f}")
print(f"Active Loans:        -P{total_loans:.2f}")
print(f"Total Repair Costs:  -P{total_repairs:.2f}")
print(f"Total Repayments:    +P{total_repayments:.2f}")
print(f"LIVE CASH AVAILABLE:  P{live_cash:.2f}")
print("------------------------------------------")

# THE SAFETY SENSOR
if live_cash < SAFETY_LIMIT:
    print(f"⚠️  ALERT: RESTORATION FUND IS LOW (Below P{SAFETY_LIMIT})!")
    print("🛑 PAUSE ALL NEW LOANS until fund recovers.")
else:
    print("✅ FUND STATUS: Healthy. You are safe to approve repairs.")
print("------------------------------------------")
