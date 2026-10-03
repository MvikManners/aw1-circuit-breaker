"""
laveto_sdk.py
Zero-dependency Python client library for Laveto Wisdom AW using standard urllib.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

class LavetoWisdomError(Exception):
    """Base exception for Laveto Wisdom SDK errors."""
    pass

class LavetoWisdomClient:
    def __init__(self, base_url: str = "https://p20.laveto.net/wisdom", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-Laveto-Key"] = self.api_key

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else str(e)
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("message") or err_json.get("error") or err_body
            except Exception:
                msg = err_body
            raise LavetoWisdomError(f"HTTP {e.code}: {msg}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to connect to Laveto Wisdom AW engine at {url}: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during Laveto Wisdom API request: {str(e)}")

    def audit_decision(
        self,
        dilemma_id: str = "CEDA-SOLAR-TENDER-2026",
        audit_fee_bwp: float = 50000.0,
        awt_market_price_bwp: float = 2.50
    ) -> Dict[str, Any]:
        """
        Execute an enterprise decision audit and trigger 20% buyback-and-burn.
        """
        endpoint = "/api/v1/aw/audit"
        payload = {
            "dilemma_id": dilemma_id,
            "audit_fee_bwp": audit_fee_bwp,
            "awt_market_price_bwp": awt_market_price_bwp
        }
        return self._post(endpoint, payload)

    def submit_pouc_evaluation(
        self,
        node_id: str = "node-edge-bw-9941",
        battery_level_percent: float = 92.0,
        thermal_state_celsius: float = 29.5,
        surfaced_blindspot: str = "Identified CEE subcontracting non-compliance in SEZA Phase 2 solar farm tender.",
        peer_scores: Optional[List[float]] = None,
        power_source: str = "AC_CHARGING",
        network_type: str = "UNMETERED_WIFI"
    ) -> Dict[str, Any]:
        """
        Submit an edge device micro-evaluation for dual-token rewards (AWT + W_tau).
        """
        if peer_scores is None:
            peer_scores = [2.1, 2.3]

        endpoint = "/api/v1/aw/pouc/submit"
        payload = {
            "node_id": node_id,
            "telemetry": {
                "power_source": power_source,
                "network_type": network_type,
                "battery_level_percent": battery_level_percent,
                "thermal_state_celsius": thermal_state_celsius
            },
            "scores": {
                "foresight_depth_Fn": 4.8,
                "axiological_coverage_Ac": 0.88,
                "irreversibility_risk_Rrisk": 1.1,
                "epistemic_hubris_penalty_Hpen": 0.7
            },
            "surfaced_blindspot": surfaced_blindspot,
            "peer_scores": peer_scores
        }
        return self._post(endpoint, payload)
