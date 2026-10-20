"""
High-Resolution 4-Slide LinkedIn Carousel Generator.
Produces Apple-grade technical carousels with optical typography,
specular glass cards, and native multi-page PDF compilation.
Zero added dependencies; uses Playwright Chromium with native Pillow fallback.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from PIL import Image

from src.config.settings import THUMBNAILS_DIR
from src.design_system.tokens import CANVAS_ASPECT_RATIOS
from src.design_system.primitives import (
    render_database_cylinder,
    render_partitioned_queue,
    render_gateway_shield,
    render_directional_flow,
)

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "carousel_slide.html"

CAROUSEL_THEMES = {
    "cyan": {
        "accent": "#38bdf8",
        "glow": "rgba(56, 189, 248, 0.25)",
        "name": "Sky Cyan"
    },
    "emerald": {
        "accent": "#34d399",
        "glow": "rgba(52, 211, 153, 0.25)",
        "name": "Mint Emerald"
    },
    "purple": {
        "accent": "#c084fc",
        "glow": "rgba(192, 132, 252, 0.25)",
        "name": "Deep Violet"
    },
    "amber": {
        "accent": "#fbbf24",
        "glow": "rgba(251, 191, 36, 0.25)",
        "name": "Warm Amber"
    },
}


def build_default_slides(topic_id: str, title: str) -> List[Dict[str, Any]]:
    """Builds the 4-slide narrative structure (Hook -> Bottleneck -> Fix -> Checklist)."""
    clean_title = (title or topic_id).strip()
    return [
        {
            "slide_number": 1,
            "badge": "SYSTEM ARCHITECTURE",
            "title": clean_title,
            "subtitle": "How staff engineers design zero-downtime distributed systems under extreme load.",
            "stage_html": f"""
            <div class="narrative-block highlight">
              <span class="block-tag">Core Challenge</span>
              <p class="block-text">When traffic spikes 100x, traditional monolithic architectures fail at connection pools and locks.</p>
            </div>
            <div class="narrative-block" style="margin-top: 16px;">
              <span class="block-tag">Architectural Blueprint</span>
              <p class="block-text">Swipe left to dissect the failure mode, the decoupled topology, and the staff checklist.</p>
            </div>
            """,
            "metric_1_label": "PEAK THROUGHPUT",
            "metric_1_val": "150,000 req/s",
            "metric_2_label": "TARGET AVAILABILITY",
            "metric_2_val": "99.999% SLA",
            "swipe_hint": "Swipe for Failure Mode →",
        },
        {
            "slide_number": 2,
            "badge": "INCIDENT POST-MORTEM",
            "title": "The Bottleneck: Cascading Lock Contention",
            "subtitle": "Why synchronous shared-database writes bring down downstream microservices.",
            "stage_html": f"""
            <div class="narrative-block" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
              <span class="block-tag" style="color: #ef4444;">Failure Pattern</span>
              <p class="block-text">Synchronous RPC calls queue up behind unindexed database row-locks. Connection pools exhaust within 8 seconds.</p>
            </div>
            <div class="narrative-block" style="margin-top: 16px;">
              <span class="block-tag" style="color: #f59e0b;">Degradation Timeline</span>
              <p class="block-text">p99 latency jumps from 18ms to 4,850ms. Health checks fail, triggering an accidental thundering herd restart loop.</p>
            </div>
            """,
            "metric_1_label": "UNHANDLED ERROR RATE",
            "metric_1_val": "34.2% HTTP 504",
            "metric_2_label": "p99 RESPONSE TIME",
            "metric_2_val": "4,850ms (CRITICAL)",
            "swipe_hint": "Swipe for The Fix →",
        },
        {
            "slide_number": 3,
            "badge": "BATTLE-TESTED PATTERN",
            "title": "The Solution: Decoupled Event Streams",
            "subtitle": "Replacing synchronous lock contention with partitioned queue buffers and read replicas.",
            "stage_html": f"""
            <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 12px;">
              <svg width="420" height="150" viewBox="0 0 420 150">
                {render_gateway_shield(10, 10, width=100, height=120, label="Gateway", rate_limit="50k req/s")}
                {render_directional_flow(115, 65, 175, 65, label="Async Event", animated=True)}
                {render_partitioned_queue(180, 20, width=130, height=85, partitions=3, topic="orders", lag=0)}
                {render_directional_flow(315, 65, 335, 65)}
                {render_database_cylinder(335, 5, width=80, height=125, label="Replica", metric="p99 4ms")}
              </svg>
            </div>
            <div class="narrative-block highlight">
              <span class="block-tag">Architectural Invariant</span>
              <p class="block-text">Writes buffer safely into partitions; read replicas serve p99 queries in under 5ms without table locking.</p>
            </div>
            """,
            "metric_1_label": "RESTORED p99 LATENCY",
            "metric_1_val": "4.2ms (STABLE)",
            "metric_2_label": "CONSUMER BUFFER LAG",
            "metric_2_val": "0 messages",
            "swipe_hint": "Swipe for Staff Checklist →",
        },
        {
            "slide_number": 4,
            "badge": "PRODUCTION PLAYBOOK",
            "title": "Staff Engineer Checklist",
            "subtitle": "Four rules to audit your distributed architecture before hitting production.",
            "stage_html": """
            <div class="narrative-block" style="gap: 14px;">
              <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-family: Consolas, monospace; font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 3px 8px; border-radius: 6px;">RULE 1</span>
                <span style="font-size: 15px; color: #f1f5f9; font-weight: 600;">Enforce timeout budgets & jittered exponential backoffs on all RPCs.</span>
              </div>
              <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-family: Consolas, monospace; font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 3px 8px; border-radius: 6px;">RULE 2</span>
                <span style="font-size: 15px; color: #f1f5f9; font-weight: 600;">Partition by high-cardinality keys to prevent hotspot partitions.</span>
              </div>
              <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-family: Consolas, monospace; font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 3px 8px; border-radius: 6px;">RULE 3</span>
                <span style="font-size: 15px; color: #f1f5f9; font-weight: 600;">Separate transactional writes from read-heavy analytical queries.</span>
              </div>
              <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-family: Consolas, monospace; font-size: 11px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 3px 8px; border-radius: 6px;">RULE 4</span>
                <span style="font-size: 15px; color: #f1f5f9; font-weight: 600;">Monitor p99 latency & queue lag instead of misleading averages.</span>
              </div>
            </div>
            """,
            "metric_1_label": "REDUNDANCY MODEL",
            "metric_1_val": "Multi-Region Active",
            "metric_2_label": "DEPLOYMENT SAFETY",
            "metric_2_val": "Zero-Downtime Blue/Green",
            "swipe_hint": "Save & Share for Reference",
        },
    ]


def build_carousel_slide_html(
    slide_data: Dict[str, Any],
    theme: str = "cyan",
    width: int = 1080,
    height: int = 1350,
    total_slides: int = 4
) -> str:
    """Renders the HTML markup for a single carousel slide."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    theme_cfg = CAROUSEL_THEMES.get(theme, CAROUSEL_THEMES["cyan"])
    accent = theme_cfg["accent"]
    glow = theme_cfg["glow"]

    replacements = {
        "{{CANVAS_WIDTH}}": str(width),
        "{{CANVAS_HEIGHT}}": str(height),
        "{{THEME_ACCENT}}": accent,
        "{{THEME_GLOW}}": glow,
        "{{TOPIC_BADGE}}": slide_data.get("badge", "SYSTEM DESIGN"),
        "{{SLIDE_NUMBER}}": str(slide_data.get("slide_number", 1)),
        "{{TOTAL_SLIDES}}": str(total_slides),
        "{{TITLE}}": slide_data.get("title", ""),
        "{{SUBTITLE}}": slide_data.get("subtitle", ""),
        "{{STAGE_HTML}}": slide_data.get("stage_html", ""),
        "{{METRIC_1_LABEL}}": slide_data.get("metric_1_label", "METRIC"),
        "{{METRIC_1_VALUE}}": slide_data.get("metric_1_val", "NOMINAL"),
        "{{METRIC_2_LABEL}}": slide_data.get("metric_2_label", "STATUS"),
        "{{METRIC_2_VALUE}}": slide_data.get("metric_2_val", "100%"),
        "{{FOOTER_TEXT}}": "LinkedIn Automation Studio • Staff Engineering Series",
        "{{SWIPE_HINT}}": slide_data.get("swipe_hint", "Swipe →"),
    }
    for placeholder, val in replacements.items():
        html = html.replace(placeholder, str(val))
    return html


