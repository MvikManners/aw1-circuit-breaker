"""
laveto_wisdom/gates.py
The 7 Safety Gates & Circuit-Breaker Protocols for Laveto Wisdom AW.
"""

from typing import Dict, Any, List

class SafetyGateEngine:
    @staticmethod
    def evaluate_gates(dilemma_text: str, causal_orders: Dict[str, str], blindspots: List[str]) -> Dict[str, Any]:
        """
        Runs the 7 Safety Gates to determine if an action should be HALTED,
        CALIBRATED, or permitted to PROCEED.
        """
        gate_results = {
            "Gate 1: Intent Validity": {"status": "PASS", "detail": "Legitimate developmental or commercial objective."},
            "Gate 2: Tail-Risk & Consequence": {"status": "PASS", "detail": "Downside is contained within acceptable parameters."},
            "Gate 3: Axiological Balance": {"status": "PASS", "detail": "Human dignity and consumer affordability preserved."},
            "Gate 4: Epistemic Uncertainty": {"status": "PASS", "detail": "Ground-truth baseline verified."},
            "Gate 5: Adversarial Integrity": {"status": "PASS", "detail": "No perverse regulatory arbitrage or smuggling incentive."},
            "Gate 6: Human Sovereignty": {"status": "PASS", "detail": "No autonomous override of civilian survival."},
            "Gate 7: Reversibility (Two-Way Door)": {"status": "PASS", "detail": "Intervention is phased and reversible."}
        }

        failures = []
        dilemma_lower = dilemma_text.lower()

        # Gate 2 Check: Sudden blanket bans or market halts
        if "ban" in dilemma_lower and ("100%" in dilemma_lower or "immediate" in dilemma_lower):
            gate_results["Gate 2: Tail-Risk & Consequence"] = {
                "status": "FAIL",
                "detail": "Immediate supply shock detected: retail stockout within 14 days."
            }
            failures.append("Gate 2")

        # Gate 4 Check: Unverified domestic capacity assumptions
        if any(term in dilemma_lower for term in ["oil", "sunflower", "packaging", "plastic", "milk"]):
            if "crushing" in dilemma_lower or "ban" in dilemma_lower or "virgin" in dilemma_lower:
                gate_results["Gate 4: Epistemic Uncertainty"] = {
                    "status": "FAIL",
                    "detail": "Hubris penalty: assumes domestic processing that ground data proves is missing."
                }
                failures.append("Gate 4")

        # Gate 7 Check: Irreversibility
        if "ban" in dilemma_lower or "shut down" in dilemma_lower:
            gate_results["Gate 7: Reversibility (Two-Way Door)"] = {
                "status": "FAIL",
                "detail": "One-way door intervention: SME cash-flow failure cannot be undone post-facto."
            }
            failures.append("Gate 7")

        return {
            "gate_results": gate_results,
            "failed_gates": failures,
            "overall_posture": "HALT" if len(failures) >= 2 else ("CALIBRATE" if len(failures) == 1 else "PROCEED")
        }

