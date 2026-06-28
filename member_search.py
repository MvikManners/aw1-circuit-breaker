import csv

# Laveto MAF - Member Search Tool 1.0
print("--- 🔍 Laveto MAF Member Lookup ---")
target_name = input("Enter Member Name to Search: ").strip().lower()

found = False
try:
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Member Name'].lower() == target_name:
                print(f"\n✅ Member Found!")
                print(f"---------------------------")
                print(f"Name:        {row['Member Name']}")
                print(f"Tier:        {row['Tier']}")
                print(f"Savings:     P{row['Monthly Savings']}")
                print(f"Loan Limit:  P{row.get('Loan Limit', 'N/A')}")
                print(f"Restoration: P{row['Net Fund']}")
                print(f"---------------------------")
                found = True
                break
    
    if not found:
        print(f"❌ No member found with the name '{target_name}'.")

except FileNotFoundError:
    print("⚠️ Error: No member list found. Please onboard members first.")
