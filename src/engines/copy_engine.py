"""
Post Copy & Authentic Developer Voice Engine.
Generates relatable, high-engagement LinkedIn posts while penalizing corporate AI clichés.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field

# Banned AI tropes and preachy corporate clichés
BANNED_BUZZWORDS = [
    "delve", "testament", "unlock", "game-changer", "dive deep",
    "in today's fast-paced world", "revolutionize", "tapestry", "agree?",
    "let that sink in", "here is the thing", "unleash", "mastering",
    "synergy", "paradigm shift", "leverage", "disrupt"
]


@dataclass
class CandidatePost:
    angle_title: str
    hook: str
    body: str
    call_to_action: str
    scene_concept: str = ""
    scores: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0


def score_text_authenticity(text: str) -> Tuple[float, List[str]]:
    """
    Scans text for banned AI buzzwords and calculates a penalty.
    Returns (penalty_score, found_banned_words).
    """
    if not text:
        return 0.0, []

    lower = text.lower()
    found = [word for word in BANNED_BUZZWORDS if word in lower]
    penalty = len(found) * 3.0
    return penalty, found


def format_linkedin_post(
    topic_title: str,
    subject: str,
    angle_content: str,
    senior_question: str
) -> str:
    """
    Generates the final formatted LinkedIn post using the proven 4-stage high-engagement blueprint:
    1. Hook: Humble learning journey origin.
    2. Visual cue: Visual breakdown introduction.
    3. Core explanation: Clean, bulleted mental model.
    4. Senior question: Inviting real-world war stories from senior engineers.
    """
    hook_subj = (subject or topic_title or "System Design").strip()
    clean_angle = (angle_content or "").strip()
    clean_q = (senior_question or "What is your approach to this in production?").strip()

    return (
        f"When I first started learning system design, {hook_subj} sounded super intimidating.\n\n"
        f"I made this short visual breakdown to understand the mechanics step-by-step:\n\n"
        f"Here is what finally made it click for me:\n"
        f"{clean_angle}\n\n"
        f"Quick question for the senior engineers here:\n"
        f"👉 {clean_q}\n\n"
        f"Would love to know what is actually standard in production.\n\n"
        f"#systemdesign #backend #softwareengineering #learninginpublic"
    )


def score_candidate(candidate: Dict) -> CandidatePost:
    """Calculates weighted authenticity score for a post candidate."""
    hook = candidate.get("hook", "")
    body = candidate.get("body", "")
    full_text = f"{hook} {body}"

    penalty, _ = score_text_authenticity(full_text)

    raw_scores = candidate.get("scores", {})
    human_auth = float(raw_scores.get("human_authenticity", 8.0))
    simplicity = float(raw_scores.get("simplicity", 8.0))
    senior_eng = float(raw_scores.get("senior_engagement", 8.0))

    total = (human_auth * 0.4) + (simplicity * 0.3) + (senior_eng * 0.3) - penalty

    return CandidatePost(
        angle_title=candidate.get("angle_title", "Untitled"),
        hook=hook,
        body=body,
        call_to_action=candidate.get("call_to_action", ""),
        scene_concept=candidate.get("manim_scene_concept", ""),
        scores=raw_scores,
        total_score=round(total, 2)
    )


def select_champion_post(candidates: List[Dict]) -> CandidatePost:
    """Ranks candidate angles and returns the top-performing candidate."""
    if not candidates:
        return CandidatePost(
            angle_title="Fallback",
            hook="Default Hook",
            body="Default Body",
            call_to_action="Default Question",
            total_score=0.0
        )
    ranked = [score_candidate(c) for c in candidates]
    ranked.sort(key=lambda x: x.total_score, reverse=True)
    return ranked[0]
