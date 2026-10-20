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
    render_full_width_topology,
    render_sequence_flow_svg,
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


def resolve_carousel_slide_count(
    topic_id: str,
    title: str,
    tags: Optional[List[str]] = None
) -> int:
    """
    Evaluates topic technical depth and cognitive complexity to select
    an optimal slide count strictly between 3 and 5 slides.
    """
    combined = f"{topic_id} {title} {' '.join(tags or [])}".lower()

    # 5 Slides: High-Scale & Multi-Tier Distributed Lifecycles
    tier5_keywords = [
        "10m", "million", "socket", "websocket", "multi-region", "raft", "paxos",
        "consensus", "zero-downtime", "event-driven", "distributed transaction",
        "saga", "high-availability", "disaster recovery", "lifecycle"
    ]
    if any(k in combined for k in tier5_keywords):
        return 5

    # 3 Slides: Focused Mental Models & Isolated Algorithms
    tier3_keywords = [
        "token bucket", "leaky bucket", "circuit breaker", "consistent hash",
        "bloom filter", "lru cache", "idempotency", "mutex", "rate limit",
        "mental model", "algorithm"
    ]
    if any(k in combined for k in tier3_keywords):
        return 3

    # Default to 4 slides for standard incident post-mortems and architecture breakdowns
    return 4


