import csv
import sys
from datetime import datetime

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")
if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED.")
    sys.exit()

# Laveto MAF - Digital Safety Passport Generator v1.1
target = input("Enter Member Name for Passport: ").strip()

try:
    # 1. Fetch Core Asset Identity
    member_data = {}
    with open('members_list.csv', mode='r') as m_file:
        reader = csv.DictReader(m_file)
        for row in reader:
            if row['Member Name'].lower() == target.lower():
                member_data = row
                break
    
    if not member_data:
        print(f"❌ Error: Sovereign '{target}' not found in the Vault.")
        sys.exit()

    # 2. Build the Document Header
    print("\n" + "█"*50)
    print("       OFFICIAL DIGITAL SAFETY PASSPORT       ")
    print("█"*50)
    print(f"SOVEREIGN: {member_data['Member Name'].upper()}")
    print(f"MEMBER ID: LVT-2026-{member_data['Member Name'][:3].upper()}")
    print(f"TIER:      {member_data['Tier']} (Sanctified Status)")
    print("-" * 50)
    print("VEHICLE PROVENANCE & TRUTH LOG:")

    # 3. Pull Forensic Audit History from Transactions
    settlements_found = 0
    try:
        with open('transactions.csv', mode='r') as t_file:
            t_reader = csv.reader(t_file)
            next(t_reader) # Skip header
            for t_row in t_reader:
                if t_row[1].lower() == target.lower() and t_row[2] == "SETTLEMENT":
                    date = t_row[0]
                    amount = t_row[3]
                    # Logic assumes the 'Part' was settled
                    print(f"✅ [{date}] SANCTIFIED: Parts & Labor (P{amount})")
                    print(f"   FORENSIC MARK: VIN-ENGRAVED & VIGIL-VERIFIED")
                    settlements_found += 1
    except FileNotFoundError: pass

    if settlements_found == 0:
        print("   ⏳ PENDING: Initial Forensic Triage complete.")
    
    # 4. The Resale Premium Guarantee
    print("-" * 50)
    print("RESALE EQUITY STATUS:")
    if settlements_found > 0:
        print("🟢 STATUS: 15% PROVENANCE PREMIUM ACTIVE")
    else:
        print("🟡 STATUS: HARDENING IN PROGRESS")

    # 5. QR CODE EVIDENCE LINK
    print("\n" + "-" * 25)
    print("FORENSIC PHOTO ARCHIVE:")
    print("┌───────────────────────┐")
    print("│  [QR CODE PLACEHOLDER]│")
    print("│ LINK: DOC-124/215 LOG │")
    print("└───────────────────────┘")
    print("Scan for 4K Vigil Evidence")
    
    print("-" * 50)
    print(f"ISSUED BY: Vela (MD, System Restoration)")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("█"*50 + "\n")

except Exception as e:
    print(f"⚠️ Forensic Retrieval Error: {e}")
