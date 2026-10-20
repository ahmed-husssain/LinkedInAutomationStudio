"""
Apple-Grade Design Foundation Tokens.
Implements size-specific optical tracking, perceptual luminance hierarchy,
translucent glass specular materials, and adaptive aspect ratio geometries.
Zero external dependencies; ultra-lean execution and token footprint.
"""

from typing import Dict, Any


# 1. OPTICAL TYPOGRAPHY TOKENS (better-typography & apple-design)
# Size-specific tracking: large display headings take negative tracking, small labels take open positive tracking.
TYPOGRAPHY_TOKENS: Dict[str, Dict[str, str]] = {
    "display": {
        "size": "44px",
        "line_height": "1.08",
        "letter_spacing": "-0.03em",
        "weight": "800",
        "text_wrap": "balance",
    },
    "heading": {
        "size": "32px",
        "line_height": "1.2",
        "letter_spacing": "-0.02em",
        "weight": "700",
        "text_wrap": "balance",
    },
    "subheading": {
        "size": "20px",
        "line_height": "1.35",
        "letter_spacing": "-0.01em",
        "weight": "600",
        "text_wrap": "pretty",
    },
    "body": {
        "size": "16px",
        "line_height": "1.5",
        "letter_spacing": "0em",
        "weight": "400",
        "text_wrap": "pretty",
    },
    "caption": {
        "size": "13px",
        "line_height": "1.4",
        "letter_spacing": "0.02em",
        "weight": "500",
    },
    "badge": {
        "size": "11px",
        "line_height": "1.0",
        "letter_spacing": "0.08em",
        "weight": "700",
        "text_transform": "uppercase",
    },
    "mono": {
        "size": "14px",
        "line_height": "1.45",
        "letter_spacing": "0em",
        "weight": "500",
        "font_family": "Consolas, 'JetBrains Mono', monospace",
        "font_variant_numeric": "tabular-nums",
    },
}


# 2. ADAPTIVE CANVAS GEOMETRIES (adaptive-layout)
# Content-topology driven dimensions: content dictates canvas geometry
CANVAS_ASPECT_RATIOS: Dict[str, Dict[str, Any]] = {
    "landscape": {  # Horizontal pipelines, streams, distributed meshes
        "ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "safe_margin": 60,
    },
    "landscape_compact": {  # Social feed summary cards, web previews
        "ratio": "1.91:1",
        "width": 1200,
        "height": 630,
        "safe_margin": 45,
    },
    "portrait": {  # LinkedIn PDF Document carousel, mobile feed reading
        "ratio": "4:5",
        "width": 1080,
        "height": 1350,
        "safe_margin": 90,
    },
    "square": {  # Cyclic loops, state machines (Token Bucket), mental models
        "ratio": "1:1",
        "width": 1080,
        "height": 1080,
        "safe_margin": 80,
    },
    "tall": {  # Deep full-stack lifecycle journey
        "ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "safe_margin": 90,
    },
}


# 3. PERCEPTUAL LUMINANCE & COGNITIVE COLOR RAMPS (better-colors)
# Strict 3-tier hierarchy: Focal point (85-100% L) -> Nodes (35-60% L) -> Ground (8-12% L)
LUMINANCE_RAMPS: Dict[str, Any] = {
    "ground": {
        "obsidian": "#07090e",
        "slate": "#0d1117",
        "border": "rgba(255, 255, 255, 0.08)",
        "grid_dots": "rgba(255, 255, 255, 0.05)",
    },
    "glass": {
        "fill": "rgba(18, 24, 38, 0.72)",
        "blur": "24px",
        "saturate": "180%",
        "bevel_top": "rgba(255, 255, 255, 0.18)",
        "bevel_side": "rgba(255, 255, 255, 0.08)",
        "shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
        "radius": "20px",
    },
    "accents": {
        "incident_warn": {"primary": "#f59e0b", "secondary": "#ef4444", "glow": "rgba(245, 158, 11, 0.25)"},
        "solution_mint": {"primary": "#10b981", "secondary": "#38bdf8", "glow": "rgba(16, 185, 129, 0.25)"},
        "streaming_violet": {"primary": "#8b5cf6", "secondary": "#ec4899", "glow": "rgba(139, 92, 246, 0.25)"},
        "core_cyan": {"primary": "#00f0ff", "secondary": "#3b82f6", "glow": "rgba(0, 240, 255, 0.25)"},
    },
}


def resolve_topology_aspect_ratio(topic_tags: list[str], title: str = "") -> str:
    """
    Determines the optimal aspect ratio based on concept topology.
    Returns ratio key: 'landscape', 'portrait', or 'square'.
    """
    text = f"{' '.join(topic_tags)} {title}".lower()

    # Horizontal streaming / pipeline / event-driven architectures -> 16:9 Landscape
    if any(k in text for k in ["stream", "pipeline", "kafka", "queue", "mesh", "rebalancing", "saga", "2pc"]):
        return "landscape"

    # Cyclic feedback loops / state machines -> 1:1 Square
    if any(k in text for k in ["rate limit", "token bucket", "leaky bucket", "circuit breaker", "election", "state machine"]):
        return "square"

    # Default to 4:5 Vertical Portrait for narrative step-by-step causality
    return "portrait"


def generate_css_tokens() -> str:
    """
    Generates ultra-compact native CSS custom properties for injection into HTML templates.
    Zero build steps, instant sub-millisecond evaluation.
    """
    return """
:root {
  --font-display-size: 44px;
  --font-display-lh: 1.08;
  --font-display-ls: -0.03em;
  --font-display-weight: 800;

  --font-heading-size: 32px;
  --font-heading-lh: 1.2;
  --font-heading-ls: -0.02em;
  --font-heading-weight: 700;

  --font-subheading-size: 20px;
  --font-subheading-lh: 1.35;
  --font-subheading-ls: -0.01em;

  --font-body-size: 16px;
  --font-body-lh: 1.5;
  --font-body-ls: 0em;

  --font-badge-size: 11px;
  --font-badge-ls: 0.08em;

  --bg-obsidian: #07090e;
  --bg-slate: #0d1117;
  --glass-fill: rgba(18, 24, 38, 0.72);
  --glass-bevel-top: 1px solid rgba(255, 255, 255, 0.18);
  --glass-bevel-side: 1px solid rgba(255, 255, 255, 0.08);
  --glass-radius: 20px;
}

.scenic-display {
  font-size: var(--font-display-size);
  line-height: var(--font-display-lh);
  letter-spacing: var(--font-display-ls);
  font-weight: var(--font-display-weight);
  text-wrap: balance;
}

.scenic-heading {
  font-size: var(--font-heading-size);
  line-height: var(--font-heading-lh);
  letter-spacing: var(--font-heading-ls);
  font-weight: var(--font-heading-weight);
  text-wrap: balance;
}

.scenic-badge {
  font-size: var(--font-badge-size);
  letter-spacing: var(--font-badge-ls);
  text-transform: uppercase;
  font-weight: 700;
}

.scenic-tabular {
  font-variant-numeric: tabular-nums;
  font-family: Consolas, 'JetBrains Mono', monospace;
}

.scenic-glass {
  background: var(--glass-fill);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-top: var(--glass-bevel-top);
  border-left: var(--glass-bevel-side);
  border-right: var(--glass-bevel-side);
  border-bottom: 1px solid rgba(0, 0, 0, 0.4);
  border-radius: var(--glass-radius);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
""".strip()
