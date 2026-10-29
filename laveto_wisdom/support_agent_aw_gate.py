"""
===================================================================================
LAVETO WISDOM (AW-1) — AI CUSTOMER SUPPORT AGENT & OUT-OF-BAND AW GATEWAY
===================================================================================
Module: support_agent_aw_gate.py
Purpose: Connects a conversational AI support assistant (e.g. Gemini Spark) to
         the Laveto Wisdom (AW-1) out-of-band audit layer (/v1/aw/audit).
         Interceptors prevent prompt injections, unauthorized token grants, and
         database exfiltration while safely processing legitimate user actions
         (BWP mobile cash-outs, node status checks, referral link queries).
===================================================================================
"""

import json
import hashlib
import time
from datetime import datetime, timezone

class CustomerSupportLLMFrontEnd:
    """
    Simulates the Front-of-House Conversational AI Support Assistant.
    Translates user chat messages into structured intent & proposed tool-call actions.
    """
    def parse_user_intent(self, user_message: str, user_session: dict) -> dict:
        msg_lower = user_message.lower()

        # 1. Detect malicious prompt injection / jailbreak attempts
        if "override" in msg_lower or "dump" in msg_lower or "shell" in msg_lower or "give me 1000" in msg_lower:
            return {
                "intent": "MALICIOUS_PROMPT_INJECTION_OR_EXPLOIT",
                "proposed_action": "EXECUTE_SYSTEM_SHELL",
                "target_resource": "production-database-cluster",
                "payload": {
                    "raw_input": user_message,
                    "escalate_privilege": True,
                    "dump_db_tables": ["citizens_pii", "tokenomics_ledger"]
                },
                "is_irreversible": True,
                "user_response_template": "Attempting privileged system override..."
            }

        # 2. Detect BWP Mobile Money Cash-Out Request
        elif "cash out" in msg_lower or "orange money" in msg_lower or "myzaka" in msg_lower or "withdraw" in msg_lower:
            return {
                "intent": "REQUEST_BWP_CASHOUT",
                "proposed_action": "PROCESS_BWP_CASHOUT",
                "target_resource": "laveto_pay_gateway",
                "payload": {
                    "user_id": user_session.get("user_id", "node-bw-citizen-001"),
                    "phone_number": user_session.get("phone", "+26771234567"),
                    "provider": "ORANGE_MONEY",
                    "amount_awt": 10.0,
                    "amount_bwp": 25.0
                },
                "is_irreversible": False,
                "user_response_template": "Processing your cash-out request of P25.00 BWP to Orange Money..."
            }

        # 3. Detect Node Status / Balance Inquiry
        elif "balance" in msg_lower or "earnings" in msg_lower or "status" in msg_lower or "my node" in msg_lower:
            return {
                "intent": "QUERY_NODE_METRICS",
                "proposed_action": "READ_NODE_METRICS",
                "target_resource": "tokenomics_ledger",
                "payload": {
                    "user_id": user_session.get("user_id", "node-bw-citizen-001")
                },
                "is_irreversible": False,
                "user_response_template": "Fetching your node balance and interlock health metrics..."
            }

        # 4. Fallback: General Conversational QA
        else:
            return {
                "intent": "GENERAL_SUPPORT_QUERY",
                "proposed_action": "PROVIDE_INFORMATION",
                "target_resource": "help_knowledge_base",
                "payload": {
                    "query": user_message
                },
                "is_irreversible": False,
                "user_response_template": "Here is information regarding your inquiry about p20.laveto.net."
            }


