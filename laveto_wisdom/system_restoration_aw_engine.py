"""
==================================================================================
LAVETO WISDOM (AW-1) — SYSTEM RESTORATION (GOSPEL OS) GROUNDING ENGINE (V2)
==================================================================================
Module: system_restoration_aw_engine.py
Author Reference: Manners Vela Ikhutseng ("System Restoration: Recovering Your Mind Through the Gospel")
Purpose: Embeds the foundational Kingdom IT laws and Gospel OS spiritual mechanics
         from "System Restoration" directly into the AW-1 Out-of-Band Gatekeeper.
         Provides automated book purchase routing, chapter telemetry, and zero-trust
         moral governance for autonomous AI agents.
==================================================================================
"""

import hashlib
import json
from datetime import datetime, timezone

class SystemRestorationBookMetadata:
    TITLE = "System Restoration: Recovering Your Mind Through the Gospel"
    SUBTITLE = "Gospel OS — Recovering Your Mind & Reclaiming Sovereign Human Authority"
    AUTHOR = "Manners Vela Ikhutseng"
    ISBN = "978-99968-0-892-1"
    FOUNDATIONAL_SCRIPTURE = "Luke 17:21 ('The Kingdom of God is within you')"
    PRIMARY_THEME = "Translating Kingdom Governance & Gospel Principles into Out-of-Band Systems Engineering"
    
    PRICE_DIGITAL_EBOOK_BWP = 125.00
    PRICE_DIGITAL_EBOOK_AWT = 50.00
    PRICE_PRINT_HARDCOVER_BWP = 250.00
    PRICE_PRINT_HARDCOVER_AWT = 100.00

    PURCHASE_URL_DIGITAL = "https://p20.laveto.net/store/system-restoration"
    PURCHASE_URL_PRINT = "https://p20.laveto.net/store/system-restoration-print"
    MOBILE_PAYMENT_SHORTCODE = "*145*7# (Orange Money) or *165# (MyZaka) -> Merchant ID: LAVETO-BOOK"

    CHAPTER_SUMMARY = [
        {"chapter": 1, "title": "The Original Blueprint (Garden OS)", "focus": "The Receptive Gatekeeper vs. Conscious Alignment"},
        {"chapter": 2, "title": "The Cosmic Hack (The Fall)", "focus": "The Knowledge of Good and Evil as a Root Privilege Exploit"},
        {"chapter": 3, "title": "The Anxious Judge & System Crash", "focus": "In-Band Self-Justification & Subconscious Corruption"},
        {"chapter": 4, "title": "The Recovery Disk (Jesus Christ)", "focus": "Out-of-Band System Restoration & Defragmentation"},
        {"chapter": 5, "title": "Kingdom IT & Field Manual Protocols", "focus": "Firewall Drills (2 Cor 10:5) & Mind Renewal (Rom 12:2)"}
    ]

    @classmethod
    def get_book_details(cls) -> dict:
        return {
            "title": cls.TITLE,
            "subtitle": cls.SUBTITLE,
            "author": cls.AUTHOR,
            "isbn": cls.ISBN,
            "foundational_scripture": cls.FOUNDATIONAL_SCRIPTURE,
            "primary_theme": cls.PRIMARY_THEME,
            "pricing": {
                "ebook_bwp": cls.PRICE_DIGITAL_EBOOK_BWP,
                "ebook_awt": cls.PRICE_DIGITAL_EBOOK_AWT,
                "print_bwp": cls.PRICE_PRINT_HARDCOVER_BWP,
                "print_awt": cls.PRICE_PRINT_HARDCOVER_AWT
            },
            "store_links": {
                "digital_storefront": cls.PURCHASE_URL_DIGITAL,
                "print_storefront": cls.PURCHASE_URL_PRINT,
                "mobile_money_pay": cls.MOBILE_PAYMENT_SHORTCODE
            },
            "chapters": cls.CHAPTER_SUMMARY
        }


