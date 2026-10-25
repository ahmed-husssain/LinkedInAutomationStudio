"""
High-Performance Headless HTML-to-Image Renderer via Playwright.
Provides lazy-singleton Chromium lifecycle management, bounded timeouts,
and zero-leak in-memory snapshotting.
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Playwright

_playwright_instance: Optional[Playwright] = None
_browser_instance: Optional[Browser] = None
_running_loop: Optional[asyncio.AbstractEventLoop] = None
_lock: Optional[asyncio.Lock] = None


def _get_lock() -> asyncio.Lock:
    global _lock
    loop = asyncio.get_running_loop()
    if _lock is None or _running_loop != loop:
        _lock = asyncio.Lock()
    return _lock


async def get_browser() -> Browser:
    """Lazily initializes and returns the shared headless Chromium browser singleton."""
    global _playwright_instance, _browser_instance, _running_loop
    loop = asyncio.get_running_loop()
    lock = _get_lock()

    if _running_loop is loop and _browser_instance is not None and _browser_instance.is_connected():
        return _browser_instance

    async with lock:
        if _running_loop is loop and _browser_instance is not None and _browser_instance.is_connected():
            return _browser_instance

        # Loop changed or instance uninitialized: start clean
        _browser_instance = None
        _playwright_instance = None
        _running_loop = loop

        _playwright_instance = await async_playwright().start()
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-sync",
            "--disable-translate",
            "--hide-scrollbars",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
        ]
        try:
            _browser_instance = await _playwright_instance.chromium.launch(
                headless=True,
                args=launch_args,
            )
        except Exception as exc:
            if "executable doesn't exist" in str(exc).lower() or "playwright install" in str(exc).lower():
                import sys
                import subprocess
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                _browser_instance = await _playwright_instance.chromium.launch(
                    headless=True,
                    args=launch_args,
                )
            else:
                raise
        return _browser_instance


async def render_html_to_image(
    html_content: str,
    width: int = 1080,
    height: int = 1080,
    timeout_ms: int = 7000,
    device_scale_factor: int = 1,
) -> bytes:
    """
    Renders an HTML string to a PNG image in memory.

    Args:
        html_content: Raw HTML markup with inline CSS or linked stylesheets.
        width: Viewport width in pixels (default 1080).
        height: Viewport height in pixels (default 1080).
        timeout_ms: Maximum duration in milliseconds before timing out.
        device_scale_factor: Viewport zoom scale (1 for 1:1 pixel mapping).

    Returns:
        Raw PNG bytes.
    """
    if not html_content or not html_content.strip():
        raise ValueError("html_content cannot be empty")

    browser = await get_browser()
    context = await browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=device_scale_factor,
    )
    page = await context.new_page()

    try:
        await page.set_content(
            html_content,
            wait_until="domcontentloaded",
            timeout=timeout_ms
        )
        png_bytes = await page.screenshot(
            type="png",
            clip={"x": 0, "y": 0, "width": width, "height": height},
            timeout=timeout_ms
        )
        return png_bytes
    finally:
        # ponytail: context.close() cleanly purges both page and cache in 1 call
        await context.close()


async def close_browser() -> None:
    """Cleanly shuts down the shared browser instance and Playwright runtime."""
    global _playwright_instance, _browser_instance, _running_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    # If the browser was bound to an older event loop that has closed,
    # attempting to await its close methods on a new loop hangs forever in Playwright.
    if _running_loop is not None and current_loop is not None and _running_loop is not current_loop:
        _browser_instance = None
        _playwright_instance = None
        _running_loop = None
        return

    lock = _get_lock()
    async with lock:
        if _browser_instance is not None:
            try:
                await asyncio.wait_for(_browser_instance.close(), timeout=3.0)
            except Exception:
                pass
            _browser_instance = None

        if _playwright_instance is not None:
            try:
                await asyncio.wait_for(_playwright_instance.stop(), timeout=3.0)
            except Exception:
                pass
            _playwright_instance = None

        # Allow proactor/epoll pipe transports to cleanly flush
        try:
            await asyncio.sleep(0.05)
        except Exception:
            pass
        _running_loop = None
