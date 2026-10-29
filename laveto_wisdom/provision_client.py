"""
Laveto Wisdom AW — B2B Enterprise Client Provisioning Utility.
Generates secure tokens, assigns rate-limit/quota tiers, and updates lvt_database.db.
"""
import sys
import secrets
import sqlite3
import argparse

DB_PATH = "/home/LavetoLab/lvt_backend/lvt_database.db"

TIERS = {
    "STANDARD": {"rate_limit": 60, "quota": 1000},
    "ENTERPRISE": {"rate_limit": 120, "quota": 5000},
    "UNLIMITED": {"rate_limit": 300, "quota": 50000}
}

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def provision_client(client_id: str, org_name: str, tier: str = "STANDARD"):
    tier = tier.upper()
    if tier not in TIERS:
        print(f"Error: Invalid tier '{tier}'. Choose from: {list(TIERS.keys())}")
        sys.exit(1)

    generated_key = f"lvt-sec-{secrets.token_hex(16)}"
    rate_limit = TIERS[tier]["rate_limit"]
    monthly_quota = TIERS[tier]["quota"]

    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO wisdom_api_clients
                (client_id, api_key, organization_name, tier, rate_limit_per_min, monthly_quota, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (client_id, generated_key, org_name, tier, rate_limit, monthly_quota))
        print("=================================================================")
        print("       LAVETO WISDOM AW — B2B CLIENT PROVISIONED SUCCESSFULLY   ")
        print("=================================================================")
        print(f"Client Identifier : {client_id}")
        print(f"Organization Name : {org_name}")
        print(f"Tier Allocated    : {tier}")
        print(f"Rate Limit (min)  : {rate_limit} req/min")
        print(f"Monthly Quota     : {monthly_quota} audits")
        print(f"API Secret Key    : {generated_key}")
        print("-----------------------------------------------------------------")
        print("Pass the token via the 'X-Laveto-Key' HTTP request header.")
        print("=================================================================")
    except Exception as e:
        print(f"Provisioning Failed: {e}")
    finally:
        conn.close()

def list_clients():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT client_id, organization_name, tier, rate_limit_per_min, monthly_quota, is_active, created_at FROM wisdom_api_clients ORDER BY created_at DESC"
        ).fetchall()
        print("=================================================================")
        print("                 REGISTERED B2B API CLIENTS                      ")
        print("=================================================================")
        for r in rows:
            status = "ACTIVE" if r["is_active"] else "DISABLED"
            print(f"[{status}] {r['client_id']} | {r['organization_name']} | Tier: {r['tier']} | Limit: {r['rate_limit_per_min']}/m | Quota: {r['monthly_quota']}/mo")
        print("=================================================================")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage B2B enterprise client tokens for Laveto Wisdom AW.")
    parser.add_argument("--provision", action="store_true", help="Provision a new enterprise client")
    parser.add_argument("--list", action="store_true", help="List registered API clients")
    parser.add_argument("--client_id", type=str, help="Unique slug identifier (e.g. org-ceda-fintech)")
    parser.add_argument("--org", type=str, help="Organization name (e.g. 'CEDA Risk Committee')")
    parser.add_argument("--tier", type=str, default="STANDARD", help="STANDARD, ENTERPRISE, or UNLIMITED")

    args = parser.parse_args()

    if args.provision:
        if not args.client_id or not args.org:
            print("Error: --client_id and --org are required to provision a client.")
            sys.exit(1)
        provision_client(args.client_id, args.org, args.tier)
    elif args.list:
        list_clients()
    else:
        parser.print_help()
