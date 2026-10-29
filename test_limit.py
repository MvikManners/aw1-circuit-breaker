import csv

# Laveto MAF - Limit Tester 1.0
print("--- 🏛️ Database Value Check ---")
target = "Vela"

try:
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Member Name'].lower() == target.lower():
                print(f"MEMBER FOUND: {row['Member Name']}")
                print(f"TIER:        {row['Tier']}")
                print(f"NET FUND:    P{row['Net Fund']}")
                print(f"LOAN LIMIT:  P{row.get('Loan Limit', 'MISSING')}")
                break
except Exception as e:
    print(f"❌ Error reading file: {e}")
