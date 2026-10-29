import csv
import sys
from datetime import datetime

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")
if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED.")
    sys.exit()

# Laveto MAF - Sanctified Settlement Control v1.1
print("\n" + "="*45)
print("     LAVETO PTY LTD: SETTLEMENT HANDSHAKE     ")
print("="*45)

member_in = input("Enter Member Name: ").strip().lower()
repair_in = input("Enter Part/Repair (e.g. Bushings): ").strip().lower()

try:
    # 1. Verify Sanctification (Repairs File)
    repair_found = False
    repair_cost = 0.0
    member_full_name = ""
    
    with open('repairs.csv', mode='r') as r_file:
        r_reader = csv.DictReader(r_file)
        for row in r_reader:
            if member_in in row['Member'].lower() and repair_in in row['Part'].lower():
                repair_found = True
                repair_cost = float(row['Cost'].replace('P', ''))
                member_full_name = row['Member']
                break

    if not repair_found:
        print(f"❌ ERROR: No record found for '{repair_in}' under '{member_in}'.")
        sys.exit()

    # 2. Execute Financial Shield (Members List)
    members = []
    found_in_list = False
    with open('members_list.csv', mode='r') as m_file:
        reader = csv.DictReader(m_file)
        for row in reader:
            if row['Member Name'].lower() == member_full_name.lower():
                current_fund = float(row['Net Fund'].replace('P', ''))
                if current_fund < repair_cost:
                    print(f"🛑 HALT: Insufficient Funds. Wallet has P{current_fund:.2f}.")
                    sys.exit()
                
                # Deduct and Update
                new_fund = current_fund - repair_cost
                row['Net Fund'] = f"{new_fund:.2f}"
                found_in_list = True
                print(f"✅ TRIPLE-LOCK VERIFIED: P{repair_cost:.2f} released.")
                print(f"📉 {member_full_name}'s New Wallet: P{new_fund:.2f}")
            members.append(row)

    if found_in_list:
        # 3. Update Database
        with open('members_list.csv', mode='w', newline='') as m_file:
            writer = csv.DictWriter(m_file, fieldnames=members[0].keys())
            writer.writeheader()
            writer.writerows(members)
        
        # 4. Log Transaction for the Digital Passport
        with open('transactions.csv', mode='a', newline='') as t_file:
            t_writer = csv.writer(t_file)
            today = datetime.now().strftime("%Y-%m-%d")
            t_writer.writerow([today, member_full_name, "SETTLEMENT", repair_cost])
        
        print(f"🌟 PASSPORT UPDATED: Recovery of '{repair_in}' is now SETTLED.")
    else:
        print("❌ Member Name in repairs.csv does not match members_list.csv.")

except Exception as e:
    print(f"⚠️ System Error: {e}")
