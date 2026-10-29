"""
laveto_wisdom/simulator.py
Dry-Run Policy Calibration and Comparative Scenario Simulator for Laveto Wisdom AW.
Evaluates baseline vs calibrated variations without logging production API usage.
"""
from .pipeline import run_wisdom_audit

def simulate_comparative_audit(baseline_proposal: str, calibrated_proposal: str) -> dict:
    """Executes a non-persisted side-by-side comparative simulation."""
    baseline_result = run_wisdom_audit(baseline_proposal)
    calibrated_result = run_wisdom_audit(calibrated_proposal)

    b_score = float(baseline_result.get("wisdom_quotient", 0.0))
    c_score = float(calibrated_result.get("wisdom_quotient", 0.0))
    delta = round(c_score - b_score, 2)

    return {
        "simulation_id": f"SIM-{baseline_result.get('audit_id', 'RAW')[-4:]}-{calibrated_result.get('audit_id', 'CAL')[-4:]}",
        "baseline": baseline_result,
        "calibrated": calibrated_result,
        "metrics_delta": {
            "score_shift": delta,
            "status": "IMPROVED" if delta > 0 else ("DEGRADED" if delta < 0 else "NEUTRAL"),
            "posture_transition": f"{baseline_result.get('posture')} -> {calibrated_result.get('posture')}"
        }
    }
