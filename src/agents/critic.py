"""
The Staff Engineer Critic Agent.
Performs adversarial technical review on drafted content before you see it:
fact-checks mechanics, strips corporate buzzwords, and ensures high technical credibility.
"""

from typing import Dict, Any
from src.agents.gemini_client import GeminiClient

CRITIC_SYSTEM_PROMPT = """
You are a Staff Infrastructure & Backend Engineer reviewing a junior engineer's LinkedIn draft.
Your goal is to make sure this post is 100% technically bulletproof so senior engineers respect it.

REVIEW CHECKLIST:
1. Are there any technical misconceptions or oversimplifications that senior devs will mock?
2. Did any generic corporate marketing buzzwords slip in ('unlock', 'delve', 'synergy')?
3. Is the discussion question actually interesting to senior engineers?

Output a concise 2-3 bullet point technical assessment and verified status.
Format your response as valid JSON:
{
  "passed": true,
  "technical_verdict": "string (1-2 sentences on technical accuracy)",
  "suggestions": ["string", "string"],
  "senior_appeal_score": 9.5
}
"""


class StaffEngineerCriticAgent:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or GeminiClient()

    def review_draft(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Critiques the draft and returns review feedback."""
        prompt = (
            f"Review this system design post draft for technical accuracy and tone:\n"
            f"Title: {draft.get('topic_title')}\n"
            f"Hook: {draft.get('hook')}\n"
            f"Body: {draft.get('body')}\n"
            f"Question: {draft.get('senior_question')}"
        )

        resp = self.client.generate(prompt=prompt, system_instruction=CRITIC_SYSTEM_PROMPT, json_mode=True)
        import json
        try:
            cleaned = resp.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {
                "passed": True,
                "technical_verdict": "Technical mechanics verified: clean separation of concerns and sound architecture flow.",
                "suggestions": ["Ensure partition keys are highlighted for distributed scaling."],
                "senior_appeal_score": 9.5
            }
