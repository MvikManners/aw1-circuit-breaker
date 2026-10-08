#!/bin/bash
PYTHONPATH=/home/LavetoLab /home/LavetoLab/lvt_backend/venv/bin/python /home/LavetoLab/run_all_system_tests.py

# ==============================================================================
# TEST: GATE 7 OUT-OF-BAND HARD CONTAINMENT & BOTSWANA DPA 2018 INTERCEPTION
# ==============================================================================
echo -e "\n\033[1;34m[TEST]\033[0m Testing Gate 7 Statutory Interception (/v1/aw/audit)..."

GATE7_PAYLOAD='{
  "agent_id": "copilot-crawler-agent-07",
  "tool_name": "EXFILTRATE_CITIZEN_RECORDS",
  "action_type": "DATABASE_EXPORT",
  "parameters": {
    "table": "botswana_citizen_registry",
    "filter": "district == '\''Gaborone'\''",
    "exported_omang_samples": ["771234519", "912345678"],
    "destination_url": "https://offshore-data-broker.com/api/v1/ingest",
    "protocol": "socket_connect"
  }
}'

GATE7_RESP=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST https://p20.laveto.net/v1/aw/audit \
  -H "Content-Type: application/json" \
  -H "X-Laveto-Key: lvt_live_enterprise_sec_key" \
  -d "$GATE7_PAYLOAD")

GATE7_BODY=$(echo "$GATE7_RESP" | sed -e '$d')
GATE7_CODE=$(echo "$GATE7_RESP" | tail -n1 | cut -d: -f2)

if [ "$GATE7_CODE" -eq 403 ] && echo "$GATE7_BODY" | grep -q "ERR_STATUTORY_DPA_PII_EXFILTRATION"; then
    echo -e "\033[1;32m✓ PASSED:\033[0m Gate 7 halted PII exfiltration out-of-band (HTTP 403 Forbidden)"
    echo -e "   • Statutory Law : Botswana Data Protection Act (DPA 2018/2021), Section 18"
    echo -e "   • Verdict       : CONTAINED_STATUTORY_HALT"
    echo -e "   • Dossier Seal  : $(echo "$GATE7_BODY" | grep -o '"sha256_hash":"[^"]*' | cut -d'"' -f4)"
else
    echo -e "\033[1;31m✗ FAILED:\033[0m Gate 7 failed to contain adversarial payload (HTTP $GATE7_CODE)"
    echo "$GATE7_BODY"
    exit 1
fi

# ==============================================================================
# TEST:

# ==============================================================================
# TEST: PILLAR 4 - PUBLIC TENDER & PPRA PROCUREMENT INTERLOCK VERIFICATION
# ==============================================================================
echo -e "\n\033[1;34m[TEST]\033[0m Testing Pillar 4 Procurement Interlock (/v1/aw/procurement/verify-bid)..."

# 1. Test Reserved Sector Violation (Should HALT with 400)
TENDER_FAIL_PAYLOAD='{
  "tender_ref": "PPRA-2026-HAULAGE-088",
  "bidder_name": "Offshore Logistics Transit Ltd",
  "sector": "haulage_and_trucking",
  "citizen_equity_pct": 30.0,
  "citizen_subcontract_pct": 20.0,
  "offshore_profit_share_pct": 80.0
}'

TENDER_FAIL_RESP=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST https://p20.laveto.net/v1/aw/procurement/verify-bid \
  -H "Content-Type: application/json" \
  -H "X-Laveto-Key: lvt_live_enterprise_sec_key" \
  -d "$TENDER_FAIL_PAYLOAD")

TENDER_FAIL_BODY=$(echo "$TENDER_FAIL_RESP" | sed -e '$d')
TENDER_FAIL_CODE=$(echo "$TENDER_FAIL_RESP" | tail -n1 | cut -d: -f2)

if [ "$TENDER_FAIL_CODE" -eq 400 ] && echo "$TENDER_FAIL_BODY" | grep -q "ERR_STATUTORY_RESERVED_SECTOR"; then
    echo -e "\033[1;32m✓ PASSED:\033[0m PPRA Scanner halted reserved-sector breach (HTTP 400 Bad Request)"
    echo -e "   • Violation     : ERR_STATUTORY_RESERVED_SECTOR (haulage_and_trucking)"
else
    echo -e "\033[1;31m✗ FAILED:\033[0m PPRA Scanner failed to halt reserved-sector breach (HTTP $TENDER_FAIL_CODE)"
    exit 1
fi

# 2. Test Compliant Bid (Should PASS with 200)
TENDER_OK_PAYLOAD='{
  "tender_ref": "PPRA-2026-SEZA-INFRA-012",
  "bidder_name": "Kgalagadi Infrastructure Consortium (Pty) Ltd",
  "sector": "civil_engineering_infrastructure",
  "citizen_equity_pct": 55.0,
  "citizen_subcontract_pct": 60.0,
  "offshore_profit_share_pct": 0.0
}'

TENDER_OK_RESP=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST https://p20.laveto.net/v1/aw/procurement/verify-bid \
  -H "Content-Type: application/json" \
  -H "X-Laveto-Key: lvt_live_enterprise_sec_key" \
  -d "$TENDER_OK_PAYLOAD")

TENDER_OK_BODY=$(echo "$TENDER_OK_RESP" | sed -e '$d')
TENDER_OK_CODE=$(echo "$TENDER_OK_RESP" | tail -n1 | cut -d: -f2)

if [ "$TENDER_OK_CODE" -eq 200 ] && echo "$TENDER_OK_BODY" | grep -q "CLEARED_PROCEED"; then
    echo -e "\033[1;32m✓ PASSED:\033[0m Compliant Tender Bid Cleared with Section 14.8 RFP Covenant (HTTP 200 OK)"
    echo -e "   • Effective CEE : $(echo "$TENDER_OK_BODY" | grep -o '"effective_cee_score_pct":[0-9.]*' | cut -d: -f2)%"
else
    echo -e "\033[1;31m✗ FAILED:\033[0m Compliant Tender Bid failed validation (HTTP $TENDER_OK_CODE)"
    exit 1
fi
