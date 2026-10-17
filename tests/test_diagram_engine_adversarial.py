"""
Adversarial Tests for Technical Diagram Generator.
Tests missing fonts, boundary canvas dimensions, invalid themes, and ultra-long titles.
"""

from pathlib import Path
import pytest
from PIL import Image

from src.engines.diagram_engine import (
    generate_technical_diagram,
    resolve_font,
    THEMES,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
)


class TestDiagramEngineAdversarial:
    def test_resolve_font_with_invalid_paths(self):
        """When given non-existent paths, must fall back cleanly without raising FileNotFoundError."""
        bogus_paths = [
            "Z:/non/existent/path/font1.ttf",
            "/tmp/fake_font_does_not_exist.ttf"
        ]
        font = resolve_font(bogus_paths, size=24)
        assert font is not None

    def test_generate_diagram_with_extreme_inputs(self, tmp_path):
        """Ultra-long title, special characters, and unknown theme key."""
        huge_title = "A" * 300 + " 🚀 Special Character Test \u200b"
        img_path = generate_technical_diagram(
            topic_id="test_adversarial_topic",
            title=huge_title,
            tagline="Extreme boundary tagline test",
            theme="non_existent_neon_theme",  # Should fall back to cyan
            output_dir=tmp_path,
            overwrite=True
        )

        assert img_path.exists()
        assert img_path.is_file()

        # Validate image specs
        with Image.open(img_path) as img:
            assert img.size == (CANVAS_WIDTH, CANVAS_HEIGHT)
            assert img.mode == "RGB"

    def test_generate_diagram_all_themes(self, tmp_path):
        """All 4 standard themes must render valid 1080x1080 PNG images."""
        for theme_key in THEMES:
            out = generate_technical_diagram(
                topic_id=f"test_{theme_key}",
                title=f"Testing {theme_key.title()}",
                tagline="Theme validation",
                theme=theme_key,
                output_dir=tmp_path,
                overwrite=True
            )
            assert out.exists()

    def test_generate_diagram_html_fallback_to_pillow(self, tmp_path, monkeypatch):
        """When HTML rendering crashes or fails, diagram engine must fall back to Pillow seamlessly."""
        async def mock_fail(*args, **kwargs):
            raise RuntimeError("Simulated browser failure for fallback verification")

        monkeypatch.setattr("src.engines.html_renderer.render_html_to_image", mock_fail)

        out = generate_technical_diagram(
            topic_id="fallback_test",
            title="Fallback Verification",
            tagline="Pillow backup test",
            theme="emerald",
            output_dir=tmp_path,
            overwrite=True
        )
        assert out.exists()
        with Image.open(out) as img:
            assert img.size == (CANVAS_WIDTH, CANVAS_HEIGHT)

    def test_generate_technical_diagram_async(self, tmp_path):
        """Verify async entrypoint directly renders high-res card."""
        import asyncio
        from src.engines.diagram_engine import generate_technical_diagram_async

        async def _run():
            out = await generate_technical_diagram_async(
                topic_id="async_test_topic",
                title="Async Playwright Render",
                tagline="Testing direct coroutine pipeline",
                theme="purple",
                output_dir=tmp_path,
                overwrite=True
            )
            assert out.exists()
            with Image.open(out) as img:
                assert img.size == (CANVAS_WIDTH, CANVAS_HEIGHT)

        asyncio.run(_run())
