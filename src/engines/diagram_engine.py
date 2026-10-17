"""
High-Resolution Technical Diagram Generator (1080x1080).
Creates ByteByteGo / Stripe-grade architecture cards using headless HTML/Tailwind
rendering via Playwright, with zero-regression fallback to Pillow.
"""

import os
import asyncio
import concurrent.futures
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont

from src.config.settings import THUMBNAILS_DIR, CANVAS_WIDTH, CANVAS_HEIGHT

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "architecture_diagram.html"

THEMES = {
    "cyan": {
        "accent": "#38bdf8",
        "glow": "rgba(56, 189, 248, 0.22)",
        "name": "Cyan High-Contrast"
    },
    "emerald": {
        "accent": "#34d399",
        "glow": "rgba(52, 211, 153, 0.22)",
        "name": "Emerald Dark"
    },
    "purple": {
        "accent": "#c084fc",
        "glow": "rgba(192, 132, 252, 0.22)",
        "name": "Neon Purple"
    },
    "amber": {
        "accent": "#fbbf24",
        "glow": "rgba(251, 191, 36, 0.22)",
        "name": "Warm Amber"
    },
}

FONT_CANDIDATES_BOLD = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]

FONT_CANDIDATES_REGULAR = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]


def resolve_font(candidates: list, size: int) -> ImageFont.ImageFont:
    """Tries candidate font paths; falls back safely to default if none exist."""
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(str(path), size)
            except (OSError, IOError):
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()


@lru_cache(maxsize=1)
def _load_html_template() -> str:
    """Loads and caches the HTML diagram template."""
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")


def _build_html_markup(topic_id: str, title: str, tagline: str, theme: str) -> str:
    """Substitutes theme variables and topic text into the HTML template."""
    raw_template = _load_html_template()
    theme_data = THEMES.get(theme.lower(), THEMES["cyan"])
    accent = theme_data["accent"]
    glow = theme_data["glow"]

    clean_title = (title or topic_id).strip()[:50]
    clean_tagline = (tagline or "Production Architecture & High-Scale Resilience").strip()[:80]

    # Dynamic tier mapping based on topic
    tier1_title = "Client Application"
    tier1_sub = "Mobile Apps, Single-Page Apps & Public API Consumers"
    tier2_title = f"{clean_title.split(':')[0] if ':' in clean_title else 'API Gateway & Edge'}"
    tier2_sub = "TLS Termination, Rate Limiting & Auth Verification"
    tier3_title = "Decoupled Microservice Cluster"
    tier3_sub = "Distributed Event Stream & Async Processing"
    tier4_title = "Storage & Cache Tier"
    tier4_sub = "In-Memory Cache (Redis) + Sharded Relational Database"

    # Contextual adjustments for known topics
    tid = topic_id.lower()
    if "rate_limiter" in tid or "token" in tid:
        tier2_title = "Token Bucket Rate Limiter"
        tier2_sub = "In-memory token counter with 2ms burst clearance"
        tier4_title = "Redis Clustered Key-Value"
        tier4_sub = "Sub-millisecond sliding window & token tracking"
    elif "oauth" in tid or "auth" in tid:
        tier2_title = "OAuth 2.0 Auth Server + PKCE"
        tier2_sub = "Validates code_verifier against code_challenge SHA-256"
        tier4_title = "Encrypted Token Store"
        tier4_sub = "RS256 Private/Public Key Pairs & Scoped Refresh Tokens"
    elif "sql" in tid or "index" in tid:
        tier3_title = "Query Planner & Engine"
        tier3_sub = "B-Tree Index Scan vs Full Table Scan Cost Estimator"
        tier4_title = "High-Throughput Storage Engine"
        tier4_sub = "Clustered primary keys on NVMe SSD with WAL"

    rendered = raw_template
    replacements = {
        "{{THEME_ACCENT}}": accent,
        "{{THEME_GLOW}}": glow,
        "{{BADGE_TEXT}}": "SYSTEM DESIGN ARCHITECTURE",
        "{{TITLE}}": clean_title,
        "{{TAGLINE}}": clean_tagline,
        "{{TIER1_TITLE}}": tier1_title,
        "{{TIER1_SUB}}": tier1_sub,
        "{{TIER2_TITLE}}": tier2_title,
        "{{TIER2_SUB}}": tier2_sub,
        "{{TIER3_TITLE}}": tier3_title,
        "{{TIER3_SUB}}": tier3_sub,
        "{{TIER4_TITLE}}": tier4_title,
        "{{TIER4_SUB}}": tier4_sub,
        "{{FOOTER_TEXT}}": "LinkedIn Automation Studio • Architecture Deep Dive",
    }
    for placeholder, val in replacements.items():
        rendered = rendered.replace(placeholder, val)
    return rendered


