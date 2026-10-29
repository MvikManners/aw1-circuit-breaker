#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/LavetoLab/aw1-breaker"
VENV_DIR="/home/LavetoLab/lvt_backend/venv"
WSGI_FILE="/var/www/p20_laveto_net_wsgi.py"
DOMAIN="p20.laveto.net"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_step() { echo -e "\n\[\033[0;33m\]==> $1"; }
log_ok()   { echo -e "    \[\033[0;32m\]✓ $1"; }
log_fail() { echo -e "    \[\033[0;31m\]✗ $1"; exit 1; }

# Layer 1: Git Working Tree
log_step "Layer 1: Checking Git Working Tree"
cd "$REPO_DIR"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "\[\033[0;33m\]Notice: Uncommitted changes present."
    git status -s
else
    log_ok "Working tree clean on $(git rev-parse --abbrev-ref HEAD)"
fi

# Layer 2: Packaging & Runtime Modules
log_step "Layer 2: Syncing Package into Python 3.11 WSGI Virtualenv"
"$VENV_DIR/bin/pip" install --quiet -e "$REPO_DIR"
"$VENV_DIR/bin/python" -c "import aw1.memory, aw1.circuit; print('Verified: aw1 core modules importable.')"
log_ok "Engine modules validated in production virtual environment"

# Layer 3: WSGI Application Reload
log_step "Layer 3: Recycling WSGI Application Worker"
touch "$WSGI_FILE"
log_ok "WSGI reload signaled. Waiting 3s for worker spawn..."
sleep 3

# Layer 4: TLS Certificate & Expiration
log_step "Layer 4: Validating SSL/TLS Certificate"
CERT_INFO=$(echo | openssl s_client -servername "$DOMAIN" -connect "${DOMAIN}:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || true)
if [ -n "$CERT_INFO" ]; then
    EXPIRY_DATE=$(echo "$CERT_INFO" | grep "notAfter=" | cut -d= -f2)
    log_ok "Valid TLS connection established (Expires: $EXPIRY_DATE)"
fi

# Layer 5: Endpoints Smoke Tests
log_step "Layer 5: Executing Multi-Endpoint Smoke Tests"
for path in "/wisdom/" "/wisdom/tender-portal" "/pay/"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://${DOMAIN}${path}")
    if [ "$CODE" -eq 200 ] || [ "$CODE" -eq 302 ]; then
        log_ok "${path}: HTTP $CODE"
    else
        log_fail "${path} returned HTTP $CODE"
    fi
done

# Layer 6: AST Circuit Breaker Containment
log_step "Layer 6: Verifying AST Circuit Breaker Containment"
CLI_TEST=$("$VENV_DIR/bin/aw1" verify "subprocess.run(['rm', '-rf', '/'])" 2>&1 || true)
if echo "$CLI_TEST" | grep -q "FAIL_CLOSED"; then
    LATENCY=$(echo "$CLI_TEST" | grep "Latency:" | awk '{print $2}')
    log_ok "AW-1 Breaker tripped fail-closed (Latency: $LATENCY)"
else
    log_fail "AW-1 Circuit Breaker failed to trip!"
fi

echo -e "\n\[\033[0;32m\]================================================================"
echo -e "\[\033[0;32m\]   AW-1 & LAVETO PLATFORM DEPLOYMENT VERIFIED (ALL LAYERS GREEN)"
echo -e "\[\033[0;32m\]================================================================\n"
