"""
Unit Tests for 4-Slide LinkedIn Carousel Generator.
Verifies optical slide markup, 4:5 aspect ratio resolution,
and native multi-page PDF compilation.
"""

import os
import asyncio
from pathlib import Path
from PIL import Image

from src.engines.carousel_engine import (
    build_default_slides,
    build_carousel_slide_html,
    generate_carousel_async,
)


def test_build_default_slides_structure():
    """Verifies that default slides provide a 4-part narrative arc."""
    slides = build_default_slides("distributed_cache", "Distributed Cache Architecture")
    assert len(slides) == 4
    # Slide 1: Hook
    assert slides[0]["slide_number"] == 1
    assert "Distributed Cache Architecture" in slides[0]["title"]
    # Slide 2: Bottleneck / Breakage
    assert slides[1]["slide_number"] == 2
    assert "Bottleneck" in slides[1]["title"]
    # Slide 3: Fix with primitives
    assert slides[2]["slide_number"] == 3
    assert "Solution" in slides[2]["title"]
    assert "primitive-gateway" in slides[2]["stage_html"]
    # Slide 4: Staff Checklist
    assert slides[3]["slide_number"] == 4
    assert "Checklist" in slides[3]["title"]


def test_build_carousel_slide_html_placeholders():
    """Verifies all template placeholders are resolved with zero leaked mustache tags."""
    slides = build_default_slides("kafka_stream", "Kafka Stream Processing")
    html = build_carousel_slide_html(slides[0], theme="cyan", width=1080, height=1350)
    assert "{{TITLE}}" not in html
    assert "{{CANVAS_WIDTH}}" not in html
    assert "Kafka Stream Processing" in html
    assert "1080px" in html
    assert "1350px" in html


def test_generate_carousel_async_execution(tmp_path):
    """Verifies async generation of 4 PNG slides and multi-page PDF document."""
    async def _run():
        res = await generate_carousel_async(
            topic_id="test_saga",
            title="Saga Pattern Orchestration",
            output_dir=tmp_path,
            theme="cyan",
            overwrite=True
        )
        assert res["pdf"].exists()
        assert len(res["slides"]) == 4
        assert res["cover"].exists()

        # Check slide dimensions (1080x1350 portrait 4:5)
        for slide_p in res["slides"]:
            assert slide_p.exists()
            with Image.open(slide_p) as img:
                assert img.size == (1080, 1350)

        # Check PDF size is valid
        assert os.path.getsize(res["pdf"]) > 5000

    asyncio.run(_run())
