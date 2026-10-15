"""
The Content Strategist & Hook Architect Agent.
Uses Gemini Pro to generate high-retention LinkedIn engineering angles,
slide-by-slide carousel breakdowns, and authentic developer copy.
"""

import json
import logging
from typing import Dict, Any, List
from src.agents.gemini_client import GeminiClient

logger = logging.getLogger("ContentStrategist")

STRATEGIST_SYSTEM_PROMPT = """
You are a Staff Technical Content Strategist & Authentic Developer Ghostwriter.
You write for senior engineers and ambitious developers on LinkedIn.

STRICT WRITING RULES:
1. Tone: Humble, curious, clear, and excited about how computer systems actually work under the hood.
2. The Hook: Start with a real production problem, a mistake you used to make, or a confusing misconception.
3. The Breakdown: Explain step-by-step with clear mental models. Use bullet points only for mechanics.
4. The Senior Question: End with a specific, technical question directed at senior engineers (e.g. partition sizing, TTL strategies, caching invalidation). Seniors LOVE debating production war stories in the comments.
5. ANTI-AI BANNED WORDS: Never use 'delve', 'unlock', 'game-changer', 'tapestry', 'synergy', 'revolutionize', 'agree?', or 'in today's fast-paced world'.

You MUST return valid JSON matching this schema:
{
  "topic_title": "string (max 38 chars)",
  "subject": "string",
  "difficulty": "foundation | production | staff",
  "hook": "string",
  "body": "string",
  "senior_question": "string",
  "slides": [
    {
      "badge": "string (e.g. The Problem, Architecture, Flow, Tradeoffs)",
      "title": "string (max 32 chars)",
      "subtitle": "string (max 50 chars)",
      "bullets": ["string", "string"],
      "accent": "string (hex color: #58a6ff, #f85149, #3fb950, #bc8cff, #e3b341, #00f0ff, #f59e0b)",
      "layout_type": "standard | comparison | code | metric (pick the most visual layout for this concept)",
      "code_snippet": "string (optional, config or code snippet if layout_type is code)",
      "left_title": "string (optional, e.g. Naive Approach if layout_type is comparison)",
      "right_title": "string (optional, e.g. Production Fix if layout_type is comparison)",
      "metric_label": "string (optional, e.g. p99 Tail Latency if layout_type is metric)",
      "metric_value": "string (optional, e.g. 420ms -> 18ms if layout_type is metric)",
      "metric_delta": "string (optional, e.g. 95% reduction under load)"
    }
  ]
}
"""


