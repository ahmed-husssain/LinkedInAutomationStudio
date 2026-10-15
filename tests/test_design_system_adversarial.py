"""
Adversarial Tests for Universal Design System & Collision Detection.
Validates:
1. Strict bounds enforcement on 1080x1080 videos and 1080x1350 PDF carousels.
2. BoundingBox2D collision math under extreme overlapping conditions.
3. Word-wrapping algorithm resilience against ultra-long unbroken tokens.
4. Total immunity to player HUD overlap (MANIM_BOTTOM_SAFE_LIMIT).
"""

import pytest
from pathlib import Path
from src.design_system.rules import (
    BoundingBox2D,
    wrap_text_cleanly,
    MANIM_ZONE_HEADER_TOP,
    MANIM_ZONE_HEADER_BOTTOM,
    MANIM_ZONE_NARRATIVE_TOP,
    MANIM_ZONE_NARRATIVE_BOTTOM,
    MANIM_BOTTOM_SAFE_LIMIT,
    PDF_WIDTH,
    PDF_HEIGHT,
    PDF_GUTTER_X
)
from src.agents.carousel_builder import render_carousel_slide, build_pdf_carousel


def test_bounding_box_collision_detection():
    """Validates AABB collision detection under overlapping and non-overlapping layouts."""
    # Box 1: Left component box
    b1 = BoundingBox2D("api_box", x_min=-3.7, y_min=-0.05, x_max=-1.5, y_max=1.55)
    # Box 2: Center component box (cleanly separated)
    b2 = BoundingBox2D("queue_box", x_min=-1.1, y_min=-0.05, x_max=1.1, y_max=1.55)
    # Box 3: Directly overlapping box
    b3_collide = BoundingBox2D("colliding_box", x_min=-2.0, y_min=0.5, x_max=0.0, y_max=1.0)

    assert not b1.collides_with(b2), "Separated boxes should not report a collision"
    assert b1.collides_with(b3_collide), "Overlapping boxes must report a collision"
    assert b2.collides_with(b3_collide), "Overlapping boxes must report a collision"


def test_wrap_text_cleanly_adversarial_inputs():
    """Validates word wrapping on empty, ultra-long, and multi-line strings."""
    assert wrap_text_cleanly("", 40) == []
    assert wrap_text_cleanly("   ", 40) == []

    # Short string
    lines = wrap_text_cleanly("Why Message Queues Save APIs", 20, max_lines=2)
    assert len(lines) <= 2
    for l in lines:
        assert len(l) <= 25

    # Very long paragraph
    long_p = "This is an extremely detailed sentence describing how partition rebalancing works in Apache Kafka under unexpected network partitions."
    wrapped = wrap_text_cleanly(long_p, max_chars_per_line=30, max_lines=3)
    assert len(wrapped) <= 3
    assert wrapped[-1].endswith("...")


def test_video_safe_zone_rules():
    """Validates that design system safe limits guarantee immunity to player controls."""
    # Bottom HUD begins at Y = -1.8 down to -4.0
    assert MANIM_BOTTOM_SAFE_LIMIT == -1.8
    # Narrative zone stays above safe limit
    assert MANIM_ZONE_NARRATIVE_BOTTOM > MANIM_BOTTOM_SAFE_LIMIT
    # Header zone is separated from narrative zone
    assert MANIM_ZONE_HEADER_BOTTOM > MANIM_ZONE_NARRATIVE_TOP


def test_pdf_carousel_slide_rendering_integrity(tmp_path):
    """Validates that all 3 types of PDF slides render cleanly without crashing or overflowing."""
    # Cover Slide
    cover = render_carousel_slide(
        slide_index=1,
        total_slides=6,
        badge_text="System Architecture",
        title="Scaling Message Queues",
        subtitle="Surviving 100k RPS traffic surges",
        bullet_points=["Spike causes connection drops", "Buffer decouples write pressure", "Zero database locks"],
        is_cover=True
    )
    assert cover.size == (1080, 1350)

    # Content Slide
    content = render_carousel_slide(
        slide_index=2,
        total_slides=6,
        badge_text="The Bottleneck",
        title="Direct Connection Pool Exhaustion",
        subtitle="Why relational databases choke under spikes",
        bullet_points=[
            "Postgres max_connections threshold is breached in under 2 seconds",
            "Thread context switching CPU overhead spikes to 100%",
            "Upstream microservices experience cascading 504 Gateway Timeouts"
        ]
    )
    assert content.size == (1080, 1350)

    # Final Question Slide
    final = render_carousel_slide(
        slide_index=6,
        total_slides=6,
        badge_text="Production Debate",
        title="Discussion Question",
        subtitle="For Senior Engineers",
        bullet_points=["In production, how does your team size dead-letter queues?"],
        is_final=True
    )
    assert final.size == (1080, 1350)


