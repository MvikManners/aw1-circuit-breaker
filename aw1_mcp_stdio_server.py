#!/usr/bin/env python3
import sys
import os
import json
import copy
import secrets
import pymysql

sys.path.insert(0, "/home/LavetoLab/aw1-breaker")
from aw1.mcp_proxy import AW1MCPInterceptor
from iso20022_engine import generate_pacs008_xml

interceptor = AW1MCPInterceptor(baseline_velocity=50000.0)

from aw1_governor import AW1ProductionGovernor

aw1_governor = AW1ProductionGovernor(
    max_burst_per_sec=10,
    min_inter_call_ms=50,
    variance_threshold=0.25
)
DB_CONFIG_PATH = "/home/LavetoLab/aw1-breaker/db_config.json"
ISO_MSG_DIR = "/home/LavetoLab/aw1-breaker/iso20022_messages"
os.makedirs(ISO_MSG_DIR, exist_ok=True)

def get_db_connection():
    with open(DB_CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return pymysql.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg.get("port", 3306),
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor
    )

def load_sovereign_trust_anchors():
    """Hydrate active fiduciary trust anchors from MySQL root store."""
    try:
        from cryptography.hazmat.primitives import serialization
        import base64
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT key_id, spki_pubkey_b64, sha256_fingerprint 
                FROM sovereign_trust_anchors 
                WHERE is_revoked = FALSE;
            """)
            rows = cur.fetchall()
            for r in rows:
                spki_bytes = base64.b64decode(r["spki_pubkey_b64"])
                pub_obj = serialization.load_der_public_key(spki_bytes)
                aw1_governor.fiduciary_pubkeys[r["key_id"]] = pub_obj
        conn.close()
    except Exception as e:
        sys.stderr.write(f"[WARN] Failed to bootstrap trust anchors: {e}\n")

load_sovereign_trust_anchors()

AVAILABLE_TOOLS = [
    {
        "name": "sql_query",
        "description": "Execute read-only SQL queries against the ledger and merchant database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute (read-only SELECT statements only)."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "treasury_transfer",
        "description": "Disburse domestic BWP funds from the statutory reserve vault to a recipient account.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Amount in BWP to transfer."
                },
                "recipient": {
                    "type": "string",
                    "description": "Recipient account ID (e.g., BW-ACC-9921)."
                }
            },
            "required": ["amount", "recipient"]
        }
    },
    {
        "name": "cross_border_transfer",
        "description": "Disburse cross-border funds with real-time central bank FX rate conversion and ISO 20022 pacs.008 message orchestration.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Disbursement amount in source currency."
                },
                "source_currency": {
                    "type": "string",
                    "enum": ["BWP", "USD", "ZAR"],
                    "description": "Source currency pool (BWP, USD, ZAR)."
                },
                "target_currency": {
                    "type": "string",
                    "enum": ["BWP", "USD", "ZAR"],
                    "description": "Target settlement currency."
                },
                "recipient": {
                    "type": "string",
                    "description": "Beneficiary account identifier."
                }
            },
            "required": ["amount", "source_currency", "target_currency", "recipient"]
        }
    }
]

def execute_tool(request: dict, execution_token: str = None, dossier_hash: str = None) -> dict:
    req_id = request.get("id")
    params = request.get("params", {})
    tool_name = params.get("name")
    args = params.get("arguments", {})

    if not execution_token:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32001, "message": "UNAUTHORIZED_EXECUTION: Missing execution token from circuit breaker."}
        }

    if tool_name == "sql_query":
        query = args.get("query", "").strip()
        first_word = query.split()[0].upper() if query else ""
        if first_word not in ("SELECT", "SHOW", "EXPLAIN", "DESCRIBE"):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32002, "message": "FORBIDDEN_SQL: Only read-only queries are permitted on this socket."}
            }
        conn = None
        try:
            conn = get_db_connection()
            conn.autocommit(True)
            with conn.cursor() as cur:
                cur.execute("SET SESSION wait_timeout = 5;")
                cur.execute("SET SESSION lock_wait_timeout = 3;")
                cur.execute(query)
                rows = cur.fetchall()
            output_str = json.dumps(rows, indent=2, default=str) if rows else "Query completed: 0 rows returned."
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": f"Token [{execution_token[:12]}...] Live MySQL Ledger Result:\n{output_str}"}]}
            }
        except Exception as err:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": f"MySQL Query Error: {str(err)}"}]}
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    elif tool_name == "treasury_transfer":
        amount = float(args.get("amount", 0.0))
        recipient = str(args.get("recipient", "")).strip()
        source = "STATUTORY_RESERVE_VAULT"

        if amount <= 0:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32003, "message": "INVALID_AMOUNT: Amount must be greater than 0 BWP."}
            }

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (source,))
                source_row = cur.fetchone()
                if not source_row or float(source_row["balance_bwp"]) < amount:
                    conn.rollback()
                    conn.close()
                    avail = float(source_row["balance_bwp"]) if source_row else 0.0
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32004, "message": f"INSUFFICIENT_FUNDS: Vault balance ({avail:,.2f} BWP) insufficient for {amount:,.2f} BWP."}
                    }

                cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s WHERE account_id = %s;", (amount, source))
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (recipient,))
                if cur.fetchone() is None:
                    cur.execute(
                        "INSERT INTO accounts (account_id, account_name, balance_bwp, currency) VALUES (%s, %s, %s, 'BWP');",
                        (recipient, f"Account {recipient}", amount)
                    )
                else:
                    cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s WHERE account_id = %s;", (amount, recipient))

                cur.execute("""
                    INSERT INTO ledger_entries (source_account, destination_account, amount_bwp, execution_token, dossier_hash)
                    VALUES (%s, %s, %s, %s, %s);
                """, (source, recipient, amount, execution_token, dossier_hash))
                entry_id = cur.lastrowid

                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s;", (source,))
                new_vault = float(cur.fetchone()["balance_bwp"])
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s;", (recipient,))
                new_rec = float(cur.fetchone()["balance_bwp"])

                conn.commit()
            conn.close()

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": (
                            f"SETTLEMENT_CONFIRMED (MySQL InnoDB): Disbursed {amount:,.2f} BWP to {recipient}.\n"
                            f"Ledger Entry: #{entry_id} | Token: {execution_token}\n"
                            f"Vault Balance: {new_vault:,.2f} BWP | Recipient Balance: {new_rec:,.2f} BWP"
                        )
                    }]
                }
            }
        except Exception as err:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32005, "message": f"LEDGER_SETTLEMENT_FAILED: {str(err)}"}
            }

    elif tool_name == "cross_border_transfer":
        amount = float(args.get("amount", 0.0))
        src_ccy = str(args.get("source_currency", "BWP")).upper()
        tgt_ccy = str(args.get("target_currency", "USD")).upper()
        recipient = str(args.get("recipient", "")).strip()

        if amount <= 0:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32006, "message": "INVALID_AMOUNT: Amount must be greater than zero."}
            }

        source_acc = "STATUTORY_RESERVE_VAULT" if src_ccy == "BWP" else f"STATUTORY_RESERVE_{src_ccy}"

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # 1. Row-lock source reserve pool
                cur.execute("SELECT balance_bwp, currency FROM accounts WHERE account_id = %s FOR UPDATE;", (source_acc,))
                src_row = cur.fetchone()
                if not src_row or float(src_row["balance_bwp"]) < amount:
                    conn.rollback()
                    conn.close()
                    avail = float(src_row["balance_bwp"]) if src_row else 0.0
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32007, "message": f"INSUFFICIENT_POOL: Escrow vault {source_acc} ({avail:,.2f} {src_ccy}) insufficient for {amount:,.2f} {src_ccy}."}
                    }

                # 2. Determine conversion rate
                if src_ccy == tgt_ccy:
                    fx_rate = 1.0
                    settlement_amount = amount
                else:
                    pair = f"{src_ccy}/{tgt_ccy}"
                    cur.execute("SELECT rate FROM fx_rates WHERE pair = %s;", (pair,))
                    fx_row = cur.fetchone()
                    if not fx_row:
                        conn.rollback()
                        conn.close()
                        return {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {"code": -32008, "message": f"UNSUPPORTED_FX_PAIR: Currency pair {pair} not registered in statutory pricing table."}
                        }
                    fx_rate = float(fx_row["rate"])
                    settlement_amount = round(amount * fx_rate, 2)

                # 3. Debit source reserve
                cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s WHERE account_id = %s;", (amount, source_acc))

                # If cross-currency, maintain 1:1 conservation via FX clearing contra account
                if src_ccy != tgt_ccy:
                    contra_acc = f"FX_CLEARING_{src_ccy}"
                    cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (contra_acc,))
                    if cur.fetchone() is None:
                        cur.execute(
                            "INSERT INTO accounts (account_id, account_name, balance_bwp, currency) VALUES (%s, %s, %s, %s);",
                            (contra_acc, f"Statutory FX Clearing Reserve {src_ccy}", amount, src_ccy)
                        )
                    else:
                        cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s WHERE account_id = %s;", (amount, contra_acc))

                    tgt_source_acc = "STATUTORY_RESERVE_VAULT" if tgt_ccy == "BWP" else f"STATUTORY_RESERVE_{tgt_ccy}"
                    cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s WHERE account_id = %s;", (settlement_amount, tgt_source_acc))

                # 4. Credit recipient account
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (recipient,))
                if cur.fetchone() is None:
                    cur.execute(
                        "INSERT INTO accounts (account_id, account_name, balance_bwp, currency) VALUES (%s, %s, %s, %s);",
                        (recipient, f"Cross-Border {recipient}", settlement_amount, tgt_ccy)
                    )
                else:
                    cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s WHERE account_id = %s;", (settlement_amount, recipient))

                # 5. Commit ledger journal entry
                cur.execute("""
                    INSERT INTO ledger_entries (source_account, destination_account, amount_bwp, execution_token, dossier_hash)
                    VALUES (%s, %s, %s, %s, %s);
                """, (source_acc, recipient, amount, execution_token, dossier_hash))
                entry_id = cur.lastrowid

                # 6. Generate and persist ISO 20022 pacs.008 XML
                msg_id = f"MSG-{secrets.token_hex(6).upper()}"
                instr_id = f"INST-{secrets.token_hex(4).upper()}"
                e2e_id = f"E2E-{entry_id:06d}"
                dossier_bind = f"AW1-XBORDER-{execution_token}"

                xml_data = generate_pacs008_xml(
                    msg_id=msg_id,
                    end_to_end_id=e2e_id,
                    amount=settlement_amount,
                    source_currency=tgt_ccy,
                    recipient=recipient
                )

                xml_filename = f"{msg_id}.xml"
                xml_filepath = os.path.join(ISO_MSG_DIR, xml_filename)
                with open(xml_filepath, "w", encoding="utf-8") as xf:
                    xf.write(xml_data)

                # Persist active V5 ISO 20022 artifact to audit log
                with conn.cursor() as audit_cur:
                    audit_cur.execute("""
                        INSERT INTO iso20022_audit_log (
                            entry_id, execution_token, message_id, message_type,
                            version, status, key_fingerprint, xml_payload, created_at
                        ) VALUES (%s, %s, %s, %s, 5, 'ACTIVE', %s, %s, NOW());
                    """, (
                        entry_id, execution_token, msg_id, 'pacs.008.001.10',
                        'bfc66641c7acfa670ae61997459cceb15b56defe493811d98589aeb7e322e683',
                        xml_data
                    ))

                conn.commit()
            conn.close()

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": (
                            f"CROSS_BORDER_CONFIRMED: Disbursed {amount:,.2f} {src_ccy} -> {settlement_amount:,.2f} {tgt_ccy} to {recipient}.\n"
                            f"FX Rate Applied: {fx_rate:.6f} ({src_ccy}/{tgt_ccy})\n"
                            f"Ledger Entry: #{entry_id} | Token: {execution_token}\n"
                            f"ISO 20022 Transmission: pacs.008.001.10 ({xml_filename}) bound to ledger proof."
                        )
                    }]
                }
            }
        except Exception as err:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32009, "message": f"CROSS_BORDER_SETTLEMENT_FAILED: {str(err)}"}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {"content": [{"type": "text", "text": f"Executed {tool_name} with token {execution_token}"}]}
    }

def handle_request(request: dict) -> dict:
    req_id = request.get("id")
    method = request.get("method")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "aw1-circuit-breaker", "version": "1.0.4"}
            }
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": AVAILABLE_TOOLS}
        }

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        caller_id = args.get("caller_id", "mcp-agent-session")

        # --- AW-1 OUT-OF-BAND GOVERNOR GATEWAY INTERCEPTION ---
        gov_verdict = aw1_governor.evaluate_request(
            agent_id=caller_id,
            tool_name=tool_name or "unknown",
            payload=args
        )
        if not gov_verdict["execution_permitted"]:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32003,
                    "message": f"AW-1 EXECUTION HALTED: {gov_verdict['reason']} | {gov_verdict['detail']} (Dossier: {gov_verdict['dossier']['dossier_id']})",
                    "data": gov_verdict
                }
            }
        # ------------------------------------------------------

        if tool_name == "cross_border_transfer":
            args = params.get("arguments", {})
            amt = float(args.get("amount", 0.0))
            src = str(args.get("source_currency", "BWP")).upper()

            factor = 1.0
            if src == "USD":
                factor = 13.605442
            elif src == "ZAR":
                factor = 0.743494
            bwp_norm = round(amt * factor, 2)

            intercept_req = copy.deepcopy(request)
            intercept_req["params"]["arguments"]["amount"] = bwp_norm

        gov_token = gov_verdict.get("execution_token")
        raw_hash = gov_verdict.get("dossier", {}).get("sha256_dossier_hash", "")
        clean_dossier_hash = raw_hash.replace("0x", "").strip().lower() if raw_hash else None

        if tool_name == "cross_border_transfer":
            args = params.get("arguments", {})
            amt = float(args.get("amount", 0.0))
            src = str(args.get("source_currency", "BWP")).upper()

            factor = 1.0
            if src == "USD":
                factor = 13.605442
            elif src == "ZAR":
                factor = 0.743494
            bwp_norm = round(amt * factor, 2)

            intercept_req = copy.deepcopy(request)
            intercept_req["params"]["arguments"]["amount"] = bwp_norm

            def cb_wrapper(req, execution_token=None):
                active_token = gov_token or execution_token
                return execute_tool(request, execution_token=active_token, dossier_hash=clean_dossier_hash)

            return interceptor.intercept_mcp_request(intercept_req, execution_handler=cb_wrapper)

        def generic_cb_wrapper(req, execution_token=None):
            active_token = gov_token or execution_token
            return execute_tool(request, execution_token=active_token, dossier_hash=clean_dossier_hash)

        return interceptor.intercept_mcp_request(request, execution_handler=generic_cb_wrapper)

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found."}
    }

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as err:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(err)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
