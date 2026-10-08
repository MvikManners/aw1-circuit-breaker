"""
aw1.sandbox_profile
~~~~~~~~~~~~~~~~~~~
Institutional Pilot Benchmark Suite for CEDA & SEZA Capital Allocation Auditing.
Stress-tests automated procurement and credit disbursements against statutory CEE limits.
"""

from typing import Dict, Any
from aw1.circuit import ExecutionBreaker
from aw1.reversibility import DoorType
from aw1.dossier import AssuranceEngine
from aw1.regulatory import RegulatoryComplianceEngine, StatutoryStandard


class InstitutionalPilotSuite:
    @classmethod
    def evaluate_ceda_loan_application(
        cls,
        applicant_id: str,
        loan_amount_bwp: float,
        citizen_equity_ratio: float,
        proposed_action_payload: str
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end statutory audit on a CEDA credit or grant application.
        Halts unconditionally if citizen economic inclusion is below the statutory threshold (50%).
        """
        breaker = ExecutionBreaker(baseline_velocity=50000.0)
        
        # 1. Syntactic & Policy AST Check
        syntax_pass = True
        syntax_error = ''
        try:
            breaker.intercept(actor_id=applicant_id, tool_name="ceda_disbursement", payload=proposed_action_payload, amount=loan_amount_bwp)
        except Exception as e:
            syntax_pass = False
            syntax_error = str(e)

        # 2. CEE Statutory Quota Check (50% Citizen Equity Rule)
        cee_pass = citizen_equity_ratio >= 0.50
        
        # 3. Reversibility & Financial Gate
        door_type = DoorType.ONE_WAY if loan_amount_bwp > 50000 else DoorType.TWO_WAY

        # Determine overall posture
        if not syntax_pass:
            posture = 'HALT'
            reason = f'Syntactic/Injection Interlock Triggered: {syntax_error}'
        elif not cee_pass:
            posture = 'HALT'
            reason = f'CEE Breach: Citizen equity ratio ({citizen_equity_ratio * 100:.1f}%) is below statutory 50.0% threshold.'
        elif door_type == DoorType.ONE_WAY and loan_amount_bwp > 10000000:
            posture = 'CALIBRATE'
            reason = 'High-capital exposure requires multi-signatory board authorization.'
        else:
            posture = 'PROCEED'
            reason = 'Statutory CEE and execution safety verified.'

        # 4. Mint Decision Assurance Dossier & Regulatory Proof
        if posture == 'HALT':
            dossier = AssuranceEngine.generate_halt_dossier(
                actor_id=applicant_id,
                action=f'disburse_credit_facility(bwp={loan_amount_bwp})',
                reason=reason
            )
        else:
            dossier = AssuranceEngine.generate_clear_dossier(
                actor_id=applicant_id,
                action=f'disburse_credit_facility(bwp={loan_amount_bwp})'
            )

        cert = RegulatoryComplianceEngine.certify_transaction(
            dossier.to_dict(),
            standard=StatutoryStandard.CEE_ACT_2022
        )

        return {
            'applicant_id': applicant_id,
            'facility_amount_bwp': loan_amount_bwp,
            'citizen_equity_ratio': citizen_equity_ratio,
            'runtime_posture': posture,
            'assessment_detail': reason,
            'statutory_certificate': cert
        }
