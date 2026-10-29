"""
MOBILE MONEY & BANKING OFF-RAMP SIMULATOR
"""
import sys
import os
for p in ['/home/LavetoLab', '/home/LavetoLab/laveto_wisdom', '/home/LavetoLab/lvt_backend']:
    if os.path.exists(p) and p not in sys.path: sys.path.insert(0, p)

from laveto_pay import LavetoPayEngine

def run():
    engine = LavetoPayEngine(540000.0)
    tiers = [
        {"tier": "Micro Node (Smartphone)", "node_id": "node-bw-gaborone-881", "awt": 90.0, "acc": "+26771882901"},
        {"tier": "Power Node (Desktop)", "node_id": "node-bw-francistown-204", "awt": 250.0, "acc": "+26772991042"},
        {"tier": "Ambassador (5% Ref)", "node_id": "node-bw-ambassador-707", "awt": 750.0, "acc": "+26773551109"}
    ]
    providers = ["ORANGE_MONEY", "MASCOM_MYZAKA", "BANK_EFT", "CARDLESS_ATM"]

    print("================================================================================")
    print("   📱 LAVETO WISDOM (AW-1) MOBILE MONEY & BANKING OFF-RAMP SIMULATOR")
    print("================================================================================")
    for t in tiers:
        print(f"👤 {t['tier']} [{t['node_id']}] -> Mined: {t['awt']} AWT (≈ BWP {t['awt']*2.50:.2f})")
        for pk in providers:
            r = engine.process_offramp_disbursement(t['node_id'], t['awt'], pk, t['acc'])
            pin_str = f" | PIN: {r['voucher_pin']}" if r['voucher_pin'] else ""
            print(f"     → [{r['provider']}] Net: BWP {r['net_bwp_disbursed']:.2f} | Ref: {r['disbursement_id']}{pin_str}")
        print("-" * 70)
    print(f"🏛️ REMAINING TREASURY RESERVE: BWP {engine.treasury_reserve_bwp:,.2f}")

if __name__ == '__main__':
    run()
