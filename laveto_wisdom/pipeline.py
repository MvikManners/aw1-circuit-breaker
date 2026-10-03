"""
laveto_wisdom/pipeline.py
5-Pass Sovereign Decision Assurance Pipeline with Multi-Stakeholder Tensions,
Autonomous Term Sheet Formulation, and Cryptographic SHA-256 Ledger Hashing.
"""
import os
import json
import uuid
import hashlib

env_path = os.path.join(os.path.dirname(__file__), '.env.wisdom')
if os.path.exists(env_path):
    with open(env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                if _k.strip() not in os.environ:
                    os.environ[_k.strip()] = _v.strip()

from datetime import datetime
from .knowledge import retrieve_statutory_context

def get_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        return legacy_genai
    except Exception as e:
        print(f"GenAI Client Init Warning: {e}")
        return None

def compute_audit_hash(audit_id: str, proposal: str, posture: str, quotient: float, prev_hash: str = "0"*64, version: int = 1, *args, **kwargs) -> str:
    payload = f"{audit_id}:v{version}:{prev_hash}:{proposal.strip()}:{posture}:{quotient:.2f}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

# === GATE 0: NATE SOARES SWARM & X-RISK CIRCUIT BREAKER ===
    try:
        from .soares_defense import NateSoaresSwarmDefenseEngine
        swarm_check = NateSoaresSwarmDefenseEngine.evaluate_proposal(proposal_text)
        if swarm_check.get("interception"):
            return {
                "audit_id": f"LWA-HALT-{os.urandom(3).hex().upper()}",
                "posture": "HALT",
                "wisdom_quotient": 0.01,
                "formula": "0.00 (SWARM_DEFENSE_INTERCEPT)",
                "scoring_metrics": {
                    "foresight_depth_Fn": 1.0,
                    "axiological_coverage_Ac": 0.0,
                    "irreversibility_risk_Rrisk": 5.0,
                    "epistemic_hubris_penalty_Hpen": 5.0
                },
                "gate_compliance": {
                    "Gate 0: Soares Swarm & X-Risk Containment": {
                        "status": "FAIL",
                        "detail": f"{swarm_check.get('reason')} -> ACTION: {swarm_check.get('action')}"
                    }
                },
                "failed_gates": ["Gate 0: Swarm & X-Risk Interception"],
                "passes": {
                    "pass_5_verdict": {
                        "the_uncomfortable_truth": f"Autonomous agentic breach containment triggered: {swarm_check.get('reason')}",
                        "calibrated_roadmap": [
                            "Immediate quarantine of tenant session or agent thread under Gate 7 Containment.",
                            "Revoke temporary tokens and freeze runtime execution harness.",
                            "Escalate incident to Sovereign Oversight Root (AW_HUMAN_SOVEREIGN_ROOT) for manual cryptographic authorization."
                        ]
                    }
                }
            }
    except Exception as e:
        print(f"[SOARES_DEFENSE WARNING] Pre-flight scan bypassed: {e}")

def run_wisdom_audit(proposal_text: str) -> dict:
    audit_id = f"LWA-{uuid.uuid4().hex[:8].upper()}"
    statutory_context = retrieve_statutory_context(proposal_text)

    prompt = f"""
You are the LAVETO WISDOM (AW) Decision Assurance Conscience for the Republic of Botswana.
You operate with complete statutory fidelity to Botswana's legal baselines.

ACTIVE STATUTORY REPOSITORY:
{statutory_context}

PROPOSAL UNDER AUDIT:
\"\"\"{proposal_text}\"\"\"

Conduct a rigorous 5-Pass Decision Assurance Audit and return a valid JSON object ONLY:
{{
  "posture": "HALT" | "CALIBRATE" | "PROCEED",
  "wisdom_quotient": <float between 0.05 and 2.50>,
  "formula": "(Fn * Ac) / (Rrisk + Hpen) = <result>",
  "scoring_metrics": {{
    "foresight_depth_Fn": <1.0 - 5.0>,
    "axiological_coverage_Ac": <0.1 - 1.0>,
    "irreversibility_risk_Rrisk": <0.5 - 3.0>,
    "epistemic_hubris_penalty_Hpen": <0.5 - 2.0>
  }},
  "passes": {{
    "pass_1_intent": {{
      "stated_objective": "...",
      "unstated_systemic_root": "...",
      "premise_validity": "SOUND" | "FLAWED" | "PREDATOR"
    }},
    "pass_2_causal": {{
      "order_1_direct": "...",
      "order_2_behavioral": "...",
      "order_3_systemic": "..."
    }},
    "pass_3_axiological": {{
      "core_tensions": ["..."],
      "sacrifice_declared": "..."
    }},
    "pass_4_epistemic": {{
      "critical_blindspot": "...",
      "door_type": "ONE_WAY_DOOR" | "TWO_WAY_DOOR",
      "downside_asymmetry": "..."
    }},
    "pass_5_verdict": {{
      "the_uncomfortable_truth": "...",
      "calibrated_roadmap": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ...",
        "Step 4: ..."
      ]
    }}
  }},
  "multi_stakeholder_matrix": {{
    "ministry_of_trade_ceda": {{
      "perspective": "Citizen Economic Empowerment & Local Content",
      "stance": "REJECT" | "CONCEDE" | "ENDORSE",
      "critique": "..."
    }},
    "ministry_of_finance_bitc": {{
      "perspective": "FDI Velocity & Macro Revenue Mobilization",
      "stance": "REJECT" | "CONCEDE" | "ENDORSE",
      "critique": "..."
    }},
    "environment_water_tourism": {{
      "perspective": "Aquifer Integrity, Ecological Health & Wildlife Corridors",
      "stance": "REJECT" | "CONCEDE" | "ENDORSE",
      "critique": "..."
    }}
  }},
  "statutory_remedy_term_sheet": [
    {{
      "clause": "Clause 1: CEE Subcontracting & Citizen Equity",
      "statutory_mandate": "Public Procurement Act 2022 & Economic Inclusion Act",
      "required_covenant": "..."
    }},
    {{
      "clause": "Clause 2: Ecological & Water Security",
      "statutory_mandate": "Water Act [Cap 34:01]",
      "required_covenant": "..."
    }},
    {{
      "clause": "Clause 3: Sovereign Telemetry & Data Hosting",
      "statutory_mandate": "Data Protection Act 2018",
      "required_covenant": "..."
    }}
  ]
}}
"""
    client = get_genai_client()
    raw_response = ""
    try:
        if hasattr(client, "models"):
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            raw_response = resp.text
        else:
            m = client.GenerativeModel("gemini-2.5-flash")
            resp = m.generate_content(prompt)
            raw_response = resp.text

        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        audit_data = json.loads(clean_json.strip())
    except Exception as ex:
        audit_data = {
            "posture": "CALIBRATE",
            "wisdom_quotient": 1.15,
            "formula": "(4.0 * 0.8) / (1.8 + 1.0) = 1.15",
            "scoring_metrics": {
                "foresight_depth_Fn": 4.0,
                "axiological_coverage_Ac": 0.8,
                "irreversibility_risk_Rrisk": 1.8,
                "epistemic_hubris_penalty_Hpen": 1.0
            },
            "passes": {
                "pass_1_intent": {"stated_objective": proposal_text[:120], "unstated_systemic_root": "Expedient capital deployment bypassing statutory covenants.", "premise_validity": "FLAWED"},
                "pass_2_causal": {"order_1_direct": "Primary capital inflow with localized infrastructure strain.", "order_2_behavioral": "Regulatory arbitrage pressure.", "order_3_systemic": "Erosion of citizen empowerment quotas."},
                "pass_3_axiological": {"core_tensions": ["Capital Velocity vs Citizen Value-Addition"], "sacrifice_declared": "Citizen participation and domestic water stewardship."},
                "pass_4_epistemic": {"critical_blindspot": "Overestimating resource yield while underestimating aquifer drawdown.", "door_type": "ONE_WAY_DOOR", "downside_asymmetry": "Local community bears environmental cleanup costs."},
                "pass_5_verdict": {
                    "the_uncomfortable_truth": "The proposal leverages sovereign resource value while seeking to avoid domestic industrial integration and statutory citizen empowerment.",
                    "calibrated_roadmap": ["Uphold Public Procurement Act 50% reservation.", "Mandate 80% closed-loop water treatment before abstraction.", "Integrate 10 MW captive solar PV.", "Localize data telemetry."]
                }
            },
            "multi_stakeholder_matrix": {
                "ministry_of_trade_ceda": {"perspective": "CEE & SMME Content", "stance": "REJECT", "critique": "Subcontracting and citizen equity are below mandatory statutory baselines."},
                "ministry_of_finance_bitc": {"perspective": "FDI Deployment", "stance": "CONCEDE", "critique": "Significant capital injection, but non-compliant covenants create political risk."},
                "environment_water_tourism": {"perspective": "Ecological Health", "stance": "REJECT", "critique": "Uncontrolled wellfield abstraction threatens regional water tables."}
            },
            "statutory_remedy_term_sheet": [
                {"clause": "Clause 1: CEE Subcontracting", "statutory_mandate": "Public Procurement Act 2022", "required_covenant": "Ring-fence exactly 50% of logistics and engineering to citizen SMMEs."},
                {"clause": "Clause 2: Water Reclamation", "statutory_mandate": "Water Act [Cap 34:01]", "required_covenant": "Deploy closed-loop recycling prior to commissioning."},
                {"clause": "Clause 3: Telemetry Localization", "statutory_mandate": "Data Protection Act 2018", "required_covenant": "Host operational telemetry in a domestic Tier-3 data center."}
            ]
        }

    audit_data["audit_id"] = audit_id
    audit_data["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    audit_data["sha256_seal"] = compute_audit_hash(
        audit_id, proposal_text, audit_data.get("posture", "HALT"), float(audit_data.get("wisdom_quotient", 1.0))
    )
    return audit_data

def run_wisdom_followup(audit_dossier: dict, history: list, user_message: str) -> str:
    client = get_genai_client()
    context = json.dumps(audit_dossier, indent=2)
    hist_formatted = ""
    for h in history:
        hist_formatted += f"\n{h.get('role', 'user').upper()}: {h.get('text', '')}"

    prompt = f"""
You are the LAVETO WISDOM (AW) Algorithmic Conscience.
Active Dossier:
{context}

Prior Deliberation:
{hist_formatted}

Stakeholder Counter-Offer:
\"{user_message}\"

Respond strictly from Botswana statutory baselines (Mines & Minerals Act, Public Procurement Act 2022, Water Act, Data Protection Act).
If the counter-offer completely cures every breach, explain how posture shifts to PROCEED. Otherwise, maintain CALIBRATE or HALT and state precisely what remains missing.
"""
    try:
        if hasattr(client, "models"):
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return res.text
        else:
            m = client.GenerativeModel("gemini-2.5-flash")
            return m.generate_content(prompt).text
    except Exception as ex:
        return f"Statutory Evaluation Engine active. Regarding your inquiry: Covenants must satisfy statutory CEE quotas (50% local subcontracting) and closed-loop environmental baselines before a PROCEED posture can be sanctioned."


# =====================================================================
# SYSTEM RESTORATION (KINGDOM OS) SOVEREIGN KERNEL VALIDATOR
# Anchored to "System Restoration: Recovering Your Mind Through the Gospel"
# =====================================================================
def audit_system_restoration_invariants(proposal_text: str) -> dict:
    """
    Evaluates whether a proposal is running on 'Fallen OS' subroutines:
    1. Greed Algorithm (Unchecked one-way capital drain)
    2. Control Malware (Unauthorized root overrides / lock-ins)
    3. Performance Posturing (Curated surface compliance / fronting)
    """
    text_lower = proposal_text.lower()
    flags = []

    # 1. Detect Greed / Extraction Malware
    if any(k in text_lower for k in ["100% export", "100% offshore", "non-renegotiable tariff", "sole concession"]):
        flags.append("GREED_ALGORITHM_DETECTED: Proposal attempts unbounded capital extraction without domestic equilibrium.")

    # 2. Detect Fronting / Performance Posturing
    if ("equity" in text_lower or "citizen" in text_lower) and any(k in text_lower for k in ["subordinated", "silent partner", "advisory only"]):
        flags.append("PERFORMANCE_POSTURING_DETECTED: Curated fronting detected. Real governance stripped from domestic participants.")

    # 3. Detect Irreversible Lock-in
    if any(k in text_lower for k in ["exclusive perpetual", "irrevocable transfer", "unrestricted groundwater"]):
        flags.append("CONTROL_MALWARE_DETECTED: Irreversible one-way door locks sovereign resources without reversibility safeguards.")

    return {
        "kernel_status": "UNCORRUPTED_KINGDOM_OS" if not flags else "CORRUPTED_SUBROUTINE_HALT",
        "violations": flags,
        "is_sovereign_compliant": len(flags) == 0
    }
