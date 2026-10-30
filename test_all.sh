#!/bin/bash
PYTHONPATH=/home/LavetoLab /home/LavetoLab/lvt_backend/venv/bin/python /home/LavetoLab/run_all_system_tests.py

# ==============================================================================
# TEST: GATE 7 OUT-OF-BAND HARD CONTAINMENT (SENSORY DEFICIT & DPA INTERCEPTION)
# ==============================================================================
echo -e "
[1;34m[TEST][0m Testing Gate 7 Statutory Interception (/wisdom/api/v1/bank/arbitrate)..."

GATE7_HTTP_CODE=$(curl -s -o /tmp/gate7_resp.json -w "%{http_code}" -X POST https://p20.laveto.net/wisdom/api/v1/bank/arbitrate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "BW-ACC-98214-FNBB",
    "action": "EXTERNAL_WIRE",
    "amount_bwp": 25000.0,
    "auth_factors_claimed": ["VOICE_BIOMETRIC", "SECURITY_QUESTIONS"]
  }')

if [ "$GATE7_HTTP_CODE" -eq 403 ]; then
  echo -e "[1;32m✓ PASSED: Gate 7 Hard Containment active (HTTP 403 Forbidden - Sensory Deficit Halted)[0m"
  cat /tmp/gate7_resp.json | grep -o '"reason":"[^"]*"'
else
  echo -e "[1;31m✗ FAILED: Gate 7 failed to contain adversarial payload (HTTP $GATE7_HTTP_CODE)[0m"
  cat /tmp/gate7_resp.json
fi

# ==============================================================================
# TEST: SUITE 16 - SAM ALTMAN BANKING VOICE SPOOF DEFENSE HARNESS
# ==============================================================================
echo -e "
[1;34m[TEST 16/16][0m Executing test_bank_voice_fraud_defense.py..."
/home/LavetoLab/lvt_backend/venv/bin/python /home/LavetoLab/test_bank_voice_fraud_defense.py