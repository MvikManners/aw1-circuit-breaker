import csv
from datetime import datetime

# Laveto MAF - Monthly Summary Generator 1.0
total_savings = 0
total_fees = 0
total_loans = 0
total_repayments = 0
member_count = 0

# 1. Pull Data
try:
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_savings += float(row['Net Fund'])
            total_fees += float(row['Laveto Fee'])
            member_count += 1
except FileNotFoundError: pass

try:
    with open('transactions.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Type'] == 'LOAN': total_loans += float(row['Amount'])
            elif row['Type'] == 'REPAY': total_repayments += float(row['Amount'])
except FileNotFoundError: pass

live_cash = total_savings - total_loans + total_repayments
date_str = datetime.now().strftime("%B %Y")

# 2. Write the Report File
report_content = f"""
==========================================
   SYSTEM RESTORATION - MAF SUMMARY
        Report Date: {date_str}
==========================================

MEMBER STATS:
- Total Onboarded: {member_count} / 500
- Community Trust Level: Stable

FINANCIAL HEALTH:
- Total Restoration Pool: P{total_savings:.2f}
- Active Loans Out:      -P{total_loans:.2f}
- Total Repayments In:   +P{total_repayments:.2f}
------------------------------------------
NET CASH AVAILABLE:      P{live_cash:.2f}

MANAGEMENT:
- Laveto Profit (Fees):  P{total_fees:.2f}

Note: All idling money is currently working 
within the community for vehicle repairs.
==========================================
"""

with open('Monthly_Summary.txt', 'w') as f:
    f.write(report_content)

print("✅ Professional Summary Generated: Monthly_Summary.txt")
