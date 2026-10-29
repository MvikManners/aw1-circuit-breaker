import csv
import sys

# --- 🔐 SECURITY GATE ---
ADMIN_PASS = "Laveto2026"
entry = input("Enter Admin Security Password: ")
if entry != ADMIN_PASS:
    print("❌ ACCESS DENIED.")
    sys.exit()
print("🔓 Access Granted...")

# Laveto MAF - Member Loyalty Statement v1.8 (Visual Edition)
target = input("Enter Member Name: ").strip()

try:
    member_info = {}
    with open('members_list.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Member Name'].lower() == target.lower():
                member_info = row
                break
    
    if not member_info:
        print(f"❌ Member '{target}' not found.")
    else:
        # 1. Calculate History
        total_loans, total_repayments = 0, 0
        try:
            with open('transactions.csv', mode='r') as file:
                t_reader = csv.DictReader(file)
                for t_row in t_reader:
                    if t_row['Member'].lower() == target.lower():
                        if t_row['Type'] == 'LOAN': total_loans += float(t_row['Amount'])
                        elif t_row['Type'] == 'REPAY': total_repayments += float(t_row['Amount'])
        except FileNotFoundError: pass
        
        current_debt = total_loans - total_repayments
        
        # 2. Financial Logic
        base_limit = float(member_info.get('Loan Limit', 1000))
        net_fund = float(member_info.get('Net Fund', 0))
        
        # BONUS PROGRESS LOGIC
        BONUS_TARGET = 250.0
        bonus = 200.0 if net_fund >= BONUS_TARGET else 0.0
        
        # Calculate Progress Bar (10 blocks total)
        progress = min(int((net_fund / BONUS_TARGET) * 10), 10)
        bar = "█" * progress + "░" * (10 - progress)
        percent = min(int((net_fund / BONUS_TARGET) * 100), 100)

        final_max = base_limit + bonus
        credit_left = final_max - current_debt

        print(f"\n==========================================")
        print(f"       OFFICIAL MEMBER STATEMENT          ")
        print(f"==========================================")
        print(f"NAME: {member_info['Member Name']} | TIER: {member_info['Tier']}")
        print(f"NET CONTRIBUTIONS:  P{net_fund:.2f}")
        print(f"------------------------------------------")
        print(f"LOYALTY BONUS PROGRESS:")
        print(f"[{bar}] {percent}%")
        if percent < 100:
            print(f"💡 Save P{BONUS_TARGET - net_fund:.2f} more to unlock your P200 bonus!")
        else:
            print(f"🌟 LOYALTY BONUS UNLOCKED (+P200.00)")
        print(f"------------------------------------------")
        print(f"TOTAL MAX LIMIT:    P{final_max:.2f}")
        print(f"- Outstanding Debt:  -P{current_debt:.2f}")
        print(f"- REMAINING CREDIT:   P{credit_left:.2f}")
        print(f"------------------------------------------")
        
        if credit_left <= 0:
            print("🛑 STATUS: LIMIT REACHED.")
        else:
            print("✅ STATUS: ELIGIBLE FOR RESTORATION")
        print(f"==========================================\n")

except Exception as e:
    print(f"⚠️ Error: {e}")
