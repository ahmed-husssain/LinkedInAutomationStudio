"""
Unit Tests for Adaptive 3-to-5 Slide LinkedIn Carousel Generator.
Verifies topic complexity resolution (3, 4, 5 slides), optical typography,
full-width 880px vector topology, and multi-page PDF compilation.
"""

import os
import asyncio
from pathlib import Path
from PIL import Image

from src.engines.carousel_engine import (
    resolve_carousel_slide_count,
    build_adaptive_slides,
    build_default_slides,
    build_carousel_slide_html,
    generate_carousel_async,
)


def test_resolve_carousel_slide_count():
    """Verifies topic complexity resolves strictly between 3 and 5 slides."""
    # 3 Slides: Isolated algorithms & mental models
    assert resolve_carousel_slide_count("token_bucket", "Token Bucket Rate Limiter") == 3
    assert resolve_carousel_slide_count("circuit_breaker", "Circuit Breaker Pattern") == 3
    assert resolve_carousel_slide_count("consistent_hash", "Consistent Hashing Algorithm") == 3

    # 4 Slides: Standard incidents and architectures
    assert resolve_carousel_slide_count("kafka_rebalance", "Kafka Partition Rebalancing") == 4
    assert resolve_carousel_slide_count("postgres_locks", "PostgreSQL Lock Contention Under Load") == 4

    # 5 Slides: High-scale lifecycles & multi-region consensus
    assert resolve_carousel_slide_count("scaling_websockets", "10 Million Sockets: Scaling WebSockets") == 5
    assert resolve_carousel_slide_count("multi_region_raft", "Multi-Region Distributed Consensus Raft") == 5
    assert resolve_carousel_slide_count("db_migration", "Zero-Downtime Database Migration Lifecycle") == 5


def test_build_adaptive_slides_structure():
    """Verifies rich multi-tier content in 3, 4, and 5 slide narrative arcs."""
    # 1. 3-Slide Arc
    slides3 = build_adaptive_slides("token_bucket", "Token Bucket Limiter", slide_count=3)
    assert len(slides3) == 3
    assert slides3[0]["slide_number"] == 1
    assert "scale-matrix" in slides3[0]["stage_html"]
    assert "full-topology-svg" in slides3[1]["stage_html"]
    assert "tradeoff-grid" in slides3[2]["stage_html"]

    # 2. 4-Slide Arc
    slides4 = build_adaptive_slides("kafka_stream", "Kafka Stream Architecture", slide_count=4)
    assert len(slides4) == 4
    assert "config-specimen" in slides4[1]["stage_html"]
    assert "full-topology-svg" in slides4[2]["stage_html"]

    # 3. 5-Slide Arc
    slides5 = build_adaptive_slides("10m_sockets", "10 Million Sockets", slide_count=5)
    assert len(slides5) == 5
    assert "scale-matrix" in slides5[0]["stage_html"]
    assert "config-specimen" in slides5[1]["stage_html"]
    assert "full-topology-svg" in slides5[2]["stage_html"]
    assert "sequence-flow-svg" in slides5[3]["stage_html"]
    assert "tradeoff-grid" in slides5[3]["stage_html"]
    assert "/etc/sysctl.conf" in slides5[4]["stage_html"]


def test_build_carousel_slide_html_placeholders():
    """Verifies all template placeholders are resolved without leaked mustache tags."""
    slides = build_adaptive_slides("websockets", "10 Million Sockets", slide_count=5)
    html = build_carousel_slide_html(slides[0], theme="cyan", width=1080, height=1350, total_slides=5)
    assert "{{TITLE}}" not in html
    assert "{{CANVAS_WIDTH}}" not in html
    assert "{{STAGE_HTML}}" not in html
    assert "10 Million Sockets" in html
    assert "1080px" in html
    assert "1350px" in html
    assert "1 / 5" in html


def test_generate_carousel_async_3_and_5_slides(tmp_path):
    """Verifies async generation of 3-slide and 5-slide carousels into multi-page PDFs."""
    async def _run():
        # Test 5-slide generation (10 Million Sockets)
        res5 = await generate_carousel_async(
            topic_id="ws_10m",
            title="10 Million Sockets",
            output_dir=tmp_path,
            theme="cyan",
            overwrite=True,
            slide_count=5
        )
        assert res5["pdf"].exists()
        assert len(res5["slides"]) == 5
        assert res5["total_slides"] == 5
        assert os.path.getsize(res5["pdf"]) > 5000

        # Verify slide 1 dimensions (1080x1350)
        with Image.open(res5["slides"][0]) as img:
            assert img.size == (1080, 1350)

        # Test 3-slide generation (Token Bucket)
        res3 = await generate_carousel_async(
            topic_id="token_bucket",
            title="Token Bucket Limiter",
            output_dir=tmp_path,
            theme="emerald",
            overwrite=True,
            slide_count=3
        )
        assert res3["pdf"].exists()
        assert len(res3["slides"]) == 3
        assert res3["total_slides"] == 3

    asyncio.run(_run())