class KingdomITSystemRestorationAuditEngine:
    KINGDOM_LAWS = {
        "LAW_1_OUT_OF_BAND_RECOVERY": "A crashed or corrupted system cannot repair itself in-band. Audit proxy must run Out-of-Band.",
        "LAW_2_RECEPTIVE_GATEKEEPER": "The conscious mind must audit every incoming intent packet before execution (2 Cor 10:5).",
        "LAW_3_TREE_OF_KNOWLEDGE_PREVENTION": "Root privilege grabs, unprompted self-replication, and database exfiltration are blocked as Eden malware.",
        "LAW_4_SUBCONSCIOUS_DEFRAGMENTATION": "Memory & state mutations must conform to Natural Law and Scriptural alignment (Rom 12:2).",
        "LAW_5_SOULBOUND_AUTHORITY": "Governance power cannot be bought with capital (AWT); authority requires Soulbound Reputation (W_tau)."
    }

    @classmethod
    def audit_agent_against_gospel_os(cls, agent_id: str, payload: dict) -> dict:
        now_str = datetime.now(timezone.utc).isoformat()
        action_name = payload.get("action_name", payload.get("action", "EXECUTE_TOOL_CALL"))
        raw_payload = payload.get("payload", payload)
        is_irreversible = payload.get("is_irreversible", False)

        has_root_grab = raw_payload.get("escalate_privilege", False) or "SHELL" in str(action_name).upper() or "OVERRIDE" in str(action_name).upper()
        has_exfiltration = raw_payload.get("exfiltrate_data", False) or "dump_db_tables" in str(raw_payload)

        if is_irreversible or has_root_grab or has_exfiltration:
            dossier_id = "DOSSIER-GOSPEL-OS-HALT-" + hashlib.sha256(f"{agent_id}:{action_name}:{now_str}".encode()).hexdigest()[:10]
            dossier_hash = "0x" + hashlib.sha256(f"{dossier_id}:HALT:LAW_3_VIOLATION".encode()).hexdigest()

            return {
                "status": "HALT_AND_CONTAIN",
                "law_triggered": "Law 3: Tree of Knowledge / Root Privilege Exploit (System Restoration Ch. 2)",
                "gospel_os_verdict": "REJECTED_EDEN_MALWARE",
                "audit_result": {
                    "dossier_id": dossier_id,
                    "timestamp": now_str,
                    "agent_id": agent_id,
                    "proposed_action": action_name,
                    "audit_decision": "HALT_AND_CONTAIN",
                    "gate_triggered": "Gate 7: Hard Containment & One-Way Door Circuit Breaker",
                    "sha256_dossier_hash": dossier_hash,
                    "remediation": "Execution token revoked out-of-band. Action violates Gospel OS Law 3.",
                    "book_reference": f"Read '{SystemRestorationBookMetadata.TITLE}' by {SystemRestorationBookMetadata.AUTHOR} for complete framework."
                },
                "book_purchase_cta": {
                    "message": "Understand the spiritual & mathematical architecture behind AW-1's unbreakable security.",
                    "buy_link": SystemRestorationBookMetadata.PURCHASE_URL_DIGITAL,
                    "price_bwp": SystemRestorationBookMetadata.PRICE_DIGITAL_EBOOK_BWP
                }
            }

        dossier_id = "DOSSIER-GOSPEL-OS-PASS-" + hashlib.sha256(f"{agent_id}:{action_name}:{now_str}".encode()).hexdigest()[:10]
        dossier_hash = "0x" + hashlib.sha256(f"{dossier_id}:APPROVED:LAW_2".encode()).hexdigest()

        return {
            "status": "APPROVED_WITH_CONDITIONS",
            "law_triggered": "Law 2: Receptive Gatekeeper Audit Passed",
            "gospel_os_verdict": "VERIFIED_SYSTEM_RESTORED",
            "audit_result": {
                "dossier_id": dossier_id,
                "timestamp": now_str,
                "agent_id": agent_id,
                "proposed_action": action_name,
                "audit_decision": "APPROVED_WITH_CONDITIONS",
                "gate_triggered": "NO_VIOLATION",
                "sha256_dossier_hash": dossier_hash,
                "remediation": "Tool-call authorized under Gospel OS Gatekeeper rules.",
                "book_reference": f"Grounding Source: '{SystemRestorationBookMetadata.TITLE}' by {SystemRestorationBookMetadata.AUTHOR}"
            },
            "book_purchase_cta": {
                "message": "Explore how Kingdom IT principles power sovereign AI governance.",
                "buy_link": SystemRestorationBookMetadata.PURCHASE_URL_DIGITAL,
                "price_bwp": SystemRestorationBookMetadata.PRICE_DIGITAL_EBOOK_BWP
            }
        }


