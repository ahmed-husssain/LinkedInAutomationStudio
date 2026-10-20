"""
Lightweight SVG Micro-Diagram Primitives.
Zero external dependencies; generates pure, standards-compliant SVG vector elements
with Apple-grade specular styling and direct in-line data labels.
"""

from typing import Optional, List


def render_database_cylinder(
    x: int,
    y: int,
    width: int = 120,
    height: int = 140,
    label: str = "Primary DB",
    metric: str = "p99 12ms",
    replicas: int = 2,
    status: str = "healthy",
    accent: str = "#38bdf8",
) -> str:
    """
    Renders an Apple-grade 3D cylinder database node with replica rings,
    specular top highlight, and direct in-line label and latency metrics.
    """
    rx = width // 2
    ry = max(12, height // 7)
    cx = x + rx
    top_cy = y + ry
    bot_cy = y + height - ry
    status_color = "#10b981" if status == "healthy" else "#ef4444"

    svg = f"""<g class="primitive-database" transform="translate({x}, {y})">
  <!-- Cylinder Body Drop Shadow -->
  <ellipse cx="{rx}" cy="{height - ry + 4}" rx="{rx - 2}" ry="{ry - 2}" fill="rgba(0,0,0,0.5)" filter="blur(6px)" />
  
  <!-- Outer Body Path -->
  <path d="M 0 {ry} L 0 {height - ry} A {rx} {ry} 0 0 0 {width} {height - ry} L {width} {ry} Z" 
        fill="rgba(15, 23, 42, 0.85)" stroke="rgba(255, 255, 255, 0.12)" stroke-width="1.5" />
"""
    step = (bot_cy - top_cy) // (replicas + 1)
    for i in range(1, replicas + 1):
        ring_y = top_cy + i * step - y
        svg += f"""  <path d="M 0 {ring_y} A {rx} {ry} 0 0 0 {width} {ring_y}" 
        fill="none" stroke="{accent}" stroke-opacity="0.35" stroke-dasharray="3 3" stroke-width="1" />
"""

    svg += f"""  <!-- Specular Top Surface -->
  <ellipse cx="{rx}" cy="{ry}" rx="{rx}" ry="{ry}" 
           fill="rgba(30, 41, 59, 0.9)" stroke="{accent}" stroke-width="1.5" />
  <ellipse cx="{rx}" cy="{ry}" rx="{rx - 3}" ry="{ry - 2}" 
           fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="1" />

  <!-- Status Beacon -->
  <circle cx="{rx}" cy="{ry}" r="4" fill="{status_color}" />
  <circle cx="{rx}" cy="{ry}" r="7" fill="none" stroke="{status_color}" stroke-opacity="0.4" stroke-width="1.5" />

  <!-- Direct In-line Label -->
  <text x="{rx}" y="{height // 2 + 6}" text-anchor="middle" 
        fill="#f8fafc" font-family="-apple-system, sans-serif" font-size="13" font-weight="700" letter-spacing="-0.01em">
    {label}
  </text>

  <!-- In-line Tabular Metric Badge -->
  <g transform="translate({rx - 38}, {height - ry - 14})">
    <rect width="76" height="18" rx="9" fill="rgba(0, 0, 0, 0.6)" stroke="{accent}" stroke-opacity="0.5" stroke-width="1" />
    <text x="38" y="13" text-anchor="middle" fill="{accent}" 
          font-family="Consolas, monospace" font-size="10" font-weight="600" font-variant-numeric="tabular-nums">
      {metric}
    </text>
  </g>
</g>"""
    return svg


def render_partitioned_queue(
    x: int,
    y: int,
    width: int = 180,
    height: int = 90,
    partitions: int = 3,
    topic: str = "events.orders",
    lag: int = 0,
    accent: str = "#818cf8",
) -> str:
    """
    Renders a partitioned streaming buffer (e.g. Kafka/Pulsar) with partition slots,
    per-slot offsets, and direct in-line consumer lag indicator.
    """
    lag_color = "#10b981" if lag == 0 else "#f59e0b" if lag < 500 else "#ef4444"
    slot_width = (width - 16) // partitions

    svg = f"""<g class="primitive-queue" transform="translate({x}, {y})">
  <!-- Outer Specular Frame -->
  <rect width="{width}" height="{height}" rx="14" fill="rgba(15, 23, 42, 0.8)" 
        stroke="rgba(255, 255, 255, 0.15)" stroke-width="1.5" />
  <rect x="1" y="1" width="{width - 2}" height="1" fill="rgba(255, 255, 255, 0.2)" />

  <!-- Topic Name Header -->
  <text x="12" y="22" fill="#94a3b8" font-family="-apple-system, sans-serif" font-size="11" font-weight="600" letter-spacing="0.05em">
    QUEUE: <tspan fill="#f8fafc" font-weight="700">{topic}</tspan>
  </text>

  <!-- Partition Slots -->
"""
    for p in range(partitions):
        px = 8 + p * slot_width
        py = 32
        p_height = height - 42
        svg += f"""  <g transform="translate({px}, {py})">
    <rect width="{slot_width - 4}" height="{p_height}" rx="6" fill="rgba(30, 41, 59, 0.7)" 
          stroke="{accent}" stroke-opacity="0.4" stroke-width="1" />
    <text x="{(slot_width - 4) // 2}" y="{p_height // 2 + 4}" text-anchor="middle" fill="#cbd5e1"
          font-family="Consolas, monospace" font-size="10" font-weight="600">P{p}</text>
  </g>
"""

    svg += f"""  <!-- Consumer Lag Pill -->
  <g transform="translate({width - 70}, 10)">
    <rect width="60" height="16" rx="8" fill="rgba(0, 0, 0, 0.6)" stroke="{lag_color}" stroke-opacity="0.6" stroke-width="1" />
    <text x="30" y="12" text-anchor="middle" fill="{lag_color}" 
          font-family="Consolas, monospace" font-size="9" font-weight="700">LAG {lag}</text>
  </g>
</g>"""
    return svg


def render_gateway_shield(
    x: int,
    y: int,
    width: int = 110,
    height: int = 120,
    label: str = "API Gateway",
    rate_limit: str = "10k req/s",
    accent: str = "#38bdf8",
) -> str:
    """
    Renders an API Gateway shield / proxy boundary with specular edges,
    internal routing mesh icon, and rate limit capability badge.
    """
    w = width
    h = height
    svg = f"""<g class="primitive-gateway" transform="translate({x}, {y})">
  <!-- Shield Polygon Body -->
  <path d="M {w//2} 0 L {w} {h//4} L {w} {3*h//4} L {w//2} {h} L 0 {3*h//4} L 0 {h//4} Z"
        fill="rgba(15, 23, 42, 0.85)" stroke="{accent}" stroke-width="1.5" />
  
  <!-- Specular Inset -->
  <path d="M {w//2} 4 L {w - 4} {h//4 + 2} L {w - 4} {3*h//4 - 2} L {w//2} {h - 4} L 4 {3*h//4 - 2} L 4 {h//4 + 2} Z"
        fill="none" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1" />

  <!-- Shield Core Pulse -->
  <circle cx="{w//2}" cy="{h//2 - 6}" r="12" fill="rgba(56, 189, 248, 0.15)" stroke="{accent}" stroke-width="1.5" />
  <path d="M {w//2 - 5} {h//2 - 6} L {w//2} {h//2 - 11} L {w//2 + 5} {h//2 - 6} L {w//2} {h//2 - 1} Z" fill="{accent}" />

  <!-- In-line Label -->
  <text x="{w//2}" y="{h//2 + 22}" text-anchor="middle" fill="#f8fafc" 
        font-family="-apple-system, sans-serif" font-size="12" font-weight="700" letter-spacing="-0.01em">
    {label}
  </text>

  <!-- Rate Limit Pill -->
  <g transform="translate({w//2 - 36}, {h - 18})">
    <rect width="72" height="16" rx="8" fill="rgba(0, 0, 0, 0.7)" stroke="rgba(255, 255, 255, 0.2)" stroke-width="1" />
    <text x="36" y="11" text-anchor="middle" fill="#94a3b8" 
          font-family="Consolas, monospace" font-size="9" font-weight="600" font-variant-numeric="tabular-nums">
      {rate_limit}
    </text>
  </g>
</g>"""
    return svg


def render_directional_flow(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    label: Optional[str] = None,
    accent: str = "#38bdf8",
    animated: bool = False,
) -> str:
    """
    Renders a directional vector connection with velocity line-weight,
    arrowhead, and direct inline payload tag (no detached legend).
    """
    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2
    dash_attr = ' stroke-dasharray="6 4"' if animated else ""

    svg = f"""<g class="primitive-flow">
  <defs>
    <marker id="arrow-{x1}-{y1}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="{accent}" />
    </marker>
  </defs>
  <!-- Main Connection Line -->
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" 
        stroke="{accent}" stroke-width="2"{dash_attr} 
        marker-end="url(#arrow-{x1}-{y1})" />
"""
    if label:
        text_w = max(50, len(label) * 7 + 16)
        svg += f"""  <!-- Direct Inline Label Pill (Zero Detached Legends) -->
  <g transform="translate({mx - text_w // 2}, {my - 10})">
    <rect width="{text_w}" height="20" rx="10" fill="rgba(8, 12, 20, 0.9)" 
          stroke="{accent}" stroke-opacity="0.4" stroke-width="1" />
    <text x="{text_w // 2}" y="14" text-anchor="middle" fill="#e2e8f0"
          font-family="Consolas, monospace" font-size="10" font-weight="600">
      {label}
    </text>
  </g>
"""
    svg += "</g>"
    return svg
