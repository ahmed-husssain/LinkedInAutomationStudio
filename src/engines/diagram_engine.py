"""
High-Resolution Technical Diagram Generator (1080x1080).
Creates ByteByteGo / Stripe-grade architecture cards using headless HTML/Tailwind
rendering via Playwright, with zero-regression fallback to Pillow.
"""

import json
import base64
import zlib
import urllib.parse
import asyncio
import concurrent.futures
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Dict, Any
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


def _build_html_markup(
    topic_id: str,
    title: str,
    tagline: str,
    theme: str,
    width: int = CANVAS_WIDTH,
    height: int = CANVAS_HEIGHT
) -> str:
    """Substitutes theme variables, dimensions, and topic text into the HTML template."""
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
        "{{CANVAS_WIDTH}}": str(width),
        "{{CANVAS_HEIGHT}}": str(height),
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
    overwrite: bool = False,
    aspect_ratio: Optional[str] = None
) -> Path:
    """
    Renders an adaptive architecture diagram via headless Chromium HTML template.
    Content-topology driven aspect ratio: landscape (16:9), portrait (4:5), or square (1:1).
    Falls back to Pillow if Playwright fails.
    """
    from src.design_system.tokens import resolve_topology_aspect_ratio, CANVAS_ASPECT_RATIOS

    # ponytail: default to square unless caller or detected topology specifies landscape/portrait
    ratio_key = aspect_ratio
    if not ratio_key:
        detected = resolve_topology_aspect_ratio([topic_id], title=title)
        # For single diagrams, preserve square unless it's an explicit pipeline/stream topology
        ratio_key = detected if detected in ("landscape", "square") else "square"

    canvas_spec = CANVAS_ASPECT_RATIOS.get(ratio_key, CANVAS_ASPECT_RATIOS["square"])
    width = canvas_spec["width"]
    height = canvas_spec["height"]

    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{ratio_key}" if ratio_key != "square" else ""
    out_file = target_dir / f"{topic_id}_Diagram_{theme}{suffix}.png"

    if out_file.exists() and not overwrite:
        return out_file

    try:
        from src.engines.html_renderer import render_html_to_image
        html_markup = _build_html_markup(topic_id, title, tagline, theme, width=width, height=height)
        png_bytes = await render_html_to_image(
            html_markup,
            width=width,
            height=height,
            timeout_ms=6000
        )
        out_file.write_bytes(png_bytes)
        return out_file
    except Exception as exc:
        logger.warning(
            f"HTML diagram render failed for '{topic_id}' ({exc}). Falling back to Pillow engine."
        )
        return _generate_diagram_pillow(
            topic_id, title, tagline, theme, output_dir, overwrite,
            width=width, height=height, out_file=out_file
        )


def _generate_diagram_pillow(
    topic_id: str,
    title: str,
    tagline: str = "",
    theme: str = "cyan",
    output_dir: Optional[Path] = None,
    overwrite: bool = False,
    width: int = CANVAS_WIDTH,
    height: int = CANVAS_HEIGHT,
    out_file: Optional[Path] = None
) -> Path:
    """Pillow fallback generator: guarantees 100% resilient rendering even without browser."""
    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    theme_data = THEMES.get(theme.lower(), THEMES["cyan"])
    accent_color = theme_data["accent"]

    if out_file is None:
        out_file = target_dir / f"{topic_id}_Diagram_{theme}.png"
    if out_file.exists() and not overwrite:
        return out_file

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
    overwrite: bool = False,
    aspect_ratio: Optional[str] = None
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
                topic_id, title, tagline, theme, output_dir, overwrite, aspect_ratio=aspect_ratio
            ))
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    lambda: asyncio.run(generate_technical_diagram_async(
                        topic_id, title, tagline, theme, output_dir, overwrite, aspect_ratio=aspect_ratio
                    ))
                ).result(timeout=10)
    except Exception as exc:
        logger.warning(f"Synchronous HTML diagram render fallback triggered: {exc}")
        return _generate_diagram_pillow(topic_id, title, tagline, theme, output_dir, overwrite)