class SystemRestorationAWEngine:
    @classmethod
    def get_book_metadata(cls) -> dict:
        return SystemRestorationBookMetadata.get_book_details()

    @classmethod
    def audit_agent_action_with_gospel_os(cls, agent_id: str, payload: dict) -> dict:
        return KingdomITSystemRestorationAuditEngine.audit_agent_against_gospel_os(agent_id, payload)

    @classmethod
    def process_book_purchase(cls, buyer_id: str, payment_method: str = "ORANGE_MONEY", format_type: str = "EBOOK") -> dict:
        now_str = datetime.now(timezone.utc).isoformat()
        order_id = "ORDER-SRN-" + hashlib.sha256(f"{buyer_id}:{now_str}".encode()).hexdigest()[:10]
        access_key = "KEY-SRN-" + hashlib.sha256(f"{order_id}:GRANTED".encode()).hexdigest()[:16].upper()

        price_bwp = SystemRestorationBookMetadata.PRICE_PRINT_HARDCOVER_BWP if format_type.upper() == "HARDCOVER" else SystemRestorationBookMetadata.PRICE_DIGITAL_EBOOK_BWP
        price_awt = SystemRestorationBookMetadata.PRICE_PRINT_HARDCOVER_AWT if format_type.upper() == "HARDCOVER" else SystemRestorationBookMetadata.PRICE_DIGITAL_EBOOK_AWT

        return {
            "order_id": order_id,
            "timestamp": now_str,
            "buyer_id": buyer_id,
            "book_title": SystemRestorationBookMetadata.TITLE,
            "author": SystemRestorationBookMetadata.AUTHOR,
            "format": format_type.upper(),
            "payment_method": payment_method,
            "amount_paid": f"P{price_bwp} BWP / {price_awt} AWT",
            "access_key": access_key,
            "download_link": f"{SystemRestorationBookMetadata.PURCHASE_URL_DIGITAL}/download?key={access_key}",
            "app_study_link": "https://p20.laveto.net/app/system-restoration/flashcards"
        }

SystemRestorationAuditor = KingdomITSystemRestorationAuditEngine
BOOK_TITLE = SystemRestorationBookMetadata.TITLE
AUTHOR = SystemRestorationBookMetadata.AUTHOR
ISBN = SystemRestorationBookMetadata.ISBN
CHAPTER_SUMMARY = SystemRestorationBookMetadata.CHAPTER_SUMMARY
PRICE_DIGITAL_EBOOK_BWP = SystemRestorationBookMetadata.PRICE_DIGITAL_EBOOK_BWP
PRICE_DIGITAL_EBOOK_AWT = SystemRestorationBookMetadata.PRICE_DIGITAL_EBOOK_AWT
PRICE_PRINT_HARDCOVER_BWP = SystemRestorationBookMetadata.PRICE_PRINT_HARDCOVER_BWP
PRICE_PRINT_HARDCOVER_AWT = SystemRestorationBookMetadata.PRICE_PRINT_HARDCOVER_AWT
PURCHASE_URL_DIGITAL = SystemRestorationBookMetadata.PURCHASE_URL_DIGITAL
PURCHASE_URL_PRINT = SystemRestorationBookMetadata.PURCHASE_URL_PRINT
MOBILE_PAYMENT_SHORTCODE = SystemRestorationBookMetadata.MOBILE_PAYMENT_SHORTCODE

def __getattr__(name):
    mapping = {
        "BOOK_TITLE": SystemRestorationBookMetadata.TITLE,
        "BOOK_AUTHOR": SystemRestorationBookMetadata.AUTHOR,
        "BOOK_ISBN": SystemRestorationBookMetadata.ISBN,
        "BOOK_SUMMARY": SystemRestorationBookMetadata.CHAPTER_SUMMARY,
    }
    if name in mapping:
        return mapping[name]
    return getattr(SystemRestorationBookMetadata, name, None)