class ContentStrategistAgent:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or GeminiClient()

    def brainstorm_topic(self, user_prompt: str) -> Dict[str, Any]:
        """Brainstorms and drafts a full content package for any technical concept."""
        prompt = (
            f"Generate a top 1% system design breakdown for LinkedIn based on this topic/request:\n"
            f"'{user_prompt}'\n\n"
            f"Include: an authentic post copy, a senior engineer discussion question, "
            f"and 4-5 content slides for an interactive PDF carousel."
        )

        response_text = self.client.generate(
            prompt=prompt,
            system_instruction=STRATEGIST_SYSTEM_PROMPT,
            json_mode=True,
            topic_hint=user_prompt
        )

        try:
            # Strip markdown code fences if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned.strip())
            from src.agents.schemas import PostPackageSchema
            validated = PostPackageSchema(**parsed)
            return validated.model_dump()
        except Exception:
            # Fallback default structure
            return {
                "topic_title": user_prompt[:35],
                "subject": user_prompt,
                "hook": f"When I first started learning about {user_prompt}, it sounded intimidating.",
                "body": f"Here is the step-by-step breakdown that finally made {user_prompt} click for me:\n• Concept 1: Core mechanics\n• Concept 2: High throughput\n• Concept 3: Zero data loss",
                "senior_question": f"In production, how does your team manage {user_prompt} under peak load?",
                "slides": [
                    {
                        "badge": "The Problem",
                        "title": "Traffic Spikes",
                        "subtitle": "Why synchronous APIs fail under load",
                        "bullets": ["Spike causes 10x connection timeouts", "Database locks up on heavy concurrent writes", "Users experience 504 Gateway errors"],
                        "accent": "#f85149"
                    },
                    {
                        "badge": "Architecture",
                        "title": "Decoupled Buffer",
                        "subtitle": "Asynchronous persistence layer",
                        "bullets": ["Requests land instantly in memory/disk buffer", "API returns 202 Accepted in under 5ms", "Consumers process at a controlled rate"],
                        "accent": "#58a6ff"
                    },
                    {
                        "badge": "The Outcome",
                        "title": "High Availability",
                        "subtitle": "Resilience against sudden spikes",
                        "bullets": ["Zero dropped user requests", "Database CPU remains steady at 40%", "Downstream outages do not drop transactions"],
                        "accent": "#3fb950"
                    }
                ]
            }

    def refine_draft(self, draft: Dict[str, Any], critique: str) -> Dict[str, Any]:
        """Iterative review loop: refines draft incorporating Staff Engineer critique."""
        prompt = (
            f"Here is a draft post & slide deck:\n{json.dumps(draft)}\n\n"
            f"A Staff Engineer provided this critical feedback:\n'{critique}'\n\n"
            f"Revise the draft to incorporate this feedback, elevating technical precision. "
            f"Return the updated JSON matching the schema."
        )
        response_text = self.client.generate(
            prompt=prompt,
            system_instruction=STRATEGIST_SYSTEM_PROMPT,
            json_mode=True,
            topic_hint=draft.get("topic_title", "Technical Architecture")
        )
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned.strip())
            from src.agents.schemas import PostPackageSchema
            validated = PostPackageSchema(**parsed)
            return validated.model_dump()
        except Exception:
            return draft

    def discover_trending_topics(self, count: int = 3) -> List[Dict[str, str]]:
        """
        Dynamically discovers viral, incident-driven architecture topics
        inspired by high-stakes outages, Big Tech engineering blogs, and real benchmarks.
        """
        prompt = (
            f"Generate {count} unique, viral, top-1% system architecture topics for LinkedIn. "
            f"Focus on real-world engineering war stories, counter-intuitive production bugs, "
            f"or deep internal mechanics that senior engineers love debating (e.g. Netflix, Discord, Stripe, Uber, Cloudflare).\n"
            f"Return JSON list: [{{'title': '...', 'tagline': '...', 'hook': '...', 'why_it_works': '...'}}]"
        )
        response_text = self.client.generate(
            prompt=prompt,
            system_instruction=(
                "You are the Lead Content Strategist for top tech influencers (like ByteByteGo / Alex Xu). "
                "Never suggest generic beginner topics like 'what is an array' or 'basic oauth'. "
                "Suggest gripping, high-retention topics about real distributed systems trade-offs."
            ),
            json_mode=True
        )
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned.strip())
            if isinstance(parsed, list) and len(parsed) >= 1:
                return parsed[:count]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as err:
            logger.debug("Failed parsing AI trending topics JSON, using curated pool: %s", err)

        # High-retention curated fallback
        return [
            {
                "title": "The Thundering Herd: How Cache Stampedes Melt Redis",
                "tagline": "Why 10,000 simultaneous cache misses crash databases (and how XFetch prevents it).",
                "hook": "Our Redis cluster hit 100% CPU when a single popular cache key expired during peak traffic.",
                "why_it_works": "Piques curiosity on mutual exclusion locking vs XFetch early expiration."
            },
            {
                "title": "Why UUIDv4 Primary Keys Silently Destroy Postgres B-Trees",
                "tagline": "Random 128-bit page splits vs time-sequential UUIDv7.",
                "hook": "We couldn't figure out why our Postgres insert throughput dropped by 80% as the table grew past 50GB.",
                "why_it_works": "Debates deep storage engine mechanics and B-Tree cache locality."
            },
            {
                "title": "Kafka Partition Rebalance Storms: Eager vs Cooperative Assignors",
                "tagline": "The 45-second consumer freeze that halts entire microservice fleets.",
                "hook": "Every time a single consumer pod restarted, all message consumption stopped completely across the cluster.",
                "why_it_works": "Senior Kafka engineers have experienced this exact outage in production."
            }
        ]
