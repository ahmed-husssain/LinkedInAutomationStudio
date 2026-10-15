"""
PDF Carousel Architect for LinkedIn Document Posts.
Built on Universal Design System Rules:
- 1080x1350 vertical (4:5) mobile-optimized format
- Dynamic topic & difficulty-aware dark-mode palettes (Cyberpunk, Security, Database, Slate)
- Modular visual layouts: Comparison, Code Terminal, Metric KPI, and Standard 3-Card Stack
- Zero Font Tofu: 100% deterministic vector graphics (macOS dots, chevrons, checkmarks, crosses)
- Bounded LRU file versioning: Keeps latest 5 iterations per topic, preventing disk bloat
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from src.config.settings import ASSETS_DIR
from src.engines.diagram_engine import resolve_font, FONT_CANDIDATES_BOLD, FONT_CANDIDATES_REGULAR
from src.design_system.rules import (
    PDF_WIDTH,
    PDF_HEIGHT,
    PDF_GUTTER_X,
    COLOR_BG_DARK,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    ACCENT_CYAN,
    wrap_text_cleanly
)

logger = logging.getLogger("CarouselArchitect")

CAROUSEL_DIR = ASSETS_DIR / "carousels"
CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)

# Monospace font candidates for Terminal & Code windows
FONT_CANDIDATES_MONO = [
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/Library/Fonts/Courier New.ttf",
]


# =============================================================================
# 1. TOPIC & DIFFICULTY THEME PALETTES
# =============================================================================
THEME_PALETTES = {
    "cyberpunk": {  # High-throughput, Kafka, Streaming, Queues
        "bg_dark": "#0d0221",
        "card_bg": "#150a2e",
        "card_border": "#341e61",
        "accent": "#00f0ff",        # Electric Cyan
        "accent_secondary": "#ff007f", # Neon Magenta
        "badge_bg": "#241734",
    },
    "security": {   # OAuth, JWT, Tokens, Rate Limiting, Locks
        "bg_dark": "#121212",
        "card_bg": "#1c1c1c",
        "card_border": "#383838",
        "accent": "#f59e0b",        # Shield Amber
        "accent_secondary": "#ef4444", # Crimson Warning
        "badge_bg": "#2b2210",
    },
    "database": {   # SQL, PostgreSQL, Redis, Cache, Storage, Sharding
        "bg_dark": "#0a192f",
        "card_bg": "#112240",
        "card_border": "#233554",
        "accent": "#34d399",        # Mint Emerald
        "accent_secondary": "#38bdf8", # Ice Sky
        "badge_bg": "#0d2e24",
    },
    "distributed": { # Raft, Paxos, Microservices, Consensus
        "bg_dark": "#0b0f19",
        "card_bg": "#161f30",
        "card_border": "#2a3852",
        "accent": "#38bdf8",        # Sky Cyan
        "accent_secondary": "#818cf8", # Electric Violet
        "badge_bg": "#1e293b",
    },
    "default": {     # Fallback clean modern GitHub dark
        "bg_dark": COLOR_BG_DARK,
        "card_bg": COLOR_CARD_BG,
        "card_border": COLOR_CARD_BORDER,
        "accent": ACCENT_CYAN,
        "accent_secondary": "#3fb950",
        "badge_bg": "#1f242c",
    }
}

DIFFICULTY_BADGES = {
    "foundation": {"label": "LEVEL 1 • MENTAL MODEL", "color": "#34d399"},
    "production": {"label": "LEVEL 2 • PRODUCTION REALITY", "color": "#f59e0b"},
    "staff": {"label": "LEVEL 3 • STAFF ARCHITECT", "color": "#ff007f"},
}


def resolve_topic_theme(topic_str: str, override: Optional[str] = None) -> Dict[str, str]:
    """Dynamically determines the high-retention theme palette based on topic keywords."""
    if override and override.lower() in THEME_PALETTES:
        return THEME_PALETTES[override.lower()]

    lower = topic_str.lower()
    if re.search(r"\b(kafka|stream|queue|pubsub|event|rabbit|buffer|pipe|throughput|flow)\b", lower):
        return THEME_PALETTES["cyberpunk"]
    elif re.search(r"\b(oauth|jwt|auth|security|token|lock|ratelimit|shield|protect|key|crypto)\b", lower):
        return THEME_PALETTES["security"]
    elif re.search(r"\b(sql|postgres|database|db|cache|redis|shard|index|storage|acid|nosql)\b", lower):
        return THEME_PALETTES["database"]
    elif re.search(r"\b(raft|paxos|consensus|microservice|distributed|system|api|cluster|mesh)\b", lower):
        return THEME_PALETTES["distributed"]
    return THEME_PALETTES["default"]


# =============================================================================
# 2. PURE VECTOR GRAPHIC DRAWING PRIMITIVES (ZERO FONT TOFU)
# =============================================================================
def draw_macos_window_dots(draw: ImageDraw.ImageDraw, x: int, y: int, radius: int = 6, spacing: int = 18):
    """Draws macOS traffic-light window controls (Close, Minimize, Maximize) using vector circles."""
    colors = ["#ff5f56", "#ffbd2e", "#27c93f"]
    for i, color in enumerate(colors):
        cx = x + (i * spacing)
        draw.ellipse([cx - radius, y - radius, cx + radius, y + radius], fill=color)


def draw_vector_chevron(draw: ImageDraw.ImageDraw, x: int, y: int, color: str = "#58a6ff", size: int = 8):
    """Draws a clean directional chevron (>) using vector lines without relying on Unicode emojis."""
    draw.line([(x, y - size), (x + size, y), (x, y + size)], fill=color, width=3)


def draw_vector_check(draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 12, color: str = "#34d399"):
    """Draws a crisp green checkmark (✓) with vector lines."""
    draw.line([(x, y + (size // 2)), (x + (size // 3), y + size), (x + size, y)], fill=color, width=3)


def draw_vector_cross(draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 12, color: str = "#ef4444"):
    """Draws a crisp red cross (✕) with vector lines."""
    draw.line([(x, y), (x + size, y + size)], fill=color, width=3)
    draw.line([(x, y + size), (x + size, y)], fill=color, width=3)


def draw_vector_bullet(draw: ImageDraw.ImageDraw, x: int, y: int, color: str = "#58a6ff", radius: int = 5):
    """Draws a clean solid geometric bullet dot."""
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)


# =============================================================================
# 3. SPECIALIZED SLIDE LAYOUT RENDERERS
# =============================================================================
def render_standard_slide_cards(
    draw: ImageDraw.ImageDraw,
    bullet_points: List[str],
    accent_color: str,
    theme: Dict[str, str],
    font_bold_bullet: ImageFont.ImageFont,
    font_body: ImageFont.ImageFont
):
    """Standard 3-card stack with vector bullets and accent left borders."""
    card_start_y = 420
    count = min(3, len(bullet_points)) if bullet_points else 1
    card_h = 175
    spacing = 35

    for i in range(count):
        pt = bullet_points[i] if i < len(bullet_points) else "Key Architectural Point"
        cy = card_start_y + (i * (card_h + spacing))

        # Main Card Body
        draw.rounded_rectangle(
            [PDF_GUTTER_X, cy, PDF_WIDTH - PDF_GUTTER_X, cy + card_h],
            radius=16,
            fill=theme["card_bg"],
            outline=theme["card_border"],
            width=2
        )
        # Accent Bar on left border
        draw.rounded_rectangle(
            [PDF_GUTTER_X, cy + 12, PDF_GUTTER_X + 6, cy + card_h - 12],
            radius=3,
            fill=accent_color
        )

        # Vector Bullet Dot
        draw_vector_bullet(draw, PDF_GUTTER_X + 35, cy + 42, color=accent_color, radius=5)

        # Smart 2-line wrapped text
        wrapped = wrap_text_cleanly(pt, max_chars_per_line=50, max_lines=2)
        if wrapped:
            draw.text((PDF_GUTTER_X + 55, cy + 28), wrapped[0], fill=COLOR_TEXT_PRIMARY, font=font_bold_bullet)
            if len(wrapped) > 1:
                draw.text((PDF_GUTTER_X + 55, cy + 78), wrapped[1], fill=COLOR_TEXT_SECONDARY, font=font_body)


def render_comparison_slide_content(
    draw: ImageDraw.ImageDraw,
    bullet_points: List[str],
    accent_color: str,
    theme: Dict[str, str],
    left_title: str,
    right_title: str,
    font_bold_bullet: ImageFont.ImageFont,
    font_body: ImageFont.ImageFont
):
    """Side-by-side or stacked 2-block Comparison / Versus breakdown."""
    start_y = 410
    block_h = 320
    gap = 40

    # Top Block: The Naive / Anti-Pattern Approach
    cy_top = start_y
    draw.rounded_rectangle(
        [PDF_GUTTER_X, cy_top, PDF_WIDTH - PDF_GUTTER_X, cy_top + block_h],
        radius=16,
        fill=theme["card_bg"],
        outline="#ef4444",
        width=2
    )
    # Header tag for Block 1
    naive_tag = (left_title or "NAIVE ANTI-PATTERN / BOTTLENECK").upper()
    draw_vector_cross(draw, PDF_GUTTER_X + 35, cy_top + 32, size=16, color="#ef4444")
    draw.text((PDF_GUTTER_X + 65, cy_top + 28), naive_tag, fill="#ef4444", font=font_bold_bullet)

    # Content for Block 1
    pt1 = bullet_points[0] if bullet_points else "Direct synchronous blocking calls choke thread pools"
    wrapped1 = wrap_text_cleanly(pt1, max_chars_per_line=48, max_lines=3)
    for idx, line in enumerate(wrapped1):
        draw.text((PDF_GUTTER_X + 35, cy_top + 80 + (idx * 36)), line, fill=COLOR_TEXT_PRIMARY if idx == 0 else COLOR_TEXT_SECONDARY, font=font_body)

    # Bottom Block: The Production Solution
    cy_bottom = cy_top + block_h + gap
    draw.rounded_rectangle(
        [PDF_GUTTER_X, cy_bottom, PDF_WIDTH - PDF_GUTTER_X, cy_bottom + block_h],
        radius=16,
        fill=theme["card_bg"],
        outline="#34d399",
        width=2
    )
    # Header tag for Block 2
    prod_tag = (right_title or "PRODUCTION-GRADE ARCHITECTURE").upper()
    draw_vector_check(draw, PDF_GUTTER_X + 35, cy_bottom + 32, size=16, color="#34d399")
    draw.text((PDF_GUTTER_X + 65, cy_bottom + 28), prod_tag, fill="#34d399", font=font_bold_bullet)

    # Content for Block 2
    pt2 = bullet_points[1] if len(bullet_points) > 1 else "Asynchronous buffering guarantees sub-5ms client latency"
    wrapped2 = wrap_text_cleanly(pt2, max_chars_per_line=48, max_lines=3)
    for idx, line in enumerate(wrapped2):
        draw.text((PDF_GUTTER_X + 35, cy_bottom + 80 + (idx * 36)), line, fill=COLOR_TEXT_PRIMARY if idx == 0 else COLOR_TEXT_SECONDARY, font=font_body)


def render_code_window_content(
    draw: ImageDraw.ImageDraw,
    bullet_points: List[str],
    code_snippet: str,
    accent_color: str,
    theme: Dict[str, str],
    font_bold_bullet: ImageFont.ImageFont,
    font_body: ImageFont.ImageFont
):
    """Dark-mode terminal/code window with macOS controls and explanation card."""
    box_y = 390
    box_h = 420

    # Terminal Container
    draw.rounded_rectangle(
        [PDF_GUTTER_X, box_y, PDF_WIDTH - PDF_GUTTER_X, box_y + box_h],
        radius=16,
        fill="#080c14",
        outline=theme["card_border"],
        width=2
    )

    # Terminal Header Bar
    draw.rectangle([PDF_GUTTER_X + 2, box_y + 2, PDF_WIDTH - PDF_GUTTER_X - 2, box_y + 44], fill="#111827")
    draw_macos_window_dots(draw, PDF_GUTTER_X + 25, box_y + 22, radius=5, spacing=16)
    
    # Header label
    font_meta = resolve_font(FONT_CANDIDATES_REGULAR, 16)
    draw.text((PDF_WIDTH // 2 - 80, box_y + 14), "system-config.yaml", fill=COLOR_TEXT_MUTED, font=font_meta)

    # Monospace Code Text
    font_mono = resolve_font(FONT_CANDIDATES_MONO, 20)
    default_code = code_snippet or (
        "# Production Resilient Configuration\n"
        "partition.assignment.strategy: CooperativeSticky\n"
        "max.poll.interval.ms: 300000\n"
        "enable.auto.commit: false"
    )
    code_lines = default_code.strip().split("\n")[:8]
    for idx, cl in enumerate(code_lines):
        line_num = f"{idx + 1:2d} "
        draw.text((PDF_GUTTER_X + 30, box_y + 65 + (idx * 34)), line_num, fill="#4b5563", font=font_mono)
        draw.text((PDF_GUTTER_X + 80, box_y + 65 + (idx * 34)), cl[:46], fill=accent_color if ":" in cl else COLOR_TEXT_PRIMARY, font=font_mono)

    # Explanatory Takeaway Card below terminal
    card_y = box_y + box_h + 30
    draw.rounded_rectangle(
        [PDF_GUTTER_X, card_y, PDF_WIDTH - PDF_GUTTER_X, card_y + 240],
        radius=16,
        fill=theme["card_bg"],
        outline=accent_color,
        width=2
    )
    draw_vector_bullet(draw, PDF_GUTTER_X + 35, card_y + 35, color=accent_color, radius=5)
    draw.text((PDF_GUTTER_X + 55, card_y + 24), "PRODUCTION TAKEAWAY", fill=accent_color, font=font_bold_bullet)

    explanation = bullet_points[0] if bullet_points else "Prevents stop-the-world partition rebalances during rolling deployments"
    wrapped = wrap_text_cleanly(explanation, max_chars_per_line=48, max_lines=4)
    for idx, line in enumerate(wrapped):
        draw.text((PDF_GUTTER_X + 35, card_y + 75 + (idx * 36)), line, fill=COLOR_TEXT_PRIMARY if idx == 0 else COLOR_TEXT_SECONDARY, font=font_body)


def render_metric_callout_content(
    draw: ImageDraw.ImageDraw,
    bullet_points: List[str],
    accent_color: str,
    theme: Dict[str, str],
    metric_label: str,
    metric_value: str,
    metric_delta: str,
    font_bold_bullet: ImageFont.ImageFont,
    font_body: ImageFont.ImageFont
):
    """High-impact KPI / Metric callout slide."""
    box_y = 400
    box_h = 320

    # Big Metric Hero Card
    draw.rounded_rectangle(
        [PDF_GUTTER_X, box_y, PDF_WIDTH - PDF_GUTTER_X, box_y + box_h],
        radius=20,
        fill=theme["card_bg"],
        outline=accent_color,
        width=3
    )

    # Metric Sub-label
    label = (metric_label or "P99 TAIL LATENCY REDUCTION").upper()
    font_meta = resolve_font(FONT_CANDIDATES_BOLD, 22)
    draw.text((PDF_GUTTER_X + 40, box_y + 40), label, fill=COLOR_TEXT_SECONDARY, font=font_meta)

    # Big Giant Metric
    font_huge = resolve_font(FONT_CANDIDATES_BOLD, 68)
    val = metric_value or "420ms -> 18ms"
    draw.text((PDF_GUTTER_X + 40, box_y + 85), val, fill=accent_color, font=font_huge)

    # Delta badge pill
    delta = metric_delta or "95.7% Improvement under 100k RPS"
    draw.rounded_rectangle(
        [PDF_GUTTER_X + 40, box_y + 215, PDF_WIDTH - PDF_GUTTER_X - 40, box_y + 275],
        radius=12,
        fill="#1e293b",
        outline="#34d399",
        width=2
    )
    draw_vector_check(draw, PDF_GUTTER_X + 60, box_y + 235, size=14, color="#34d399")
    draw.text((PDF_GUTTER_X + 90, box_y + 233), delta, fill="#34d399", font=font_bold_bullet)

    # Detailed Points below
    detail_y = box_y + box_h + 40
    for idx, pt in enumerate(bullet_points[:2]):
        cy = detail_y + (idx * 160)
        draw.rounded_rectangle(
            [PDF_GUTTER_X, cy, PDF_WIDTH - PDF_GUTTER_X, cy + 130],
            radius=14,
            fill=theme["card_bg"],
            outline=theme["card_border"],
            width=2
        )
        draw_vector_bullet(draw, PDF_GUTTER_X + 35, cy + 35, color=accent_color, radius=5)
        wrapped = wrap_text_cleanly(pt, max_chars_per_line=48, max_lines=2)
        if wrapped:
            draw.text((PDF_GUTTER_X + 55, cy + 24), wrapped[0], fill=COLOR_TEXT_PRIMARY, font=font_bold_bullet)
            if len(wrapped) > 1:
                draw.text((PDF_GUTTER_X + 55, cy + 65), wrapped[1], fill=COLOR_TEXT_SECONDARY, font=font_body)


# =============================================================================
# 4. MASTER SLIDE COMPILER
# =============================================================================
def render_carousel_slide(
    slide_index: int,
    total_slides: int,
    badge_text: str,
    title: str,
    subtitle: str,
    bullet_points: List[str],
    accent_color: str = ACCENT_CYAN,
    is_cover: bool = False,
    is_final: bool = False,
    layout_type: str = "standard",
    code_snippet: str = "",
    left_title: str = "",
    right_title: str = "",
    metric_label: str = "",
    metric_value: str = "",
    metric_delta: str = "",
    difficulty: str = "production",
    diagram_nodes: Optional[List[str]] = None,
    theme: Optional[Dict[str, str]] = None
) -> Image.Image:
    """
    Renders a single high-contrast 1080x1350 dark-mode slide with zero overlapping text.
    Maintains 100% theme consistency across all slides in the deck.
    """
    if theme is None:
        theme = resolve_topic_theme(title)
    active_accent = accent_color if accent_color != ACCENT_CYAN else theme["accent"]

    img = Image.new("RGB", (PDF_WIDTH, PDF_HEIGHT), color=theme["bg_dark"])
    draw = ImageDraw.Draw(img)

    # 1. Outer Container Border Card with subtle accent glow
    draw.rounded_rectangle(
        [40, 40, PDF_WIDTH - 40, PDF_HEIGHT - 40],
        radius=24,
        fill=theme["card_bg"],
        outline=theme["card_border"],
        width=3
    )

    # 2. Typography
    font_title = resolve_font(FONT_CANDIDATES_BOLD, 52 if is_cover else 40)
    font_sub = resolve_font(FONT_CANDIDATES_REGULAR, 26)
    font_badge = resolve_font(FONT_CANDIDATES_BOLD, 20)
    font_body = resolve_font(FONT_CANDIDATES_REGULAR, 24)
    font_bold_bullet = resolve_font(FONT_CANDIDATES_BOLD, 26)
    font_meta = resolve_font(FONT_CANDIDATES_REGULAR, 20)

    # 3. Slide Counter (Top Right)
    draw.text(
        (PDF_WIDTH - 150, 80),
        f"{slide_index} / {total_slides}",
        fill=COLOR_TEXT_SECONDARY,
        font=font_meta
    )

    # 4. Badge Pill (Top Left: Y = 75 to 125)
    clean_badge = badge_text.strip().upper()[:30]
    badge_width = max(240, min(440, len(clean_badge) * 16 + 50))
    draw.rounded_rectangle(
        [PDF_GUTTER_X, 75, PDF_GUTTER_X + badge_width, 125],
        radius=14,
        fill=theme["badge_bg"],
        outline=active_accent,
        width=2
    )
    draw.text((PDF_GUTTER_X + 24, 87), clean_badge, fill=active_accent, font=font_badge)

    # 5. Title & Subtitle Zone (Y: 180 to 350)
    title_lines = wrap_text_cleanly(title, max_chars_per_line=32 if is_cover else 38, max_lines=2)
    start_y = 190 if not is_cover else 260
    for idx, tl in enumerate(title_lines):
        draw.text((PDF_GUTTER_X, start_y + (idx * 58)), tl, fill=COLOR_TEXT_PRIMARY, font=font_title)

    sub_y = start_y + (len(title_lines) * 58) + 15
    if subtitle:
        sub_lines = wrap_text_cleanly(subtitle, max_chars_per_line=50, max_lines=2)
        for idx, sl in enumerate(sub_lines):
            draw.text((PDF_GUTTER_X, sub_y + (idx * 36)), sl, fill=COLOR_TEXT_SECONDARY, font=font_sub)

    # 6. Main Content Area Dispatcher
    if is_cover:
        # Cover Hero Slide with Difficulty Badge and Preview Cards
        box_y = 480
        draw.rounded_rectangle(
            [PDF_GUTTER_X, box_y, PDF_WIDTH - PDF_GUTTER_X, box_y + 540],
            radius=18,
            fill=theme["bg_dark"],
            outline=active_accent,
            width=2
        )

        # Difficulty Tag inside Cover
        diff_info = DIFFICULTY_BADGES.get(difficulty.lower(), DIFFICULTY_BADGES["production"])
        draw.rounded_rectangle(
            [PDF_GUTTER_X + 35, box_y + 35, PDF_GUTTER_X + 410, box_y + 85],
            radius=10,
            fill=theme["card_bg"],
            outline=diff_info["color"],
            width=2
        )
        draw.text((PDF_GUTTER_X + 50, box_y + 47), diff_info["label"], fill=diff_info["color"], font=font_badge)

        # 3 Preview bullets with vector dots (no emojis)
        for i, pt in enumerate(bullet_points[:3]):
            cy = box_y + 125 + (i * 125)
            draw_vector_bullet(draw, PDF_GUTTER_X + 45, cy + 12, color=active_accent, radius=6)
            draw.text((PDF_GUTTER_X + 68, cy), pt[:48], fill=COLOR_TEXT_PRIMARY, font=font_bold_bullet)
            if len(pt) > 48:
                draw.text((PDF_GUTTER_X + 68, cy + 36), pt[48:105], fill=COLOR_TEXT_SECONDARY, font=font_body)

        # Bottom Swipe Prompt with vector chevrons
        swipe_x = PDF_WIDTH // 2 - 120
        draw.text((swipe_x, 1180), "SWIPE FOR ARCHITECTURE", fill=active_accent, font=font_bold_bullet)
        draw_vector_chevron(draw, swipe_x + 295, 1195, color=active_accent, size=10)

    elif is_final:
        # Final Discussion Question Slide with vector speech/debate styling
        box_y = 380
        draw.rounded_rectangle(
            [PDF_GUTTER_X, box_y, PDF_WIDTH - PDF_GUTTER_X, box_y + 640],
            radius=18,
            fill=theme["bg_dark"],
            outline=active_accent,
            width=2
        )
        # Vector question header
        draw_vector_bullet(draw, PDF_GUTTER_X + 40, box_y + 55, color=active_accent, radius=6)
        draw.text((PDF_GUTTER_X + 60, box_y + 40), "SENIOR PRODUCTION DEBATE:", fill=active_accent, font=font_bold_bullet)

        question_text = bullet_points[0] if bullet_points else "In production, how does your team scale this architecture?"
        q_lines = wrap_text_cleanly(question_text, max_chars_per_line=34, max_lines=5)
        for j, ql in enumerate(q_lines):
            draw.text((PDF_GUTTER_X + 40, box_y + 120 + (j * 54)), ql, fill=COLOR_TEXT_PRIMARY, font=font_title)

        # Call to action footer
        draw.text((PDF_GUTTER_X + 40, box_y + 530), "Drop your war stories in the comments ->", fill=COLOR_TEXT_SECONDARY, font=font_sub)

    else:
        # Content Slide Dispatcher with defensive fallbacks
        layout = (layout_type or "standard").lower()

        if layout == "comparison" and len(bullet_points) >= 2:
            render_comparison_slide_content(
                draw, bullet_points, active_accent, theme,
                left_title, right_title, font_bold_bullet, font_body
            )
        elif layout == "code" and (code_snippet or len(bullet_points) > 0):
            render_code_window_content(
                draw, bullet_points, code_snippet, active_accent, theme,
                font_bold_bullet, font_body
            )
        elif layout == "metric" and (metric_value or len(bullet_points) > 0):
            render_metric_callout_content(
                draw, bullet_points, active_accent, theme,
                metric_label, metric_value, metric_delta, font_bold_bullet, font_body
            )
        else:
            # Universal Fallback: Standard 3-card stack
            render_standard_slide_cards(
                draw, bullet_points, active_accent, theme,
                font_bold_bullet, font_body
            )

        # Next Slide navigation cue with vector chevron
        cue_x = PDF_WIDTH - 260
        draw.text((cue_x, 1220), "Next Slide", fill=COLOR_TEXT_SECONDARY, font=font_meta)
        draw_vector_chevron(draw, cue_x + 95, 1230, color=COLOR_TEXT_SECONDARY, size=8)

    # 7. Bottom Navigation & Footer Zone (Y: 1260)
    draw.text((PDF_GUTTER_X, 1260), "LinkedIn Engineering Series • Save & Repost", fill=COLOR_TEXT_MUTED, font=font_meta)

    return img


# =============================================================================
# 5. BOUNDED VERSION PRUNING & PDF COMPILER
# =============================================================================
def prune_old_carousel_versions(topic_slug: str, max_versions: int = 5):
    """
    Bounded LRU File Pruner: Keeps the latest N versions of a topic's carousel,
    deleting older iterations to prevent unbounded disk growth.
    """
    try:
        existing_files = sorted(
            CAROUSEL_DIR.glob(f"{topic_slug}_*.pdf"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        for old_file in existing_files[max_versions:]:
            try:
                old_file.unlink(missing_ok=True)
                logger.info("Pruned older carousel version: %s", old_file.name)
            except OSError as err:
                logger.debug("Could not unlink %s: %s", old_file, err)
    except Exception as e:
        logger.debug("Pruner skipped due to: %s", e)


def build_pdf_carousel(
    topic_id: str,
    topic_title: str,
    slides_data: List[Dict],
    senior_question: str = "",
    difficulty: str = "production",
    theme_override: Optional[str] = None
) -> Path:
    """
    Assembles all slides and compiles them into a single high-resolution PDF document.
    Saves a timestamped version for instant Discord delivery and maintains a canonical copy.
    """
    total = len(slides_data) + 2
    rendered_images: List[Image.Image] = []

    # Resolve theme once for the entire carousel deck to guarantee 100% visual consistency
    deck_theme = resolve_topic_theme(topic_title, override=theme_override)
    deck_accent = deck_theme["accent"]

    # 1. Cover Slide
    cover_bullets = [s.get("title", "") for s in slides_data[:3]]
    cover_img = render_carousel_slide(
        slide_index=1,
        total_slides=total,
        badge_text="System Architecture",
        title=topic_title,
        subtitle="A 60-Second Visual Mental Model",
        bullet_points=cover_bullets,
        accent_color=deck_accent,
        is_cover=True,
        difficulty=difficulty,
        theme=deck_theme
    )
    rendered_images.append(cover_img)

    # 2. Content Slides (Sharing exact same deck_theme)
    for idx, s in enumerate(slides_data):
        slide_num = idx + 2
        slide_accent = s.get("accent") if s.get("accent") and s.get("accent") != ACCENT_CYAN else deck_accent
        slide_img = render_carousel_slide(
            slide_index=slide_num,
            total_slides=total,
            badge_text=s.get("badge", "Key Concept"),
            title=s.get("title", f"Concept {idx+1}"),
            subtitle=s.get("subtitle", ""),
            bullet_points=s.get("bullets", []),
            accent_color=slide_accent,
            layout_type=s.get("layout_type", "standard"),
            code_snippet=s.get("code_snippet", ""),
            left_title=s.get("left_title", ""),
            right_title=s.get("right_title", ""),
            metric_label=s.get("metric_label", ""),
            metric_value=s.get("metric_value", ""),
            metric_delta=s.get("metric_delta", ""),
            difficulty=difficulty,
            theme=deck_theme
        )
        rendered_images.append(slide_img)

    # 3. Final Discussion Question Slide (Sharing exact same deck_theme)
    final_q = senior_question or "In production, what is your team's standard approach for handling this?"
    final_img = render_carousel_slide(
        slide_index=total,
        total_slides=total,
        badge_text="Production Debate",
        title="Discussion Question",
        subtitle="For Senior & Staff Engineers",
        bullet_points=[final_q],
        accent_color=deck_theme.get("accent_secondary", "#34d399"),
        is_final=True,
        difficulty=difficulty,
        theme=deck_theme
    )
    rendered_images.append(final_img)

    # 4. Save Timestamped & Canonical Multi-Page PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_pdf_path = CAROUSEL_DIR / f"{topic_id}_{timestamp}.pdf"
    canonical_pdf_path = CAROUSEL_DIR / f"{topic_id}_Carousel_Deck.pdf"

    first_page = rendered_images[0]
    # Save the timestamped version (busts Discord cache)
    first_page.save(
        out_pdf_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=rendered_images[1:]
    )

    # Also save/update the canonical path for backwards-compatibility
    try:
        first_page.save(
            canonical_pdf_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=rendered_images[1:]
        )
    except Exception as e:
        logger.debug("Could not write canonical pdf: %s", e)

    # 5. Enforce Bounded Storage (keep latest 5 versions)
    prune_old_carousel_versions(topic_id, max_versions=5)

    return out_pdf_path
