"""
End-to-End Adversarial Integration Tests for LinkedIn Automation Studio.
Tests the full lifecycle: topic selection -> copy formatting -> diagram generation -> safe publishing.
"""

from pathlib import Path
import pytest

from src.config.topics import TOPIC_POOL, get_topic_by_id
from src.engines.text_splitter import split_text_for_option
from src.engines.copy_engine import format_linkedin_post, score_text_authenticity
from src.engines.diagram_engine import generate_technical_diagram
from src.publishers.safety_guard import LinkedInSafetyGuard
from src.publishers.linkedin_client import LinkedInClient


class TestIntegrationAdversarial:
    @pytest.fixture
    def test_env(self, tmp_path):
        state_file = tmp_path / "integration_publish_state.json"
        guard = LinkedInSafetyGuard(state_file=state_file, cooldown_hours=20.0)
        client = LinkedInClient(access_token="", author_urn="", safety_guard=guard)
        return {"guard": guard, "client": client, "output_dir": tmp_path}

    def test_full_pipeline_with_cooldown_enforcement(self, test_env):
        guard = test_env["guard"]
        client = test_env["client"]
        out_dir = test_env["output_dir"]

        # 1. Topic Selection
        topic = get_topic_by_id("oauth")
        assert topic is not None
        assert "OAuth 2.0" in topic.title

        # 2. Text Splitter for Dropdown
        question = topic.questions[0]
        l1, l2 = split_text_for_option(question, max_line1=38, max_line2=95)
        assert len(l1) <= 38
        assert l2 is not None

        # 3. Authentic Post Copy Generation
        angle = topic.angles[0].text
        post_text = format_linkedin_post(
            topic_title=topic.title,
            subject=topic.subject,
            angle_content=angle,
            senior_question=question
        )
        assert "OAuth 2.0" in post_text
        assert "Google" in post_text

        # Authentic scoring check
        penalty, banned = score_text_authenticity(post_text)
        assert penalty == 0.0

        # 4. Diagram Generator
        diag_path = generate_technical_diagram(
            topic_id=topic.id,
            title=topic.title,
            tagline=topic.tagline,
            theme="cyan",
            output_dir=out_dir
        )
        assert diag_path.exists()

        # 5. First Publish Attempt (Simulation Mode)
        res1 = client.publish_post(text=post_text, media_path=diag_path)
        assert res1["success"] is True
        assert res1.get("simulation") is True

        # 6. Immediate Second Publish Attempt (Must be BLOCKED by Safety Guard)
        res2 = client.publish_post(text=post_text, media_path=diag_path)
        assert res2["success"] is False
        assert res2.get("cooldown_active") is True
        assert "Cooldown active" in res2["error"]

        # 7. Reset Cooldown State and Verify Re-enablement
        guard.reset_state()
        res3 = client.publish_post(text=post_text, media_path=diag_path)
        assert res3["success"] is True
