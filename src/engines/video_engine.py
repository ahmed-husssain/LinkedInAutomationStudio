"""
Parameterized Dynamic Video Engine.
Provides deterministic resolution, parameter schema injection, and
asynchronous rendering for Manim CE system design animations.
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Video storage root
VIDEO_DIR = Path("assets/videos")

# Strict mapping of animation identifiers to Manim scene classes and video filenames
ANIMATION_REGISTRY: Dict[str, Dict[str, str]] = {
    "token_bucket": {
        "file": "src/animations/rate_limiter.py",
        "scene": "TokenBucketScene",
        "output": "TokenBucketScene.mp4",
        "title": "Token Bucket Rate Limiter",
    },
    "leaky_bucket": {
        "file": "src/animations/rate_limiter.py",
        "scene": "LeakyBucketScene",
        "output": "LeakyBucketScene.mp4",
        "title": "Leaky Bucket Rate Limiter",
    },
    "fixed_window": {
        "file": "src/animations/rate_limiter.py",
        "scene": "FixedWindowScene",
        "output": "FixedWindowScene.mp4",
        "title": "Fixed Window Rate Limiter",
    },
    "sliding_window": {
        "file": "src/animations/rate_limiter.py",
        "scene": "SlidingWindowScene",
        "output": "SlidingWindowScene.mp4",
        "title": "Sliding Window Rate Limiter",
    },
    "oauth": {
        "file": "src/animations/oauth.py",
        "scene": "OAuthScene",
        "output": "OAuthScene.mp4",
        "title": "OAuth 2.0 Auth Flow",
    },
    "sql_index": {
        "file": "src/animations/sql_index.py",
        "scene": "SqlIndexScene",
        "output": "SqlIndexScene.mp4",
        "title": "B-Tree Database Indexing",
    },
    "cache_aside": {
        "file": "src/animations/cache_aside.py",
        "scene": "CacheAsideScene",
        "output": "CacheAsideScene.mp4",
        "title": "Cache-Aside Architecture",
    },
    "api_idempotency": {
        "file": "src/animations/idempotency.py",
        "scene": "IdempotencyScene",
        "output": "IdempotencyScene.mp4",
        "title": "API Idempotency Keys",
    },
    "queue": {
        "file": "src/animations/queue.py",
        "scene": "QueueScene",
        "output": "QueueScene.mp4",
        "title": "Message Queue Decoupling",
    },
}


def resolve_video_path(animation_id: str) -> Optional[Path]:
    """
    Deterministically resolves the video file path for a given animation_id.
    Zero silent fallback: returns None if the animation is unknown or missing.
    """
    if not animation_id or not animation_id.strip():
        return None

    clean_id = animation_id.strip().lower()

    if clean_id not in ANIMATION_REGISTRY:
        # Check if animation_id is a direct filename
        direct_path = VIDEO_DIR / animation_id.strip()
        if direct_path.is_file() and direct_path.stat().st_size > 1024:
            return direct_path
        return None

    entry = ANIMATION_REGISTRY[clean_id]
    target_path = VIDEO_DIR / entry["output"]
    if target_path.is_file() and target_path.stat().st_size > 1024:
        return target_path

    return None


async def render_parameterized_animation(
    animation_id: str,
    params: Optional[Dict[str, Any]] = None,
    force_render: bool = False
) -> Path:
    """
    Renders or resolves a Manim animation deterministically.
    If pre-rendered video is available and force_render is False, returns existing file.
    Otherwise, executes Manim CE via non-blocking asyncio subprocess.
    """
    if animation_id not in ANIMATION_REGISTRY:
        raise ValueError(
            f"Unknown animation identifier '{animation_id}'. "
            f"Supported animations: {list(ANIMATION_REGISTRY.keys())}"
        )

    entry = ANIMATION_REGISTRY[animation_id]
    target_path = VIDEO_DIR / entry["output"]

    # If cached file exists and re-render is not requested, return immediately
    if not force_render and target_path.exists() and target_path.stat().st_size > 1024:
        logger.info(f"Serving pre-rendered animation asset: {target_path}")
        return target_path

    logger.info(f"Compiling Manim scene '{entry['scene']}' from {entry['file']}...")

    cmd = [
        sys.executable,
        "-m",
        "manim",
        "-ql",  # 720p 30fps fast compilation for rapid bot delivery
        "--media_dir",
        "assets/videos/media",
        entry["file"],
        entry["scene"],
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err_msg = stderr.decode().strip() or stdout.decode().strip()
        logger.error(f"Manim render failed for {animation_id}: {err_msg}")
        raise RuntimeError(f"Manim render error for '{animation_id}': {err_msg[:300]}")

    if not target_path.exists():
        raise FileNotFoundError(f"Expected rendered video at {target_path}, but not found after compilation.")

    return target_path
