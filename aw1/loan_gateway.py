"""
aw1.loan_gateway
~~~~~~~~~~~~~~~~
Statutory Enforcement Gateway for CEDA / SEZA Credit Disbursements.
Enforces Economic Inclusion Act 2021 citizen equity quotas prior to transaction execution.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any


class StatutoryGateError(Exception):
    """Raised when an allocation violates statutory quotas or execution safety."""
    pass


class CEDADisbursementGate:
    """
    Acts as a deterministic execution barrier before funds release.
    """
    AUDIT_ENDPOINT = "https://p20.laveto.net/wisdom/api/v1/compliance/ceda-audit"

    @classmethod
    def verify_and_authorize(
        cls,
        applicant_id: str,
        loan_amount_bwp: float,
        citizen_equity_ratio: float,
        execution_action_str: str
    ) -> Dict[str, Any]:
        """
        Validates equity quota and AST safety against the live compliance gate.
        Returns the statutory clearance certificate upon success; raises StatutoryGateError on HALT.
        """
        payload = {
            "applicant_id": applicant_id,
            "loan_amount_bwp": float(loan_amount_bwp),
            "citizen_equity_ratio": float(citizen_equity_ratio),
            "proposed_action_payload": execution_action_str
        }

        req = urllib.request.Request(
            cls.AUDIT_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("runtime_posture") == "PROCEED":
                    return data
                raise StatutoryGateError(f"Pre-approval rejected: {data.get('assessment_detail')}")

        except urllib.error.HTTPError as e:
            err_data = json.loads(e.read().decode("utf-8"))
            cert = err_data.get("statutory_certificate", {})
            raise StatutoryGateError(
                f"EXECUTION_HALTED: {err_data.get('assessment_detail')} "
                f"[Seal: {cert.get('statutory_seal_sha256')}]"
            ) from None
