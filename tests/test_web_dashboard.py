"""
Tests for Streamlit Web Dashboard (app.py).
Verifies curated topic bindings, video registry mappings, and generation integrity.
"""

import pytest
from app import CURATED_TOPICS
from src.engines.video_engine import ANIMATION_REGISTRY
from src.engines.carousel_engine import resolve_topic_profile


def test_curated_topics_integrity():
    """Verifies all curated topics have valid labels, default titles, and valid video IDs."""
    assert len(CURATED_TOPICS) >= 12

    for topic_id, cfg in CURATED_TOPICS.items():
        assert "label" in cfg and len(cfg["label"]) > 5
        assert "default_title" in cfg and len(cfg["default_title"]) > 5
        assert "video_id" in cfg
        # Every video_id must exist in ANIMATION_REGISTRY
        assert cfg["video_id"] in ANIMATION_REGISTRY, f"Invalid video_id {cfg['video_id']} for topic {topic_id}"


def test_curated_topics_resolve_valid_profiles():
    """Verifies that each curated topic produces a rich, valid architectural profile."""
    for topic_id, cfg in CURATED_TOPICS.items():
        profile = resolve_topic_profile(topic_id, cfg["default_title"])
        assert "title" in profile
        assert "invariant" in profile and len(profile["invariant"]) > 10
        assert "rule_1" in profile and len(profile["rule_1"]) == 2
        assert "rule_2" in profile and len(profile["rule_2"]) == 2
        assert "gain" in profile and len(profile["gain"]) > 5
        assert "cost" in profile and len(profile["cost"]) > 5
        assert "metric_1" in profile
        assert "metric_2" in profile


def test_streamlit_app_loads_and_renders_cleanly():
    """Verifies that app.py initializes cleanly in Streamlit AppTest headless environment."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parent.parent / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run(timeout=10)

    # Verify no unhandled exceptions were raised
    assert not at.exception
    # Verify primary generate button is rendered
    assert len(at.button) >= 1
    assert any("generate" in b.label.lower() for b in at.button)
    # Verify radio selection for topic mode and format choice
    assert len(at.radio) >= 2