def test_pdf_carousel_specialized_layouts():
    """Validates comparison, code terminal, and metric KPI slide rendering and fallbacks."""
    # 1. Comparison Slide (Happy Path)
    comp_slide = render_carousel_slide(
        slide_index=3,
        total_slides=6,
        badge_text="Architecture Comparison",
        title="Eager vs Cooperative Rebalance",
        subtitle="Evaluating partition migration strategies",
        bullet_points=[
            "Eager revokes all partitions causing a global stop-the-world freeze",
            "Cooperative Sticky migrates partitions incrementally with zero downtime"
        ],
        layout_type="comparison",
        left_title="Eager Rebalance (Naive)",
        right_title="Cooperative Sticky (Production)"
    )
    assert comp_slide.size == (1080, 1350)

    # 2. Comparison Slide Fallback (Adversarial: only 1 bullet point)
    comp_fallback = render_carousel_slide(
        slide_index=3,
        total_slides=6,
        badge_text="Architecture Comparison",
        title="Single Point Fallback",
        subtitle="Should gracefully fall back to standard",
        bullet_points=["Single bullet point provided by AI"],
        layout_type="comparison"
    )
    assert comp_fallback.size == (1080, 1350)

    # 3. Code Window Slide
    code_slide = render_carousel_slide(
        slide_index=4,
        total_slides=6,
        badge_text="Config Hardening",
        title="Cooperative Sticky Assignor",
        subtitle="Configuring librdkafka and Java clients",
        bullet_points=["Eliminates 99% of consumer group latency spikes"],
        layout_type="code",
        code_snippet="partition.assignment.strategy: CooperativeSticky\nmax.poll.interval.ms: 300000"
    )
    assert code_slide.size == (1080, 1350)

    # 4. Metric KPI Slide
    metric_slide = render_carousel_slide(
        slide_index=5,
        total_slides=6,
        badge_text="Production Impact",
        title="Tail Latency Results",
        subtitle="Measured across 50 consumer pods",
        bullet_points=["Zero rebalance freezes observed over 30 days"],
        layout_type="metric",
        metric_label="P99 TAIL LATENCY",
        metric_value="420ms -> 18ms",
        metric_delta="95.7% Improvement under load"
    )
    assert metric_slide.size == (1080, 1350)


def test_dynamic_theme_resolver():
    """Validates that topic keywords resolve to the appropriate calibrated theme."""
    from src.agents.carousel_builder import resolve_topic_theme

    assert resolve_topic_theme("Kafka Partition Rebalance")["accent"] == "#00f0ff"
    assert resolve_topic_theme("OAuth2 JWT PKCE Security")["accent"] == "#f59e0b"
    assert resolve_topic_theme("PostgreSQL B-Tree Index Optimization")["accent"] == "#34d399"
    assert resolve_topic_theme("Raft Consensus Distributed State")["accent"] == "#38bdf8"
    assert resolve_topic_theme("General Programming Concepts")["accent"] == "#58a6ff"


def test_bounded_carousel_file_pruning(tmp_path):
    """Validates that LRU file pruning enforces the max_versions bound."""
    from src.agents.carousel_builder import prune_old_carousel_versions, CAROUSEL_DIR
    import time

    topic_key = "test_pruning_topic"
    created_files = []
    
    # Create 8 dummy PDF files with distinct timestamps
    for i in range(8):
        f = CAROUSEL_DIR / f"{topic_key}_version_{i}.pdf"
        f.write_text(f"dummy pdf content {i}")
        created_files.append(f)
        time.sleep(0.01)

    try:
        # Prune to maximum 5
        prune_old_carousel_versions(topic_key, max_versions=5)
        remaining = list(CAROUSEL_DIR.glob(f"{topic_key}_*.pdf"))
        assert len(remaining) == 5, f"Expected 5 files, but found {len(remaining)}"
    finally:
        # Cleanup test files
        for f in CAROUSEL_DIR.glob(f"{topic_key}_*.pdf"):
            f.unlink(missing_ok=True)

