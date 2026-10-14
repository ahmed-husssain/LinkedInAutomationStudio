"""
PDF Carousel Architect for LinkedIn Document Posts.
Built on Universal Design System Rules:
- 1080x1350 vertical (4:5) format
- Dynamic word-boundary text wrapping (zero crude string clipping)
- Strict vertical budget zones preventing bullet card collisions
- Consistent high-contrast dark theme (#0d1117 / #161b22)
"""

from pathlib import Path
from typing import List, Dict, Optional
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

CAROUSEL_DIR = ASSETS_DIR / "carousels"
CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)


def render_carousel_slide(
    slide_index: int,
    total_slides: int,
    badge_text: str,
    title: str,
    subtitle: str,
    bullet_points: List[str],
    accent_color: str = ACCENT_CYAN,
    is_cover: bool = False,
    is_final: bool = False
) -> Image.Image:
    """Renders a single high-contrast 1080x1350 dark-mode slide with zero overlapping text."""
    img = Image.new("RGB", (PDF_WIDTH, PDF_HEIGHT), color=COLOR_BG_DARK)
    draw = ImageDraw.Draw(img)

    # 1. Outer Container Border Card
    draw.rounded_rectangle(
        [40, 40, PDF_WIDTH - 40, PDF_HEIGHT - 40],
        radius=24,
        fill=COLOR_CARD_BG,
        outline=COLOR_CARD_BORDER,
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
    badge_width = max(240, min(420, len(clean_badge) * 16 + 50))
    draw.rounded_rectangle(
        [PDF_GUTTER_X, 75, PDF_GUTTER_X + badge_width, 125],
        radius=14,
        fill="#1f242c",
        outline=accent_color,
        width=2
    )
    draw.text((PDF_GUTTER_X + 24, 87), clean_badge, fill=accent_color, font=font_badge)

    # 5. Title & Subtitle Zone (Y: 180 to 340)
    title_lines = wrap_text_cleanly(title, max_chars_per_line=32 if is_cover else 38, max_lines=2)
    start_y = 190 if not is_cover else 300
    for idx, tl in enumerate(title_lines):
        draw.text((PDF_GUTTER_X, start_y + (idx * 58)), tl, fill=COLOR_TEXT_PRIMARY, font=font_title)

    sub_y = start_y + (len(title_lines) * 58) + 15
    if subtitle:
        sub_lines = wrap_text_cleanly(subtitle, max_chars_per_line=50, max_lines=2)
        for idx, sl in enumerate(sub_lines):
            draw.text((PDF_GUTTER_X, sub_y + (idx * 36)), sl, fill=COLOR_TEXT_SECONDARY, font=font_sub)

    # 6. Main Content Area (Y: 420 to 1150)
    if is_cover:
        box_y = 540
        draw.rounded_rectangle(
            [PDF_GUTTER_X, box_y, PDF_WIDTH - PDF_GUTTER_X, box_y + 440],
            radius=18,
            fill=COLOR_BG_DARK,
            outline="#21262d",
            width=2
        )
        for i, pt in enumerate(bullet_points[:3]):
            cy = box_y + 45 + (i * 125)
            draw.text((PDF_GUTTER_X + 40, cy), f"👉  {pt[:48]}", fill=COLOR_TEXT_PRIMARY, font=font_bold_bullet)
            if len(pt) > 48:
                draw.text((PDF_GUTTER_X + 75, cy + 36), pt[48:105], fill=COLOR_TEXT_SECONDARY, font=font_body)

        draw.text((PDF_WIDTH // 2 - 80, 1180), "Swipe 👉", fill=accent_color, font=font_bold_bullet)

    elif is_final:
        box_y = 380
        draw.rounded_rectangle(
            [PDF_GUTTER_X, box_y, PDF_WIDTH - PDF_GUTTER_X, box_y + 600],
            radius=18,
            fill=COLOR_BG_DARK,
            outline=accent_color,
            width=2
        )
        draw.text((PDF_GUTTER_X + 40, box_y + 50), "💬 Senior Discussion Question:", fill=accent_color, font=font_bold_bullet)

        question_text = bullet_points[0] if bullet_points else "In production, how does your team scale this architecture?"
        q_lines = wrap_text_cleanly(question_text, max_chars_per_line=34, max_lines=5)
        for j, ql in enumerate(q_lines):
            draw.text((PDF_GUTTER_X + 40, box_y + 120 + (j * 52)), ql, fill=COLOR_TEXT_PRIMARY, font=font_title)

        draw.text((PDF_GUTTER_X + 40, box_y + 490), "Drop your war stories in the comments ⬇️", fill=COLOR_TEXT_SECONDARY, font=font_sub)

    else:
        # Standard Content Slide: Maximum 3-4 structured cards with clean spacing
        card_start_y = 420
        usable_height = 700
        count = min(3, len(bullet_points)) if bullet_points else 1
        card_h = 170
        spacing = 35

        for i in range(count):
            pt = bullet_points[i] if i < len(bullet_points) else ""
            cy = card_start_y + (i * (card_h + spacing))

            draw.rounded_rectangle(
                [PDF_GUTTER_X, cy, PDF_WIDTH - PDF_GUTTER_X, cy + card_h],
                radius=14,
                fill=COLOR_BG_DARK,
                outline=COLOR_CARD_BORDER,
                width=2
            )

            # Smart 2-line wrapped text inside card
            wrapped = wrap_text_cleanly(pt, max_chars_per_line=52, max_lines=2)
            if wrapped:
                draw.text((PDF_GUTTER_X + 35, cy + 35), f"•  {wrapped[0]}", fill=COLOR_TEXT_PRIMARY, font=font_bold_bullet)
                if len(wrapped) > 1:
                    draw.text((PDF_GUTTER_X + 62, cy + 85), wrapped[1], fill=COLOR_TEXT_SECONDARY, font=font_body)

        draw.text((PDF_WIDTH - 240, 1220), "Next Slide 👉", fill=COLOR_TEXT_SECONDARY, font=font_meta)

    # 7. Bottom Navigation & Footer Zone (Y: 1260)
    draw.text((PDF_GUTTER_X, 1260), "LinkedIn Engineering Series • Save & Repost", fill=COLOR_TEXT_MUTED, font=font_meta)

    return img


def build_pdf_carousel(
    topic_id: str,
    topic_title: str,
    slides_data: List[Dict],
    senior_question: str = ""
) -> Path:
    """Assembles all slides and compiles them into a single high-resolution PDF document."""
    total = len(slides_data) + 2
    rendered_images: List[Image.Image] = []

    # 1. Cover Slide
    cover_bullets = [s.get("title", "") for s in slides_data[:3]]
    cover_img = render_carousel_slide(
        slide_index=1,
        total_slides=total,
        badge_text="System Design Guide",
        title=topic_title,
        subtitle="A 60-Second Visual Mental Model",
        bullet_points=cover_bullets,
        accent_color=ACCENT_CYAN,
        is_cover=True
    )
    rendered_images.append(cover_img)

    # 2. Content Slides
    for idx, s in enumerate(slides_data):
        slide_num = idx + 2
        slide_img = render_carousel_slide(
            slide_index=slide_num,
            total_slides=total,
            badge_text=s.get("badge", "Key Concept"),
            title=s.get("title", f"Concept {idx+1}"),
            subtitle=s.get("subtitle", ""),
            bullet_points=s.get("bullets", []),
            accent_color=s.get("accent", ACCENT_CYAN)
        )
        rendered_images.append(slide_img)

    # 3. Final Discussion Question Slide
    final_q = senior_question or "In production, what is your team's standard approach for handling this?"
    final_img = render_carousel_slide(
        slide_index=total,
        total_slides=total,
        badge_text="Production Debate",
        title="Discussion Question",
        subtitle="For Senior & Staff Engineers",
        bullet_points=[final_q],
        accent_color="#3fb950",
        is_final=True
    )
    rendered_images.append(final_img)

    # 4. Save Multi-Page PDF
    out_pdf_path = CAROUSEL_DIR / f"{topic_id}_Carousel_Deck.pdf"
    first_page = rendered_images[0]
    first_page.save(
        out_pdf_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=rendered_images[1:]
    )

    return out_pdf_path
