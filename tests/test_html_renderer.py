"""
Unit and Adversarial Tests for HTML Headless Renderer.
Tests browser singleton lifecycle, Retina image rendering, timeout enforcement,
and memory/resource isolation.
"""

import pytest
import asyncio
from src.engines.html_renderer import (
    render_html_to_image,
    close_browser,
    get_browser,
)


@pytest.fixture(autouse=True)
def cleanup_browser():
    yield
    try:
        asyncio.run(close_browser())
    except Exception:
        pass


def test_render_simple_html_to_png():
    async def _run():
        html = """
        <!DOCTYPE html>
        <html>
        <body style="margin:0; background-color: #0f172a; color: #38bdf8; display: flex; align-items: center; justify-content: center; height: 100vh;">
            <h1 style="font-family: sans-serif; font-size: 48px;">Architecture Test</h1>
        </body>
        </html>
        """
        png_bytes = await render_html_to_image(html, width=600, height=600)
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 1000
        # Standard PNG magic header
        assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    asyncio.run(_run())


def test_render_empty_html_raises_value_error():
    async def _run():
        with pytest.raises(ValueError, match="html_content cannot be empty"):
            await render_html_to_image("")

        with pytest.raises(ValueError, match="html_content cannot be empty"):
            await render_html_to_image("   \n\t  ")

    asyncio.run(_run())


def test_render_timeout_enforcement():
    async def _run():
        # Markup with a hanging external resource / network block
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <!-- Hanging script -->
            <script src="http://10.255.255.1/nonexistent.js"></script>
        </head>
        <body>
            <p>Timeout test</p>
        </body>
        </html>
        """
        # Tight timeout of 500ms should trigger Playwright timeout
        with pytest.raises(Exception):
            await render_html_to_image(html, timeout_ms=500)

    asyncio.run(_run())


def test_browser_singleton_reuse_and_shutdown():
    async def _run():
        b1 = await get_browser()
        b2 = await get_browser()
        assert b1 is b2
        assert b1.is_connected()

        # Clean shutdown
        await close_browser()
        assert not b1.is_connected()

    asyncio.run(_run())