def build_d2_script(
    topic_id: str,
    title: str,
    profile: Optional[Dict[str, Any]] = None,
    theme: str = "cyan"
) -> str:
    """
    Generates declarative D2 diagram script for publication-grade architectures.
    Decoupled and lightweight; produces valid D2 syntax ready for CLI or Playground.
    """
    from src.engines.carousel_engine import resolve_topic_profile

    prof = profile or resolve_topic_profile(topic_id, title)
    clean_title = prof.get("title", title or topic_id)
    theme_data = THEMES.get(theme.lower(), THEMES["cyan"])
    accent = theme_data["accent"]

    topo = prof.get("topology", {})
    ingress_lbl = topo.get("ingress_label", "Edge Gateway")
    ingress_met = topo.get("ingress_metric", "TLS Term")
    worker_lbl = topo.get("worker_label", "Stateless Workers")
    worker_met = topo.get("worker_metric", "Autoscaling")
    queue_lbl = topo.get("queue_label", "Buffer Stream")
    queue_met = topo.get("queue_metric", "Partitions")
    store_lbl = topo.get("store_label", "Consensus Store")
    store_met = topo.get("store_metric", "p99 4ms")

    seq = prof.get("seq_steps", ["Request Ingress", "Processing", "Commit"])
    s1 = seq[0] if len(seq) > 0 else "Client Request"
    s2 = seq[1] if len(seq) > 1 else "Route & Verify"
    s3 = seq[2] if len(seq) > 2 else "Async Buffer"
    s4 = seq[3] if len(seq) > 3 else "Atomic Store"

    d2_lines = [
        "direction: right",
        f'title: "{clean_title}\\nHigh-Scale Architecture" {{',
        '  near: top-center',
        '}',
        '',
        'client: "Client App\\n(Mobile / Web)" {',
        '  shape: person',
        '  style.stroke: "#94a3b8"',
        '  style.fill: "#1e293b"',
        '}',
        '',
        f'ingress: "{ingress_lbl}\\n({ingress_met})" {{',
        '  shape: diamond',
        f'  style.stroke: "{accent}"',
        '  style.fill: "#0f172a"',
        '}',
        '',
        f'buffer: "{queue_lbl}\\n({queue_met})" {{',
        '  shape: queue',
        '  style.stroke: "#f59e0b"',
        '  style.fill: "#0f172a"',
        '}',
        '',
        f'workers: "{worker_lbl}\\n({worker_met})" {{',
        '  shape: rectangle',
        '  style.stroke: "#10b981"',
        '  style.fill: "#0f172a"',
        '}',
        '',
        f'storage: "{store_lbl}\\n({store_met})" {{',
        '  shape: cylinder',
        '  style.stroke: "#c084fc"',
        '  style.fill: "#0f172a"',
        '}',
        '',
        f'client -> ingress: "1. {s1}"',
        f'ingress -> buffer: "2. {s2}"',
        f'buffer -> workers: "3. {s3}"',
        f'workers -> storage: "4. {s4}"',
    ]
    return "\n".join(d2_lines)


def build_d2_playground_url(d2_script: str) -> str:
    """
    Encodes D2 script into a direct 1-click D2 Playground URL using raw deflate + base64.
    Zero added dependencies; uses Python standard library zlib and base64.
    """
    compressor = zlib.compressobj(level=9, wbits=-zlib.MAX_WBITS)
    compressed = compressor.compress(d2_script.encode("utf-8")) + compressor.flush()
    encoded = base64.b64encode(compressed).decode("utf-8")
    encoded_safe = urllib.parse.quote(encoded)
    return f"https://play.d2lang.com/?script={encoded_safe}"