def build_adaptive_slides(
    topic_id: str,
    title: str,
    slide_count: Optional[int] = None,
    accent: str = "#38bdf8",
) -> List[Dict[str, Any]]:
    """
    Builds a high-density, publication-grade carousel narrative strictly
    between 3 and 5 slides, completely eliminating empty canvas void.
    """
    clean_title = (title or topic_id).strip()
    count = slide_count or resolve_carousel_slide_count(topic_id, title)
    count = max(3, min(5, count))

    if count == 3:
        return [
            {
                "slide_number": 1,
                "badge": "MENTAL MODEL 101",
                "title": clean_title,
                "subtitle": "How staff engineers reason about this core building block in high-scale systems.",
                "stage_html": f"""
                <div class="scale-matrix">
                  <div class="scale-kpi"><span class="scale-kpi-label">CONCURRENCY</span><span class="scale-kpi-val">Lock-Free</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">OVERHEAD</span><span class="scale-kpi-val">O(1) Memory</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">FAILURE RISK</span><span class="scale-kpi-val">Zero-Downtime</span></div>
                </div>
                <div class="narrative-block highlight">
                  <span class="block-tag">Core Principle</span>
                  <p class="block-text">Isolating state changes prevents global lock contention while preserving deterministic execution under load.</p>
                </div>
                <div class="config-specimen">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">invariant_spec.go</span></div>
                  <div class="specimen-body">// Invariant: Atomically swap without mutex lock contention<br>atomic.CompareAndSwapUint64(&counter, oldVal, newVal)</div>
                </div>
                """,
                "metric_1_label": "SLA GUARANTEE",
                "metric_1_val": "99.99% Nominal",
                "metric_2_label": "EFFICIENCY",
                "metric_2_val": "100% Deterministic",
                "swipe_hint": "Swipe for Mechanism →",
            },
            {
                "slide_number": 2,
                "badge": "ARCHITECTURE & MECHANISM",
                "title": "Under-the-Hood Mechanism",
                "subtitle": "Step-by-step state transition and distributed dataflow topology.",
                "stage_html": f"""
                {render_full_width_topology(width=880, height=220, ingress_label="Ingress", worker_label="Worker Tier", queue_label="Buffer Stream", store_label="State Store", accent=accent)}
                <div class="narrative-block highlight">
                  <span class="block-tag">Architectural Invariant</span>
                  <p class="block-text">In-memory state transitions execute in sub-millisecond cycles without triggering disk I/O bottlenecks.</p>
                </div>
                """,
                "metric_1_label": "p99 LATENCY",
                "metric_1_val": "< 2.5ms Global",
                "metric_2_label": "STATE DRIFT",
                "metric_2_val": "0% Packet Loss",
                "swipe_hint": "Swipe for Production Rules →",
            },
            {
                "slide_number": 3,
                "badge": "STAFF PLAYBOOK",
                "title": "Production Invariants & Rules",
                "subtitle": "Engineering guardrails to prevent silent degradation in production.",
                "stage_html": f"""
                <div class="playbook-card">
                  <span class="playbook-num">RULE 1</span>
                  <div class="playbook-content"><span class="playbook-title">Set Strict Timeout Budgets</span><span class="playbook-sub">Enforce client-side deadlines with exponential backoff and jitter.</span></div>
                </div>
                <div class="playbook-card">
                  <span class="playbook-num">RULE 2</span>
                  <div class="playbook-content"><span class="playbook-title">Measure Tail Latencies (p99)</span><span class="playbook-sub">Averages hide tail-end connection starvation and thundering herds.</span></div>
                </div>
                <div class="tradeoff-grid">
                  <div class="tradeoff-card gain"><span class="tradeoff-tag" style="color: #10b981;">ARCHITECTURAL GAIN</span><span class="tradeoff-text">10x Concurrency with O(1) state lookup</span></div>
                  <div class="tradeoff-card cost"><span class="tradeoff-tag" style="color: #f59e0b;">KNOWN TRADE-OFF</span><span class="tradeoff-text">Memory overhead scales linearly with active keys</span></div>
                </div>
                """,
                "metric_1_label": "DEPLOYMENT SAFETY",
                "metric_1_val": "Safe Rolling",
                "metric_2_label": "OBSERVABILITY",
                "metric_2_val": "100% Traced",
                "swipe_hint": "Save & Share for Reference",
            },
        ]

    elif count == 5:
        return [
            {
                "slide_number": 1,
                "badge": "SCALE BENCHMARK",
                "title": clean_title,
                "subtitle": "How staff engineers architect zero-downtime distributed systems under extreme load.",
                "stage_html": f"""
                <div class="scale-matrix">
                  <div class="scale-kpi"><span class="scale-kpi-label">SCALE TARGET</span><span class="scale-kpi-val">10M Sockets</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">RAM / SOCKET</span><span class="scale-kpi-val">2.4 KB Pool</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">THROUGHPUT</span><span class="scale-kpi-val">1.5M msg/s</span></div>
                </div>
                <div class="narrative-block highlight">
                  <span class="block-tag">The Core Challenge</span>
                  <p class="block-text">Standard thread-per-request architectures hit kernel limits and OOM crashes past 50,000 concurrent sockets.</p>
                </div>
                <div class="narrative-block">
                  <span class="block-tag">System Blueprint Journey</span>
                  <p class="block-text">Swipe left to inspect the kernel bottleneck, the epoll mesh, the protocol flow, and the production sysctl runbook.</p>
                </div>
                """,
                "metric_1_label": "CONCURRENCY TARGET",
                "metric_1_val": "10,000,000 Active",
                "metric_2_label": "SLA COMMITMENT",
                "metric_2_val": "99.999% Global",
                "swipe_hint": "Swipe for Naive Bottleneck →",
            },
            {
                "slide_number": 2,
                "badge": "ANATOMY OF FAILURE",
                "title": "The Bottleneck: Kernel & Thread Collapse",
                "subtitle": "Why standard blocking I/O models exhaust memory and collapse file descriptors.",
                "stage_html": f"""
                <div class="narrative-block" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
                  <span class="block-tag" style="color: #ef4444;">Failure Pattern</span>
                  <p class="block-text">Operating system threads allocate 2MB stack space per connection. 100k threads demand 200GB RAM, triggering OOM-killer.</p>
                </div>
                <div class="config-specimen">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">kernel_panic.log</span></div>
                  <div class="specimen-body">[ERR_FD_EXHAUSTED] accept(): too many open files (max=65535)<br>[OOM_KILLER] Invoked oom-killer: gfp_mask=0x100cca(GFP_HIGHUSER)</div>
                </div>
                <div class="narrative-block" style="border-color: #f59e0b; background: rgba(245, 158, 11, 0.08);">
                  <span class="block-tag" style="color: #f59e0b;">Degradation Timeline</span>
                  <p class="block-text">p99 latency spikes from 12ms to 6,200ms. Keepalive probes timeout, generating a recursive reconnect avalanche.</p>
                </div>
                """,
                "metric_1_label": "FAILED CONNECTIONS",
                "metric_1_val": "42.8% HTTP 504",
                "metric_2_label": "p99 RESPONSE TIME",
                "metric_2_val": "6,200ms (CRITICAL)",
                "swipe_hint": "Swipe for Decoupled Mesh →",
            },
            {
                "slide_number": 3,
                "badge": "DISTRIBUTED TOPOLOGY",
                "title": "The Solution: Decoupled Event Mesh",
                "subtitle": "Stateless epoll connection workers connected via partitioned stream buffers.",
                "stage_html": f"""
                {render_full_width_topology(width=880, height=220, ingress_label="L4 Proxy (IP Hash)", ingress_metric="1M rps", worker_label="Epoll Edge Tier", worker_metric="10M Conns", queue_label="Partitioned Bus", queue_metric="64 Partitions", store_label="Raft Store", store_metric="p99 3.2ms", accent=accent)}
                <div class="narrative-block highlight">
                  <span class="block-tag">Architectural Invariant</span>
                  <p class="block-text">Workers register socket file descriptors with non-blocking epoll event loops, reducing memory from 2MB to 2.4KB per socket.</p>
                </div>
                """,
                "metric_1_label": "RESTORED p99 LATENCY",
                "metric_1_val": "3.2ms (STABLE)",
                "metric_2_label": "MEMORY PER SOCKET",
                "metric_2_val": "2.4 KB (-99.8%)",
                "swipe_hint": "Swipe for Protocol Flow →",
            },
            {
                "slide_number": 4,
                "badge": "PROTOCOL FLOW & TRADE-OFFS",
                "title": "Temporal Flow & Senior Trade-Offs",
                "subtitle": "The complete lifecycle of a real-time message and its architectural costs.",
                "stage_html": f"""
                {render_sequence_flow_svg(["TCP SYN Handshake", "HTTP 101 Upgrade", "Epoll Registration", "Pub/Sub Broadcast", "Client Frame ACK"], width=880, height=75, accent=accent)}
                <div class="tradeoff-grid">
                  <div class="tradeoff-card gain">
                    <span class="tradeoff-tag" style="color: #10b981;">ARCHITECTURAL GAIN</span>
                    <span class="tradeoff-text">100x Concurrency density; sub-5ms broadcast to 10M subscribers.</span>
                  </div>
                  <div class="tradeoff-card cost">
                    <span class="tradeoff-tag" style="color: #f59e0b;">OPERATIONAL GOTCHA</span>
                    <span class="tradeoff-text">Requires strict TCP socket buffer tuning and partitioned backpressure buffers.</span>
                  </div>
                </div>
                """,
                "metric_1_label": "PUBSUB FANOUT",
                "metric_1_val": "1.2M msgs/sec",
                "metric_2_label": "BUFFER DROPRATE",
                "metric_2_val": "0.000% Dropped",
                "swipe_hint": "Swipe for Production Runbook →",
            },
            {
                "slide_number": 5,
                "badge": "PRODUCTION RUNBOOK",
                "title": "Staff Engineer Runbook",
                "subtitle": "Exact kernel parameters and operational rules for production readiness.",
                "stage_html": f"""
                <div class="config-specimen">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">/etc/sysctl.conf</span></div>
                  <div class="specimen-body">fs.file-max = 2097152<br>net.ipv4.tcp_max_syn_backlog = 65536<br>net.core.somaxconn = 65535<br>net.ipv4.tcp_rmem = 4096 87380 16777216</div>
                </div>
                <div class="playbook-card">
                  <span class="playbook-num">RULE 1</span>
                  <div class="playbook-content"><span class="playbook-title">Set ulimit -n 1048576</span><span class="playbook-sub">Prevent default Linux 1024 file descriptor exhaustion on socket creation.</span></div>
                </div>
                <div class="playbook-card">
                  <span class="playbook-num">RULE 2</span>
                  <div class="playbook-content"><span class="playbook-title">Enforce Heartbeat Jitter</span><span class="playbook-sub">Stagger ping/pong intervals by +/- 20% to avoid synchronized heartbeat bursts.</span></div>
                </div>
                """,
                "metric_1_label": "RUNBOOK STATUS",
                "metric_1_val": "Production Ready",
                "metric_2_label": "RESILIENCE MODEL",
                "metric_2_val": "Multi-Region Active",
                "swipe_hint": "Save & Share for Reference",
            },
        ]

    # Default 4-slide structure (Incident Post-Mortem & Architecture)
    return [
        {
            "slide_number": 1,
            "badge": "SYSTEM ARCHITECTURE",
            "title": clean_title,
            "subtitle": "How staff engineers design zero-downtime distributed systems under extreme load.",
            "stage_html": f"""
            <div class="scale-matrix">
              <div class="scale-kpi"><span class="scale-kpi-label">PEAK SCALE</span><span class="scale-kpi-val">150k req/s</span></div>
              <div class="scale-kpi"><span class="scale-kpi-label">AVAILABILITY</span><span class="scale-kpi-val">99.999% SLA</span></div>
              <div class="scale-kpi"><span class="scale-kpi-label">DATA DRIFT</span><span class="scale-kpi-val">0% Loss</span></div>
            </div>
            <div class="narrative-block highlight">
              <span class="block-tag">The Core Challenge</span>
              <p class="block-text">When traffic spikes 100x, traditional monolithic architectures fail at connection pools and locks.</p>
            </div>
            <div class="narrative-block">
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
            "title": "The Bottleneck: Cascading Contention",
            "subtitle": "Why synchronous shared-database writes bring down downstream microservices.",
            "stage_html": f"""
            <div class="narrative-block" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
              <span class="block-tag" style="color: #ef4444;">Failure Pattern</span>
              <p class="block-text">Synchronous RPC calls queue up behind unindexed database row-locks. Connection pools exhaust within 8 seconds.</p>
            </div>
            <div class="config-specimen">
              <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">postgres_lockup.log</span></div>
              <div class="specimen-body">[FATAL] remaining connection slots are reserved for non-replication superuser connections<br>[ALERT] thread pool starved: 512/512 active workers blocked</div>
            </div>
            <div class="narrative-block" style="border-color: #f59e0b; background: rgba(245, 158, 11, 0.08);">
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
            {render_full_width_topology(width=880, height=220, ingress_label="Edge Gateway", ingress_metric="50k rps", worker_label="Stateless Workers", worker_metric="Autoscaling", queue_label="Kafka Partitions", queue_metric="16 Partitions", store_label="Read Replicas", store_metric="p99 4.2ms", accent=accent)}
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
            "stage_html": f"""
            <div class="playbook-card">
              <span class="playbook-num">RULE 1</span>
              <div class="playbook-content"><span class="playbook-title">Enforce Timeout Budgets</span><span class="playbook-sub">Apply jittered exponential backoffs on all downstream RPC calls.</span></div>
            </div>
            <div class="playbook-card">
              <span class="playbook-num">RULE 2</span>
              <div class="playbook-content"><span class="playbook-title">Partition by High-Cardinality Keys</span><span class="playbook-sub">Prevent hot partitions and rebalance overhead under sudden traffic surges.</span></div>
            </div>
            <div class="tradeoff-grid">
              <div class="tradeoff-card gain">
                <span class="tradeoff-tag" style="color: #10b981;">ARCHITECTURAL GAIN</span>
                <span class="tradeoff-text">Decoupled throughput; failure isolation across all downstream services.</span>
              </div>
              <div class="tradeoff-card cost">
                <span class="tradeoff-tag" style="color: #f59e0b;">KNOWN CEILING</span>
                <span class="tradeoff-text">Requires handling eventual consistency and asynchronous out-of-order retries.</span>
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


def build_default_slides(topic_id: str, title: str) -> List[Dict[str, Any]]:
    """Builds adaptive slides (3-5 slides) based on topic depth."""
    return build_adaptive_slides(topic_id, title)



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
    overwrite: bool = False,
    slide_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Asynchronously generates an adaptive 3-to-5 slide carousel:
    - 3, 4, or 5 PNG slide images (1080x1350 4:5 vertical carousel format)
    - 1 compiled multi-page PDF document for LinkedIn
    """
    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    slides = slides_data or build_adaptive_slides(topic_id, title, slide_count=slide_count)
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
        "total_slides": len(slides),
    }


def generate_carousel(
    topic_id: str,
    title: str,
    slides_data: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[Path] = None,
    theme: str = "cyan",
    overwrite: bool = False,
    slide_count: Optional[int] = None,
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
                    overwrite=overwrite,
                    slide_count=slide_count,
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
                overwrite=overwrite,
                slide_count=slide_count,
            )
        )
