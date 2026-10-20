"""Design System package."""
from src.design_system.rules import (
    COLOR_BG_DARK,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_YELLOW,
    ACCENT_RED,
    ACCENT_PURPLE,
    MANIM_ZONE_HEADER_TOP,
    MANIM_ZONE_HEADER_BOTTOM,
    MANIM_ZONE_DIAGRAM_TOP,
    MANIM_ZONE_DIAGRAM_BOTTOM,
    MANIM_ZONE_NARRATIVE_TOP,
    MANIM_ZONE_NARRATIVE_BOTTOM,
    MANIM_BOTTOM_SAFE_LIMIT,
    MANIM_ARROW_BUFFER,
    MANIM_MIN_ELEMENT_GAP,
    PDF_WIDTH,
    PDF_HEIGHT,
    BoundingBox2D,
    wrap_text_cleanly
)
from src.design_system.tokens import (
    TYPOGRAPHY_TOKENS,
    CANVAS_ASPECT_RATIOS,
    LUMINANCE_RAMPS,
    resolve_topology_aspect_ratio,
    generate_css_tokens
)
from src.design_system.primitives import (
    render_database_cylinder,
    render_partitioned_queue,
    render_gateway_shield,
    render_directional_flow,
    render_full_width_topology,
    render_sequence_flow_svg,
)

