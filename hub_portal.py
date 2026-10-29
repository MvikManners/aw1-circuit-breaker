import os
import csv
import sys
import time

# --- CONFIGURATION ---
METADATA_DIR = "03_METADATA_DUMP"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_member_data(target_name):
    try:
        with open('members_list.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if target_name.lower() in row['Member Name'].lower():
                    return row
    except Exception: return None

def live_evidence_log(member_name):
    clear()
    print("="*60)
    print(f"            WING II: LIVE EVIDENCE LOG - {member_name.upper()}")
    print("="*60)
    print(f"{'FILE NAME':<40} | {'STATUS'}")
    print("-" * 60)
    
    # Ensure directory exists for the simulation
    if not os.path.exists(METADATA_DIR):
        os.makedirs(METADATA_DIR)
        # Create a dummy file for the first test
        with open(f"{METADATA_DIR}/B20-01-CNTRL_ARM-SANCTIFIED-230226.jpg", "w") as f: f.write("")

    files = os.listdir(METADATA_DIR)
    # Only show files relevant to this member's restoration (e.g., Beta 20 cohort)
    found = False
    for f in files:
        if "B20" in f: # Example: Beta 20 cohort filter
            status = "✅ VERIFIED" if "SANCTIFIED" in f else "🟡 PENDING"
            print(f"{f:<40} | {status}")
            found = True
    
    if not found:
        print(" [ ! ] No forensic evidence detected for this session.")
    
    print("-" * 60)
    print(" [SYTAX]: [ID]-[PART]-[STATUS]-[DATE].jpg")
    input("\nPress Enter to return to the Vault...")

def vault_wing(data):
    while True:
        clear()
        print("="*60)
        print("                WING II: THE SOVEREIGN VAULT           ")
        print("="*60)
        print(" 1. [🔗] Open Cloud Hangar Link")
        print(" 2. [🔍] View Live Evidence Log (Metadata)")
        print(" 3. RETURN TO DASHBOARD")
        print("-" * 60)
        choice = input("Select Action: ")
        if choice == '1':
            print(f"\n[🔗] DRIVE: https://drive.google.com/drive/folders/...")
            input("\nPress Enter to continue...")
        elif choice == '2':
            live_evidence_log(data['Member Name'])
        elif choice == '3':
            break

def main_menu():
    clear()
    print("="*60)
    print("           LAVETO PTY LTD: HUB LOGIN v1.9              ")
    print("="*60)
    member_in = input("Enter Member Name to Sync: ").strip()
    data = load_member_data(member_in)
    if not data: sys.exit()

    while True:
        clear()
        print("="*60)
        print(f"       LAVETO ONLINE HUB | SOVEREIGN: {data['Member Name'].upper()}       ")
        print("="*60)
        print(" 1. [🎥 MECHANICAL LAB]")
        print(" 2. [📂 THE VAULT]")
        print(" 3. EXIT PORTAL")
        print("-" * 60)
        choice = input("Select a Wing: ")
        if choice == '2': vault_wing(data)
        elif choice == '3': break

if __name__ == "__main__":
    main_menu()
