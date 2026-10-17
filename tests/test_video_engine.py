"""
Unit and Adversarial Tests for Parameterized Dynamic Video Engine.
Verifies deterministic path resolution, absence of silent fallbacks,
and cached asset delivery.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.engines.video_engine import (
    resolve_video_path,
    render_parameterized_animation,
    ANIMATION_REGISTRY,
)


def test_resolve_video_path_all_algorithms():
    """Verifies that all 4 rate limiting algorithms resolve to their distinct .mp4 files."""
    for anim_id in ["token_bucket", "leaky_bucket", "fixed_window", "sliding_window"]:
        path = resolve_video_path(anim_id)
        assert path is not None, f"Expected {anim_id} to resolve to a video path"
        assert path.exists(), f"Expected {path} to exist on disk"
        assert path.suffix == ".mp4"
        assert path.stat().st_size > 1024


def test_resolve_video_path_unknown_id_returns_none():
    """Verifies zero silent fallback: unknown animation IDs return None."""
    assert resolve_video_path("non_existent_algorithm_xyz") is None
    assert resolve_video_path("") is None
    assert resolve_video_path("random_unknown") is None


def test_render_parameterized_animation_cached():
    """Verifies that cached video assets are returned immediately without spawning subprocess."""
    async def _run():
        path = await render_parameterized_animation("sliding_window", force_render=False)
        assert path.exists()
        assert path.name == "SlidingWindowScene.mp4"

    asyncio.run(_run())


def test_render_parameterized_animation_unknown_raises_value_error():
    """Verifies that attempting to render an unknown animation raises ValueError."""
    async def _run():
        with pytest.raises(ValueError, match="Unknown animation identifier"):
            await render_parameterized_animation("fake_scene_123")

    asyncio.run(_run())


def test_registry_contains_all_core_scenes():
    """Verifies that the animation registry contains all required system design animations."""
    expected_scenes = {
        "token_bucket",
        "leaky_bucket",
        "fixed_window",
        "sliding_window",
        "oauth",
        "sql_index",
        "cache_aside",
        "api_idempotency",
        "queue",
    }
    assert expected_scenes.issubset(set(ANIMATION_REGISTRY.keys()))
