import csv
import os

# Laveto MAF - Loan Repayment Tool 1.0
print("--- 💰 Laveto MAF Loan Repayment ---")

member = input("Enter Member Name: ")
amount = float(input("Enter Repayment Amount (Pula): "))

# 1. Record the Repayment
file_exists = os.path.isfile('transactions.csv')
with open('transactions.csv', mode='a', newline='') as t_file:
    writer = csv.writer(t_file)
    if not file_exists:
        writer.writerow(['Type', 'Member', 'Amount', 'Balance_After'])
    
    # We use 'REPAY' as the type so the Dashboard can find it
    writer.writerow(['REPAY', member, amount, "N/A"])

print(f"✅ Success! P{amount} repayment recorded for {member}.")
