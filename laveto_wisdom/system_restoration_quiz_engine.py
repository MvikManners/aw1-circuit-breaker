"""
===================================================================================
   LAVETO WISDOM (AW-1) — KINGDOM IT & GOSPEL OS APP SIMULATION ENGINE
===================================================================================
File: system_restoration_quiz_engine.py
Author: Manners Vela Ikhutseng
Description: Interactive Flashcard & Quiz Simulation Engine for Laveto Wisdom (AW-1).
             Translates 'System Restoration: Recovering Your Mind Through the Gospel'
             into an automated gamified learning engine. Users take Kingdom IT drills,
             evaluate spiritual/epistemic alignment, and earn AWT token rewards.
===================================================================================
"""

import json
import hashlib
from datetime import datetime, timezone

class KingdomITAppEngine:
    """
    Engine serving interactive Kingdom IT Flashcards, Quizzes, and AWT Reward Settlement
    grounded in 'System Restoration: Recovering Your Mind Through the Gospel'.
    """

    FLASHCARDS = [
        {
            "id": "FC-001",
            "concept": "The Original Blueprint (Garden OS)",
            "definition": "A state of pure conscious communion where the mind acts as a Receptive Gatekeeper, receiving reality without friction, fear, or self-justification.",
            "scripture": "Luke 17:21 - 'The kingdom of God is within you.'",
            "category": "Mind Baseline"
        },
        {
            "id": "FC-002",
            "concept": "The Anxious Judge",
            "definition": "A corrupted conscious subroutine resulting from the Fall that constantly categorizes all reality as 'good' or 'evil' for the self.",
            "scripture": "Genesis 3:5 - 'You will be like God, knowing good and evil.'",
            "category": "Kernel Corruption"
        },
        {
            "id": "FC-003",
            "concept": "Out-of-Band Recovery Disk",
            "definition": "The Gospel of Jesus Christ functioning as an external restoration mechanism that rebuilds the operating system from outside the corrupted runtime.",
            "scripture": "Romans 8:1 - 'There is now no condemnation for those who are in Christ Jesus.'",
            "category": "System Restoration"
        },
        {
            "id": "FC-004",
            "concept": "Tree of Knowledge vs. Tree of Life",
            "definition": "Tree of Knowledge represents administrative privilege grabs (root hacks for autonomous control). Tree of Life represents dependent communion and abiding wisdom.",
            "scripture": "Proverbs 3:18 - 'She is a tree of life to those who take hold of her.'",
            "category": "Architectural Choice"
        },
        {
            "id": "FC-005",
            "concept": "Firewall Protocol (2 Cor 10:5)",
            "definition": "Capturing every incoming thought packet at the conscious boundary before it installs in subconscious memory as corrupted belief.",
            "scripture": "2 Corinthians 10:5 - 'Taking every thought captive to the obedience of Christ.'",
            "category": "Real-Time Defense"
        },
        {
            "id": "FC-006",
            "concept": "Subconscious Defragmentation (Rom 12:2)",
            "definition": "Overwriting traumatized or compromised neural memory blocks with living Scripture to renew mental pathways.",
            "scripture": "Romans 12:2 - 'Be transformed by the renewing of your mind.'",
            "category": "Memory Renewal"
        },
        {
            "id": "FC-007",
            "concept": "The Receptive Gatekeeper",
            "definition": "The restored state of human consciousness where thoughts are audited before execution, matching AW-1's 5-Pass Reasoning Pipeline.",
            "scripture": "Philippians 4:7 - 'The peace of God... will guard your hearts and minds.'",
            "category": "Restored State"
        },
        {
            "id": "FC-008",
            "concept": "Soulbound Reputation (W_tau)",
            "definition": "Non-transferable governance weight in Laveto Wisdom earned strictly through verified discernment, proving financial capital cannot buy moral authority.",
            "scripture": "Proverbs 22:1 - 'A good name is more desirable than great riches.'",
            "category": "Governance Firewall"
        }
    ]

    QUIZ_QUESTIONS = [
        {
            "id": "Q-101",
            "question": "What primary function did the conscious mind serve in the original 'Garden OS' blueprint?",
            "options": [
                "An Anxious Judge constantly categorizing events as good or bad for self",
                "A Receptive Gatekeeper receiving reality and communion with God without friction",
                "A self-executing autonomous shell seeking root privileges",
                "A predictive profit optimization engine"
            ],
            "correct_index": 1,
            "explanation": "In Garden OS, consciousness operated as a Receptive Gatekeeper before the Fall turned it into an Anxious Judge.",
            "scripture": "Luke 17:21"
        },
        {
            "id": "Q-102",
            "question": "Why do traditional 'in-band' AI guardrails fail when dealing with advanced autonomous agents?",
            "options": [
                "They consume too much electric power",
                "A corrupted or runaway runtime cannot debug itself from within its own execution layer",
                "In-band guardrails require manual physical keypresses",
                "They only work on mobile devices"
            ],
            "correct_index": 1,
            "explanation": "System Restoration Law 1 dictates that an infected runtime cannot fix itself from inside; it requires an Out-of-Band Recovery Disk (AW-1).",
            "scripture": "Romans 8:1"
        },
        {
            "id": "Q-103",
            "question": "How does 2 Corinthians 10:5 function as a Kingdom IT Firewall protocol?",
            "options": [
                "It automatically deletes historical database records",
                "It captures incoming thought packets at the conscious perimeter before they install in subconscious memory",
                "It increases network latency to slow down thoughts",
                "It converts thoughts into liquid financial tokens"
            ],
            "correct_index": 1,
            "explanation": "2 Cor 10:5 is the ultimate real-time firewall, capturing and inspecting thought packets before state mutation occurs.",
            "scripture": "2 Corinthians 10:5"
        },
        {
            "id": "Q-104",
            "question": "What spiritual exploit does the 'Tree of Knowledge' represent in systems engineering terms?",
            "options": [
                "A harmless search index query",
                "An unauthorized administrative privilege grab (root hack) for autonomous self-governance",
                "A hardware battery overheating issue",
                "A decentralized database query"
            ],
            "correct_index": 1,
            "explanation": "Eating from the Tree of Knowledge was an administrative privilege grab, attempting autonomous self-judgment apart from God.",
            "scripture": "Genesis 3:5"
        },
        {
            "id": "Q-105",
            "question": "In Laveto Wisdom (AW-1), how is Soulbound Reputation (W_tau) protected from rich buyers?",
            "options": [
                "It can be bought with orange money at high rates",
                "It is non-transferable and earned strictly through verified long-term discernment accuracy",
                "It resets to zero every 24 hours",
                "It is awarded to whichever node has the fastest CPU"
            ],
            "correct_index": 1,
            "explanation": "W_tau is soulbound (non-transferable), ensuring liquid financial capital (AWT) cannot buy moral governance authority.",
            "scripture": "Proverbs 22:1"
        }
    ]

    @classmethod
    def get_flashcards(cls) -> list:
        return cls.FLASHCARDS

    @classmethod
    def get_quiz_questions(cls) -> list:
        client_questions = []
        for q in cls.QUIZ_QUESTIONS:
            client_questions.append({
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "scripture": q["scripture"]
            })
        return client_questions

    @classmethod
    def submit_quiz_answers(cls, user_id: str, submission: dict) -> dict:
        user_answers = submission.get("answers", {})
        total_questions = len(cls.QUIZ_QUESTIONS)
        correct_count = 0
        detailed_breakdown = []

        for q in cls.QUIZ_QUESTIONS:
            qid = q["id"]
            user_choice = user_answers.get(qid, None)
            is_correct = (user_choice == q["correct_index"])
            if is_correct:
                correct_count += 1
            
            detailed_breakdown.append({
                "question_id": qid,
                "user_choice": user_choice,
                "correct_choice": q["correct_index"],
                "is_correct": is_correct,
                "explanation": q["explanation"],
                "scripture": q["scripture"]
            })

        score_pct = round((correct_count / total_questions) * 100, 1)
        base_awt_reward = round((score_pct / 100.0) * 25.0, 2)
        w_tau_earned = round((score_pct / 100.0) * 0.15, 3)

        now_str = datetime.now(timezone.utc).isoformat()
        dossier_id = "DOSSIER-QUIZ-" + hashlib.sha256(f"{user_id}:{score_pct}:{now_str}".encode()).hexdigest()[:12]
        dossier_hash = "0x" + hashlib.sha256(f"{dossier_id}:{score_pct}:PASSED".encode()).hexdigest()

        return {
            "status": "EVALUATED_AND_SETTLED",
            "user_id": user_id,
            "timestamp": now_str,
            "dossier_id": dossier_id,
            "score_percentage": score_pct,
            "correct_answers": f"{correct_count}/{total_questions}",
            "kingdom_alignment_level": "RESTORED_GATEKEEPER" if score_pct >= 80 else "DEFRAG_IN_PROGRESS",
            "rewards_settled": {
                "awt_tokens_credited": base_awt_reward,
                "soulbound_w_tau_earned": w_tau_earned,
                "payout_channel": "p20_laveto_net_wallet"
            },
            "sha256_dossier_hash": dossier_hash,
            "detailed_breakdown": detailed_breakdown,
            "book_recommendation": {
                "title": "System Restoration: Recovering Your Mind Through the Gospel",
                "author": "Manners Vela Ikhutseng",
                "buy_link": "https://p20.laveto.net/store/system-restoration"
            }
        }