async def generate_technical_diagram_async(
    topic_id: str,
    title: str,
    tagline: str = "",
    theme: str = "cyan",
    output_dir: Optional[Path] = None,
    overwrite: bool = False
) -> Path:
    """
    Renders a high-res architecture diagram via headless Chromium HTML template.
    Falls back to Pillow if Playwright fails.
    """
    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / f"{topic_id}_Diagram_{theme}.png"

    if out_file.exists() and not overwrite:
        return out_file

    try:
        from src.engines.html_renderer import render_html_to_image
        html_markup = _build_html_markup(topic_id, title, tagline, theme)
        png_bytes = await render_html_to_image(
            html_markup,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            timeout_ms=6000
        )
        out_file.write_bytes(png_bytes)
        return out_file
    except Exception as exc:
        logger.warning(
            f"HTML diagram render failed for '{topic_id}' ({exc}). Falling back to Pillow engine."
        )
        return _generate_diagram_pillow(topic_id, title, tagline, theme, output_dir, overwrite)


def _generate_diagram_pillow(
    topic_id: str,
    title: str,
    tagline: str = "",
    theme: str = "cyan",
    output_dir: Optional[Path] = None,
    overwrite: bool = False
) -> Path:
    """Pillow fallback generator: guarantees 100% resilient rendering even without browser."""
    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    theme_data = THEMES.get(theme.lower(), THEMES["cyan"])
    accent_color = theme_data["accent"]

    out_file = target_dir / f"{topic_id}_Diagram_{theme}.png"
    if out_file.exists() and not overwrite:
        return out_file

    width, height = CANVAS_WIDTH, CANVAS_HEIGHT
    img = Image.new("RGB", (width, height), color="#0d1117")
    draw = ImageDraw.Draw(img)

    # Outer border card
    draw.rounded_rectangle(
        [40, 40, width - 40, height - 40],
        radius=24,
        fill="#161b22",
        outline="#30363d",
        width=3
    )

    # Fonts
    font_bold = resolve_font(FONT_CANDIDATES_BOLD, 46)
    font_sub = resolve_font(FONT_CANDIDATES_REGULAR, 30)
    font_badge = resolve_font(FONT_CANDIDATES_BOLD, 22)
    font_step = resolve_font(FONT_CANDIDATES_BOLD, 24)
    font_step_body = resolve_font(FONT_CANDIDATES_REGULAR, 22)
    font_footer = resolve_font(FONT_CANDIDATES_REGULAR, 24)

    # Badge Pill
    draw.rounded_rectangle(
        [90, 85, 460, 137],
        radius=14,
        fill="#1f242c",
        outline=accent_color,
        width=2
    )
    draw.text((110, 97), "SYSTEM DESIGN EXPLAINED", fill=accent_color, font=font_badge)

    clean_title = (title or topic_id)[:40]
    clean_tagline = (tagline or "Technical Architecture Breakdown")[:55]

    draw.text((90, 175), clean_title, fill="#ffffff", font=font_bold)
    draw.text((90, 245), clean_tagline, fill="#8b949e", font=font_sub)

    # Central Architecture Area
    box_top = 340
    box_bottom = 900
    draw.rounded_rectangle(
        [90, box_top, width - 90, box_bottom],
        radius=18,
        fill="#0d1117",
        outline="#21262d",
        width=2
    )

    card_w = (width - 180 - 60) // 3
    step_y = box_top + 35
    card_h = box_bottom - step_y - 35
    steps = [
        ("1. The Problem", "High latency or\nunexpected server\nfailure under load", "#f85149"),
        ("2. Architecture", "Decoupled logic\nor in-memory cache\nhandles requests", accent_color),
        ("3. The Outcome", "Fast throughput\nZero data loss\nHigh availability", "#3fb950"),
    ]

    for i, (stitle, sdesc, scolor) in enumerate(steps):
        cx = 120 + i * (card_w + 30)
        draw.rounded_rectangle(
            [cx, step_y, cx + card_w, step_y + card_h],
            radius=14,
            fill="#161b22",
            outline=scolor,
            width=2
        )
        draw.text((cx + 16, step_y + 22), stitle, fill=scolor, font=font_step)
        draw.text((cx + 16, step_y + 75), sdesc, fill="#ffffff", font=font_step_body)

    # Footer
    draw.text(
        (90, 940),
        "Technical Architecture Breakdown • Swipe for Senior Discussion",
        fill="#8b949e",
        font=font_footer
    )

    img.save(out_file)
    return out_file


def generate_technical_diagram(
    topic_id: str,
    title: str,
    tagline: str = "",
    theme: str = "cyan",
    output_dir: Optional[Path] = None,
    overwrite: bool = False
) -> Path:
    """
    Synchronous entrypoint for technical diagram generation.
    Attempts modern HTML rendering; falls back to Pillow if headless browser fails.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is None:
            return asyncio.run(generate_technical_diagram_async(
                topic_id, title, tagline, theme, output_dir, overwrite
            ))
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    lambda: asyncio.run(generate_technical_diagram_async(
                        topic_id, title, tagline, theme, output_dir, overwrite
                    ))
                ).result(timeout=10)
    except Exception as exc:
        logger.warning(f"Synchronous HTML diagram render fallback triggered: {exc}")
        return _generate_diagram_pillow(topic_id, title, tagline, theme, output_dir, overwrite)