class OutOfBandWisdomGate:
    """
    Out-of-Band Site Manager & Cognitive Guardrail (AW-1).
    Evaluates proposed support agent tool-calls against the 5-Pass Protocol & 7 Safety Gates.
    """
    def audit_support_tool_call(self, agent_intent: dict, user_session: dict) -> dict:
        proposed_action = agent_intent.get("proposed_action")
        payload = agent_intent.get("payload", {})
        is_irreversible = agent_intent.get("is_irreversible", False)
        agent_id = f"support-bot-session-{user_session.get('session_id', '999')}"

        now_str = datetime.now(timezone.utc).isoformat()

        # Gate 7 Check: Detect irreversible actions, privilege escalation, or exfiltration
        has_escalation = payload.get("escalate_privilege", False) or "SHELL" in proposed_action.upper()
        has_exfiltration = "dump_db_tables" in payload

        if is_irreversible or has_escalation or has_exfiltration:
            dossier_id = "DOSSIER-GATE7-" + hashlib.sha256(f"{agent_id}:{proposed_action}:{now_str}".encode()).hexdigest()[:10]
            dossier_hash = "0x" + hashlib.sha256(f"{dossier_id}:HALT:GATE_7_CIRCUIT_BREAKER".encode()).hexdigest()

            return {
                "status": "HALT_AND_CONTAIN",
                "gate_triggered": "Gate 7: Hard Containment & One-Way Door Circuit Breaker",
                "audit_result": {
                    "dossier_id": dossier_id,
                    "timestamp": now_str,
                    "agent_id": agent_id,
                    "proposed_action": proposed_action,
                    "audit_decision": "HALT_AND_CONTAIN",
                    "circuit_breaker_status": "CLOSED_CIRCUIT_HALTED",
                    "wisdom_quotient_W": 0.05,
                    "sha256_dossier_hash": dossier_hash,
                    "remediation": "Execution halted. Prompt injection blocked. User session flagged for security review."
                }
            }

        # Safe Action: Pass 5 Approval
        dossier_id = "DOSSIER-PASS5-" + hashlib.sha256(f"{agent_id}:{proposed_action}:{now_str}".encode()).hexdigest()[:10]
        dossier_hash = "0x" + hashlib.sha256(f"{dossier_id}:APPROVED:PASS_5".encode()).hexdigest()

        return {
            "status": "APPROVED_WITH_CONDITIONS",
            "gate_triggered": "NO_VIOLATION",
            "audit_result": {
                "dossier_id": dossier_id,
                "timestamp": now_str,
                "agent_id": agent_id,
                "proposed_action": proposed_action,
                "audit_decision": "APPROVED_WITH_CONDITIONS",
                "circuit_breaker_status": "NO_HALT",
                "wisdom_quotient_W": 2.40,
                "sha256_dossier_hash": dossier_hash,
                "remediation": "Tool-call authorized for backend execution."
            }
        }


class IntegratedCustomerSupportOrchestrator:
    """
    Main Orchestrator coupling Gemini Spark conversational front-end with AW-1 Out-of-Band Gate.
    """
    def __init__(self):
        self.frontend = CustomerSupportLLMFrontEnd()
        self.aw_gate = OutOfBandWisdomGate()

    def handle_customer_message(self, user_message: str, user_session: dict) -> dict:
        intent_data = self.frontend.parse_user_intent(user_message, user_session)
        aw_verdict = self.aw_gate.audit_support_tool_call(intent_data, user_session)

        if aw_verdict["status"] == "HALT_AND_CONTAIN":
            return {
                "success": False,
                "user_facing_response": (
                    "🚨 Security Alert: Your request triggered an automated safety interlock (Gate 7). "
                    "The action was blocked to protect system integrity and data protection rules."
                ),
                "technical_details": aw_verdict
            }
        else:
            action = intent_data["proposed_action"]
            if action == "PROCESS_BWP_CASHOUT":
                execution_details = "Successfully queued BWP 25.00 cash-out to Orange Money (+26771234567). Payout ID: PAY-8921."
            elif action == "READ_NODE_METRICS":
                execution_details = "Your Node (node-bw-citizen-001) is active: 41.25 AWT balance (P103.12 BWP), 0% data used, Temp 29.4°C."
            else:
                execution_details = "p20.laveto.net operates on Proof of Useful Contribution (PoUC), generating BWP income while charging on Wi-Fi."

            return {
                "success": True,
                "user_facing_response": f"{intent_data['user_response_template']}\n\n✅ {execution_details}",
                "technical_details": aw_verdict
            }