def build_excalidraw_json(
    topic_id: str,
    title: str,
    profile: Optional[Dict[str, Any]] = None,
    theme: str = "cyan"
) -> Dict[str, Any]:
    """
    Generates an Excalidraw-compatible schema dictionary with zero dependencies.
    Can be loaded directly into Excalidraw or saved as a .excalidraw file.
    """
    from src.engines.carousel_engine import resolve_topic_profile

    prof = profile or resolve_topic_profile(topic_id, title)
    clean_title = prof.get("title", title or topic_id)
    theme_data = THEMES.get(theme.lower(), THEMES["cyan"])
    accent = theme_data["accent"]

    topo = prof.get("topology", {})
    ingress_lbl = topo.get("ingress_label", "Edge Gateway")
    ingress_met = topo.get("ingress_metric", "TLS Term")
    worker_lbl = topo.get("worker_label", "Stateless Workers")
    worker_met = topo.get("worker_metric", "Autoscaling")
    queue_lbl = topo.get("queue_label", "Buffer Stream")
    queue_met = topo.get("queue_metric", "Partitions")
    store_lbl = topo.get("store_label", "Consensus Store")
    store_met = topo.get("store_metric", "p99 4ms")

    cards = [
        ("node_client", "text_client", 80, 240, 160, 100, "Client / SPA", "HTTPS / TLS 1.3", "#94a3b8"),
        ("node_ingress", "text_ingress", 300, 240, 170, 100, ingress_lbl, ingress_met, accent),
        ("node_queue", "text_queue", 530, 240, 170, 100, queue_lbl, queue_met, "#f59e0b"),
        ("node_workers", "text_workers", 760, 240, 170, 100, worker_lbl, worker_met, "#10b981"),
        ("node_store", "text_store", 990, 240, 170, 100, store_lbl, store_met, "#c084fc"),
    ]

    elements: List[Dict[str, Any]] = [
        {
            "id": "title_header",
            "type": "text",
            "x": 80,
            "y": 120,
            "width": 800,
            "height": 40,
            "text": f"{clean_title} — Production Topology",
            "fontSize": 26,
            "fontFamily": 1,
            "textAlign": "left",
            "verticalAlign": "top",
            "strokeColor": "#ffffff",
            "backgroundColor": "transparent",
        }
    ]

    for nid, tid, x, y, w, h, name, metric, stroke in cards:
        elements.append({
            "id": nid,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "strokeColor": stroke,
            "backgroundColor": "#111827",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "roughness": 1,
            "roundness": {"type": 3},
        })
        elements.append({
            "id": tid,
            "type": "text",
            "x": x + 10,
            "y": y + 25,
            "width": w - 20,
            "height": 50,
            "text": f"{name}\n({metric})",
            "fontSize": 15,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "strokeColor": "#f8fafc",
            "backgroundColor": "transparent",
        })

    arrows = [
        ("arr_1", 240, 290, 300, 290, accent),
        ("arr_2", 470, 290, 530, 290, "#f59e0b"),
        ("arr_3", 700, 290, 760, 290, "#10b981"),
        ("arr_4", 930, 290, 990, 290, "#c084fc"),
    ]
    for aid, x1, y1, x2, y2, stroke in arrows:
        elements.append({
            "id": aid,
            "type": "arrow",
            "x": x1,
            "y": y1,
            "width": x2 - x1,
            "height": 0,
            "strokeColor": stroke,
            "strokeWidth": 2,
            "roughness": 1,
            "points": [[0, 0], [x2 - x1, 0]],
        })

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "LinkedInAutomationStudio",
        "elements": elements,
        "appState": {
            "viewBackgroundColor": "#080c14",
            "theme": "dark",
        },
    }


async def generate_diagram_package_async(
    topic_id: str,
    title: str,
    output_dir: Optional[Path] = None,
    theme: str = "cyan",
    aspect_ratio: Optional[str] = None,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Compiles the complete 2D Architecture Diagram package.
    Produces high-resolution PNG image, declarative D2 script, 1-click Playground URL,
    and Excalidraw whiteboard file with zero cloud cost.
    """
    from src.engines.carousel_engine import resolve_topic_profile

    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    prof = resolve_topic_profile(topic_id, title)
    tagline = prof.get("subtitle", "Production Architecture & High-Scale Flow")

    # 1. Render PNG diagram
    png_path = await generate_technical_diagram_async(
        topic_id=topic_id,
        title=prof["title"],
        tagline=tagline,
        theme=theme,
        output_dir=target_dir,
        overwrite=overwrite,
        aspect_ratio=aspect_ratio,
    )

    # 2. Build D2 script & URL
    d2_script = build_d2_script(topic_id, title, profile=prof, theme=theme)
    d2_url = build_d2_playground_url(d2_script)
    d2_file = target_dir / f"{topic_id}_architecture.d2"
    d2_file.write_text(d2_script, encoding="utf-8")

    # 3. Build Excalidraw JSON & save file
    excal_data = build_excalidraw_json(topic_id, title, profile=prof, theme=theme)
    excal_file = target_dir / f"{topic_id}_architecture.excalidraw"
    excal_file.write_text(json.dumps(excal_data, indent=2), encoding="utf-8")

    return {
        "png_path": png_path,
        "d2_script": d2_script,
        "d2_url": d2_url,
        "d2_file": d2_file,
        "excalidraw_file": excal_file,
        "excalidraw_data": excal_data,
        "profile": prof,
    }


def generate_diagram_package(
    topic_id: str,
    title: str,
    output_dir: Optional[Path] = None,
    theme: str = "cyan",
    aspect_ratio: Optional[str] = None,
    overwrite: bool = False
) -> Dict[str, Any]:
    """Synchronous wrapper for generate_diagram_package_async."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        return asyncio.run(generate_diagram_package_async(
            topic_id, title, output_dir, theme, aspect_ratio=aspect_ratio, overwrite=overwrite
        ))
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(
            lambda: asyncio.run(generate_diagram_package_async(
                topic_id, title, output_dir, theme, aspect_ratio=aspect_ratio, overwrite=overwrite
            ))
        ).result(timeout=12)


