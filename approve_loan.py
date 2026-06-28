import sys

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")

if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED: Incorrect Credentials.")
    sys.exit()
print("🔓 Access Granted. Initializing Loan Sequence...")
# ------------------------
import csv
import os

# Laveto MAF - Loan Approval & Auto-Logger 1.2
print("--- 💸 Laveto MAF Loan Approval ---")

member = input("Enter Member Name: ")
loan_amount = float(input("Enter Loan Amount (Pula): "))

# 1. Check Fund Health from Member List
total_available = 0
try:
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_available += float(row['Net Fund'])

    if loan_amount > total_available:
        print(f"❌ DENIED: Only P{total_available} available in the pool.")
    else:
        new_balance = total_available - loan_amount
        print(f"✅ APPROVED: P{loan_amount} issued to {member}.")
        
        # 2. Self-Healing Ledger (This builds the file if it's missing!)
        file_exists = os.path.isfile('transactions.csv')
        with open('transactions.csv', mode='a', newline='') as t_file:
            writer = csv.writer(t_file)
            if not file_exists:
                writer.writerow(['Type', 'Member', 'Amount', 'Balance_After'])
            writer.writerow(['LOAN', member, loan_amount, new_balance])
        print("📝 Transaction recorded in the ledger.")
            
except FileNotFoundError:
    print("⚠️ Error: No member data found. Add members first!")
