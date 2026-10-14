"""
High-Resolution Technical Diagram Generator (1080x1080).
Creates crisp, professional system design architecture cards with dynamic themes
and resilient cross-platform font resolution.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont

from src.config.settings import THUMBNAILS_DIR, CANVAS_WIDTH, CANVAS_HEIGHT

THEMES = {
    "cyan": {"accent": "#58a6ff", "name": "Cyan High-Contrast"},
    "emerald": {"accent": "#3fb950", "name": "Emerald Dark"},
    "purple": {"accent": "#bc8cff", "name": "Neon Purple"},
    "amber": {"accent": "#e3b341", "name": "Warm Amber"},
}

# Platform-independent font candidate lookup
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
            except Exception:
                continue
    try:
        # Fallback to standard truetype if font name is known to system
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def generate_technical_diagram(
    topic_id: str,
    title: str,
    tagline: str = "",
    theme: str = "cyan",
    output_dir: Optional[Path] = None,
    overwrite: bool = False
) -> Path:
    """
    Generates a crisp 1080x1080 dark-mode technical diagram for a topic.

    Args:
        topic_id: Unique slug identifier for the topic.
        title: Post topic title.
        tagline: Short description or problem hook.
        theme: Color theme key ('cyan', 'emerald', 'purple', 'amber').
        output_dir: Target directory (defaults to assets/thumbnails).
        overwrite: Whether to re-render if cached file exists.

    Returns:
        Path to the saved PNG image.
    """
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

    # Title & Subtitle with truncation guard
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

    # 3 Architectural cards
    step_y = box_top + 35
    card_h = box_bottom - step_y - 35
    steps = [
        ("1. The Problem", "High latency or\nunexpected server\nfailure under load", "#f85149"),
        ("2. Architecture", "Decoupled logic\nor in-memory cache\nhandles requests", accent_color),
        ("3. The Outcome", "Fast throughput\nZero data loss\nHigh availability", "#3fb950"),
    ]

    card_w = (width - 180 - 60) // 3
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
