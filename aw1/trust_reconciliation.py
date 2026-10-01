"""
aw1.trust_reconciliation
~~~~~~~~~~~~~~~~~~~~~~~~
Bank of Botswana (BoB) 1-to-1 Trust Account Reconciliation Engine.
Verifies liquid fiat escrow backing against aggregate circulating float under the NCSS Act.
"""

from typing import Dict, Any, List
import time
from aw1.dossier import DecisionAssuranceDossier, AssuranceEngine
from aw1.regulatory import RegulatoryComplianceEngine, StatutoryStandard


class TrustAccountReconciliationEngine:
    @classmethod
    def audit_daily_trust_balance(
        cls,
        audit_date: str,
        custodian_bank_name: str,
        escrow_fiat_balance_bwp: float,
        circulating_float_bwp: float,
        pending_outbound_settlements_bwp: float = 0.0
    ) -> Dict[str, Any]:
        """
        Audits 1-to-1 trust coverage for Bank of Botswana compliance.
        Coverage Ratio = Escrow Fiat Reserves / (Circulating Float + Pending Settlements)
        Requirement: Ratio >= 1.0000 (100% Backing). Any deficit triggers an immediate HALT.
        """
        total_customer_obligations = round(circulating_float_bwp + pending_outbound_settlements_bwp, 2)
        escrow_balance = round(escrow_fiat_balance_bwp, 2)
        variance_bwp = round(escrow_balance - total_customer_obligations, 2)
        
        ratio = round(escrow_balance / total_customer_obligations, 4) if total_customer_obligations > 0 else 1.0
        
        is_compliant = variance_bwp >= 0.0 and ratio >= 1.0000

        if not is_compliant:
            posture = "HALT"
            reason = (
                f"CRITICAL BOB BREACH: Reserve deficit of BWP {abs(variance_bwp):,.2f}. "
                f"Backing ratio is {ratio * 100:.2f}% (Statutory minimum: 100.00%)."
            )
            dossier = AssuranceEngine.generate_halt_dossier(
                actor_id=f"bob_custodian_{custodian_bank_name.lower().replace(' ', '_')}",
                action=f"reconcile_trust_escrow(date={audit_date})",
                reason=reason
            )
        else:
            posture = "PROCEED"
            surplus_str = f" Surplus: BWP {variance_bwp:,.2f}." if variance_bwp > 0 else " Exact 1-to-1 parity."
            reason = f"Bank of Botswana 1-to-1 trust backing verified at {ratio * 100:.2f}%.{surplus_str}"
            dossier = AssuranceEngine.generate_clear_dossier(
                actor_id=f"bob_custodian_{custodian_bank_name.lower().replace(' ', '_')}",
                action=f"reconcile_trust_escrow(date={audit_date})"
            )

        cert = RegulatoryComplianceEngine.certify_transaction(
            dossier.to_dict(),
            standard=StatutoryStandard.BOB_NPS_ACT_2022
        )

        return {
            "audit_date": audit_date,
            "custodian_bank": custodian_bank_name,
            "escrow_fiat_balance_bwp": escrow_balance,
            "circulating_float_bwp": circulating_float_bwp,
            "pending_settlements_bwp": pending_outbound_settlements_bwp,
            "total_customer_obligations_bwp": total_customer_obligations,
            "variance_bwp": variance_bwp,
            "backing_ratio": ratio,
            "runtime_posture": posture,
            "reconciliation_status": "VERIFIED_SOLVENT" if is_compliant else "DEFICIT_INSOLVENCY_ALERT",
            "statutory_assessment": reason,
            "assurance_dossier": dossier.to_dict(),
            "statutory_certificate": cert
        }