async def generate_carousel_async(
    topic_id: str,
    title: str,
    slides_data: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[Path] = None,
    theme: str = "cyan",
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Asynchronously generates a 4-slide carousel:
    - 4 PNG slide images (1080x1350 4:5 vertical carousel format)
    - 1 compiled multi-page PDF document for LinkedIn
    """
    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    slides = slides_data or build_default_slides(topic_id, title)
    canvas_spec = CANVAS_ASPECT_RATIOS["portrait"]
    width = canvas_spec["width"]
    height = canvas_spec["height"]

    pdf_path = target_dir / f"{topic_id}_Carousel_{theme}.pdf"
    slide_paths: List[Path] = []
    pil_images: List[Image.Image] = []

    from src.engines.html_renderer import render_html_to_image

    for slide in slides:
        num = slide.get("slide_number", 1)
        slide_png = target_dir / f"{topic_id}_Slide_{num}_{theme}.png"
        slide_paths.append(slide_png)

        if not slide_png.exists() or overwrite:
            html = build_carousel_slide_html(
                slide_data=slide,
                theme=theme,
                width=width,
                height=height,
                total_slides=len(slides)
            )
            try:
                png_bytes = await render_html_to_image(html, width=width, height=height, timeout_ms=6000)
                slide_png.write_bytes(png_bytes)
            except Exception as exc:
                logger.warning(f"Carousel slide {num} Playwright render failed: {exc}. Using fallback.")
                # Fallback: create solid dark card with Pillow
                img = Image.new("RGB", (width, height), color="#0b101c")
                img.save(slide_png)

        # Open image for PDF compilation
        pil_images.append(Image.open(slide_png).convert("RGB"))

    # Compile multi-page PDF
    if pil_images and (not pdf_path.exists() or overwrite):
        first_img = pil_images[0]
        other_imgs = pil_images[1:] if len(pil_images) > 1 else []
        first_img.save(
            pdf_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=other_imgs
        )

    # Close open image handles
    for img in pil_images:
        img.close()

    return {
        "pdf": pdf_path,
        "slides": slide_paths,
        "cover": slide_paths[0] if slide_paths else None,
    }


def generate_carousel(
    topic_id: str,
    title: str,
    slides_data: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[Path] = None,
    theme: str = "cyan",
    overwrite: bool = False
) -> Dict[str, Any]:
    """Synchronous entrypoint for carousel generation."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                asyncio.run,
                generate_carousel_async(
                    topic_id=topic_id,
                    title=title,
                    slides_data=slides_data,
                    output_dir=output_dir,
                    theme=theme,
                    overwrite=overwrite
                )
            )
            return future.result()
    else:
        return asyncio.run(
            generate_carousel_async(
                topic_id=topic_id,
                title=title,
                slides_data=slides_data,
                output_dir=output_dir,
                theme=theme,
                overwrite=overwrite
            )
        )
