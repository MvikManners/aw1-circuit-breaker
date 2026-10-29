import csv
import os

# Laveto MAF - Repair & Parts Tracker 1.0
print("--- 🔧 Laveto MAF Repair Tracker ---")

member = input("Enter Member Name: ")
part_fixed = input("Enter Part Replaced (e.g., Control Arm): ")
cost = float(input("Enter Total Cost (Pula): "))

# 1. Record the Mechanical Detail
file_exists = os.path.isfile('repairs.csv')
with open('repairs.csv', mode='a', newline='') as r_file:
    writer = csv.writer(r_file)
    if not file_exists:
        writer.writerow(['Member', 'Part', 'Cost'])
    writer.writerow([member, part_fixed, cost])

# 2. Record the Financial Deduction
with open('transactions.csv', mode='a', newline='') as t_file:
    writer = csv.writer(t_file)
    writer.writerow(['REPAIR', member, cost, "N/A"])

print(f"✅ Success! {part_fixed} for {member} recorded and funded.")
