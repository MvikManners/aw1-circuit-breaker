import csv

# Laveto MAF - Smart Admin Dashboard 1.4 (Final Version)
total_savings = 0
total_fees = 0
total_loans_issued = 0
total_repayments = 0
member_count = 0

# 1. Calculate Total Savings & Fees
try:
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_savings += float(row['Net Fund'])
            total_fees += float(row['Laveto Fee'])
            member_count += 1
except FileNotFoundError:
    pass

# 2. Track Loans AND Repayments
try:
    with open('transactions.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Type'] == 'LOAN':
                total_loans_issued += float(row['Amount'])
            elif row['Type'] == 'REPAY':
                total_repayments += float(row['Amount'])
except FileNotFoundError:
    pass

# The Final Math: Savings - Loans + Repayments
live_cash_pool = total_savings - total_loans_issued + total_repayments

print("\n--- 🏛️ Laveto MAF Live Command Center ---")
print(f"Total Members: {member_count} / 500")
print(f"Total Laveto Profit: P{total_fees:.2f}")
print(f"---")
print(f"Total Member Savings: P{total_savings:.2f}")
print(f"Total Active Loans:  -P{total_loans_issued:.2f}")
print(f"Total Repayments:    +P{total_repayments:.2f}")
print(f"LIVE CASH AVAILABLE:  P{live_cash_pool:.2f}")
print("------------------------------------------")
