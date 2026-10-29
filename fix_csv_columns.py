import csv
import os

# Laveto MAF - Structural Repair v2.0 (Ghost Buster Edition)
filename = 'members_list.csv'
temp_file = 'temp.csv'

try:
    with open(filename, 'r') as infile, open(temp_file, 'w', newline='') as outfile:
        # We read the file as it is
        reader = csv.DictReader(infile)
        
        # We define the 6 mandatory columns for System Restoration
        fieldnames = ['Member Name', 'Tier', 'Monthly Savings', 'Laveto Fee', 'Net Fund', 'Loan Limit']
        
        # 'extrasaction=ignore' tells Python to delete any "None" ghost fields it finds
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction='ignore')
        
        writer.writeheader()
        for row in reader:
            # If 'Loan Limit' is missing or empty, we set the Pioneer P1000 default
            if not row.get('Loan Limit'):
                row['Loan Limit'] = '1000'
            writer.writerow(row)

    os.replace(temp_file, filename)
    print("✅ DATABASE REPAIRED: Ghost fields removed and 'Loan Limit' column active.")

except Exception as e:
    print(f"❌ Repair Failed: {e}")
