#!/usr/bin/env python3
import sys
import os
import json
from crypto_engine import get_kms_provider, KEY_STORE

provider = get_kms_provider()

def list_officers():
    if not os.path.exists(KEY_STORE):
        print("No signatories registered.")
        return
    with open(KEY_STORE, "r", encoding="utf-8") as f:
        registry = json.load(f)

    print("\n" + "=" * 80)
    print(f"{'REGISTERED COMPLIANCE SIGNATORIES (KMS ENCLAVE PROTECTED)':^80}")
    print("=" * 80)
    header = f"{'Officer ID':<22} | {'Status':<8} | {'Limit (BWP)':>14} | {'KMS Mode':<10} | {'Name'}"
    print(header)
    print("-" * 80)
    for oid, d in registry.items():
        st = "ACTIVE" if d.get("active") else "REVOKED"
        lim = f"{d.get('spending_limit_bwp', 0.0):>14,.2f}"
        name = d.get("name", "N/A")
        mode = "ENCLAVE" if d.get("hsm_enclave_protected") else "LEGACY"
        print(f"{oid:<22} | {st:<8} | {lim} | {mode:<10} | {name}")
    print("=" * 80 + "\n")

def add_officer(officer_id: str, name: str, spending_limit: float):
    res = provider.onboard_signatory(officer_id, name, float(spending_limit))
    print(f"\nSUCCESS: Signatory '{officer_id}' onboarded into KMS Enclave.")
    print(f"  Name:           {res['name']}")
    print(f"  Spending Limit: {res['spending_limit_bwp']:,.2f} BWP")
    print(f"  Public Key:     {res['public_key_hex']}")
    print("  Private Key:    [SEALED INSIDE AES-256-GCM ENCLAVE - ZERO DISK EXPOSURE]")

def sign_dossier(officer_id: str, dossier_hash: str):
    sig = provider.sign_dossier(officer_id, dossier_hash)
    print(f"\nSIGNATURE FOR DOSSIER: {dossier_hash}")
    print(f"OFFICER:               {officer_id}")
    print(f"KMS ED25519 SIGNATURE: {sig}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("Usage:")
        print("  python3 manage_keys.py list")
        print("  python3 manage_keys.py add <OFFICER_ID> '<Full Name>' <LIMIT_BWP>")
        print("  python3 manage_keys.py sign <OFFICER_ID> <DOSSIER_HASH>")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "list":
        list_officers()
    elif cmd == "add" and len(sys.argv) >= 5:
        add_officer(sys.argv[2], sys.argv[3], float(sys.argv[4]))
    elif cmd == "sign" and len(sys.argv) >= 4:
        sign_dossier(sys.argv[2], sys.argv[3])
    else:
        print("Invalid arguments. Run with --help for command syntax.")
