"""
laveto_wisdom/scoring.py
Mathematical Scoring Engine for the Wisdom Quotient (W).
Formula: W = (Fn * Ac) / (Rrisk + Hpen)
"""

class WisdomScorer:
    @staticmethod
    def calculate(
        foresight_depth: float,    # Fn in [1.0, 5.0]
        axiological_coverage: float, # Ac in [0.0, 1.0]
        irreversibility_risk: float, # Rrisk in [0.1, 10.0]
        epistemic_hubris: float     # Hpen in [0.1, 5.0]
    ) -> dict:
        denominator = irreversibility_risk + epistemic_hubris
        w_score = (foresight_depth * axiological_coverage) / max(denominator, 0.01)
        w_score_rounded = round(w_score, 2)

        # Classify Posture based on score
        if w_score_rounded >= 2.5:
            posture = "PROCEED"
        elif 1.0 <= w_score_rounded < 2.5:
            posture = "CALIBRATE"
        else:
            posture = "HALT"

        return {
            "wisdom_quotient": w_score_rounded,
            "posture": posture,
            "metrics": {
                "foresight_depth_Fn": foresight_depth,
                "axiological_coverage_Ac": axiological_coverage,
                "irreversibility_risk_Rrisk": irreversibility_risk,
                "epistemic_hubris_penalty_Hpen": epistemic_hubris
            },
            "formula": f"({foresight_depth} * {axiological_coverage}) / ({irreversibility_risk} + {epistemic_hubris}) = {w_score_rounded}"
        }
