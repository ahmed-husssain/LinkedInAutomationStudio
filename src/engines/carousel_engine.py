"""
High-Resolution 4-Slide LinkedIn Carousel Generator.
Produces Apple-grade technical carousels with optical typography,
specular glass cards, and native multi-page PDF compilation.
Zero added dependencies; uses Playwright Chromium with native Pillow fallback.
"""

import os
import re
import html as html_lib
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


def resolve_topic_profile(
    topic_id: str,
    title: str,
    angle_content: Optional[str] = None,
    feedback: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolves domain-accurate architectural specs, failure logs, and topologies
    for any topic in the topic pool or custom AI topic.
    """
    base_id = re.sub(r"_\d{9,}$", "", (topic_id or "").lower()).strip()
    clean_title = (title or topic_id or "Distributed Architecture").strip()
    lookup = f"{base_id} {clean_title.lower()} {(angle_content or '').lower()}"

    # Default profile for unknown or generic topics
    profile = {
        "title": clean_title,
        "subtitle": "How staff engineers design zero-downtime distributed systems under extreme load.",
        "kpi_1": ("SCALE TARGET", "150k req/s"),
        "kpi_2": ("AVAILABILITY", "99.999% SLA"),
        "kpi_3": ("DATA DRIFT", "0% Loss"),
        "bottleneck_title": "Cascading Contention",
        "bottleneck_sub": "Why synchronous shared-state writes bring down downstream microservices.",
        "fail_pattern": "Synchronous RPC calls queue up behind unindexed database row-locks. Connection pools exhaust within 8 seconds.",
        "specimen_file": f"{base_id or 'incident'}_lockup.log",
        "specimen_body": "[FATAL] remaining connection slots are reserved for non-replication superuser connections<br>[ALERT] thread pool starved: 512/512 active workers blocked",
        "fail_timeline": "p99 latency jumps from 18ms to 4,850ms. Health checks fail, triggering an accidental thundering herd restart loop.",
        "solution_title": "Decoupled Event Streams",
        "solution_sub": "Replacing synchronous lock contention with partitioned queue buffers and read replicas.",
        "topology": {
            "ingress_label": "Edge Gateway",
            "ingress_metric": "50k rps",
            "worker_label": "Stateless Workers",
            "worker_metric": "Autoscaling",
            "queue_label": "Buffer Stream",
            "queue_metric": "16 Partitions",
            "store_label": "Read Replicas",
            "store_metric": "p99 4.2ms",
        },
        "invariant": "Writes buffer safely into partitions; read replicas serve p99 queries in under 5ms without table locking.",
        "rule_1": ("Enforce Timeout Budgets", "Apply jittered exponential backoffs on all downstream RPC calls."),
        "rule_2": ("Partition by High-Cardinality Keys", "Prevent hot partitions and rebalance overhead under sudden traffic surges."),
        "gain": "Decoupled throughput; failure isolation across all downstream services.",
        "cost": "Requires handling eventual consistency and asynchronous out-of-order retries.",
        "seq_steps": ["Request Ingress", "Buffer Stream", "Worker Processing", "Atomic Store Write", "Async Client ACK"],
        "sysctl_file": "/etc/sysctl.conf",
        "sysctl_body": "fs.file-max = 2097152<br>net.ipv4.tcp_max_syn_backlog = 65536<br>net.core.somaxconn = 65535<br>net.ipv4.tcp_rmem = 4096 87380 16777216",
        "metric_1": ("p99 LATENCY", "4.2ms (STABLE)"),
        "metric_2": ("DEPLOYMENT SAFETY", "Zero-Downtime Blue/Green"),
    }

    # 1. JWT Revocation & Stateless Auth Myth
    if any(k in lookup for k in ["jwt", "token", "session", "revocation"]):
        profile.update({
            "title": "The JWT Revocation Dilemma",
            "subtitle": "Why revoking a compromised token forces you back to Redis state anyway.",
            "kpi_1": ("AUTH OVERHEAD", "O(1) Local RS256"),
            "kpi_2": ("REVOCATION", "15m Blindspot"),
            "kpi_3": ("REPLAY DEFENSE", "Token Families"),
            "bottleneck_title": "The 15-Minute Blindspot",
            "bottleneck_sub": "Why compromised bearer tokens bypass edge gateways until TTL expiry.",
            "fail_pattern": "A compromised JWT bearer token continues authorizing high-privilege API mutations until TTL expiration, with zero gateway rejection.",
            "specimen_file": "jwt_revocation.log",
            "specimen_body": "[SEC_ALERT] Reused refresh_token detected for user_id=8842<br>[REVOCATION_BLINDSPOT] Stolen access_token valid for 14m18s across 18 edge services",
            "fail_timeline": "Immediate revocation requires a centralized blocklist—re-introducing the exact Redis bottleneck JWTs were chosen to eliminate.",
            "solution_title": "Ephemeral Access + Rotating Refresh",
            "solution_sub": "5-minute short-lived RS256 tokens paired with stateful Redis token families.",
            "topology": {
                "ingress_label": "Edge Gateway",
                "ingress_metric": "RS256 Verify",
                "worker_label": "Microservices",
                "worker_metric": "Local Parse",
                "queue_label": "Redis Blocklist",
                "queue_metric": "Revocation Bloom",
                "store_label": "Token Families",
                "store_metric": "Redis Cluster",
            },
            "invariant": "Access tokens live for 5 minutes max; refresh token rotation detects reuse instantly and revokes the entire token family.",
            "rule_1": ("Cap Access TTL at 5 Minutes", "Minimize the compromise window without hammering central auth servers on every RPC."),
            "rule_2": ("Token Family Invalidation", "If an expired or consumed refresh token is replayed, immediately invalidate all child tokens in Redis."),
            "gain": "Sub-millisecond local RS256 verification across 100+ services without central DB hits.",
            "cost": "Requires maintaining a Redis revocation set or Bloom filter for immediate session termination.",
            "seq_steps": ["User Auth (POST /token)", "Issue RS256 (5m TTL)", "Local Signature Verify", "Refresh Token Replay", "Cascade Invalidation"],
            "sysctl_file": "auth_policy.json",
            "sysctl_body": "{\\n  \\\"jwt_access_ttl_seconds\\\": 300,\\n  \\\"refresh_token_ttl_seconds\\\": 604800,\\n  \\\"rotate_refresh_tokens\\\": true,\\n  \\\"revoke_token_family_on_reuse\\\": true\\n}",
            "metric_1": ("REVOCATION LATENCY", "< 1ms in Redis"),
            "metric_2": ("CRYPTO ALGORITHM", "RS256 Asymmetric"),
        })

    # 2. OAuth 2.0 & PKCE
    elif any(k in lookup for k in ["oauth", "pkce"]):
        profile.update({
            "title": "OAuth 2.0 & PKCE Security",
            "subtitle": "Why public clients cannot hold secrets and why PKCE is mandatory.",
            "kpi_1": ("CLIENT TYPE", "Public / Mobile"),
            "kpi_2": ("VERIFIER", "SHA-256 S256"),
            "kpi_3": ("REPLAY RISK", "One-Time Code"),
            "bottleneck_title": "Secret Decompilation & Interception",
            "bottleneck_sub": "Why mobile apps and SPAs cannot keep client secrets safe.",
            "fail_pattern": "Mobile apps decompiled by attackers reveal hardcoded client secrets, enabling authorization code interception attacks.",
            "specimen_file": "auth_intercept.log",
            "specimen_body": "[SEC_WARN] Auth code interception detected on custom URI scheme<br>[FAIL] Client secret decompiled from Android APK binary",
            "fail_timeline": "Malicious apps registered to custom URI schemes steal auth codes and impersonate users.",
            "solution_title": "Dynamic PKCE Code Exchange",
            "solution_sub": "Binding one-time authorization codes with dynamic SHA-256 verifiers.",
            "topology": {
                "ingress_label": "Mobile / SPA",
                "ingress_metric": "code_challenge",
                "worker_label": "Auth Server",
                "worker_metric": "code_verifier",
                "queue_label": "Token Exchange",
                "queue_metric": "One-Time Code",
                "store_label": "Resource Server",
                "store_metric": "Scoped Bearer",
            },
            "invariant": "PKCE dynamically binds authorization codes to the client using cryptographic code verifiers and SHA-256 challenges.",
            "rule_1": ("Mandate PKCE on All Public Clients", "Never embed client secrets in browser single-page apps or mobile bundles."),
            "rule_2": ("Single-Use Authorization Codes", "Expire authorization codes within 60 seconds and reject any reused codes immediately."),
            "gain": "100% immune to authorization code interception without requiring embedded secrets.",
            "cost": "Requires cryptographic SHA-256 hashing and additional token exchange latency.",
            "seq_steps": ["Generate Code Verifier", "SHA-256 Challenge Sent", "User Login & Consent", "Auth Code Returned", "Exchange with Verifier"],
            "sysctl_file": "pkce_policy.json",
            "sysctl_body": "{\\n  \\\"code_challenge_method\\\": \\\"S256\\\",\\n  \\\"auth_code_ttl_seconds\\\": 60,\\n  \\\"allow_plain_challenge\\\": false,\\n  \\\"strict_redirect_uri\\\": true\\n}",
            "metric_1": ("CHALLENGE METHOD", "SHA-256 (S256)"),
            "metric_2": ("SECRET EXPOSURE", "0% Secrets in App"),
        })

    # 3. Rate Limiter (Token Bucket)
    elif any(k in lookup for k in ["rate_limit", "token_bucket", "leaky_bucket", "bucket"]):
        profile.update({
            "title": "Token Bucket: Surviving Traffic Bursts",
            "subtitle": "Permitting legitimate bursts while dropping abusive traffic in under 2ms.",
            "kpi_1": ("REFILL RATE", "Steady +1/s"),
            "kpi_2": ("BURST CAPACITY", "Instant Peak"),
            "kpi_3": ("TAIL OVERHEAD", "< 2ms Redis Lua"),
            "bottleneck_title": "Boundary Double-Spikes & Starvation",
            "bottleneck_sub": "Why fixed windows allow 2x traffic surges at minute boundaries.",
            "fail_pattern": "Fixed window rate limiters allow double-limit boundary spikes (e.g. 100 requests at 0:59 and 100 at 1:01), overloading downstream DBs.",
            "specimen_file": "rate_limit_breach.log",
            "specimen_body": "[HTTP 429] 10,000 req/s surge exceeded quota for client_id=stripe_live<br>[DROP] Throttled 8,420 unbuffered requests at API edge",
            "fail_timeline": "Synchronous unthrottled traffic spikes exhaust connection pools within 2 seconds, triggering cascading 504 gateway timeouts.",
            "solution_title": "Atomic In-Memory Token Bucket",
            "solution_sub": "Continuous steady refill with single-roundtrip Redis Lua scripts.",
            "topology": {
                "ingress_label": "Envoy Gateway",
                "ingress_metric": "100k rps",
                "worker_label": "Rate Limiter",
                "worker_metric": "Atomic Lua",
                "queue_label": "Redis Token Bucket",
                "queue_metric": "TTL Keys",
                "store_label": "Protected DB",
                "store_metric": "Nominal 200 OK",
            },
            "invariant": "Tokens refill continuously at a deterministic rate; requests consume tokens instantly without database lock contention.",
            "rule_1": ("Enforce Atomic Lua Evaluation", "Never run separate INCR and EXPIRE commands to prevent race conditions during traffic spikes."),
            "rule_2": ("Send Jittered Retry Headers", "Always return Retry-After with randomized jitter to prevent client retry thundering herds."),
            "gain": "Protects backend infrastructure from DDOS while transparently supporting bursty user traffic.",
            "cost": "Adds sub-2ms Redis roundtrip to each ingress request and requires memory per active rate limit key.",
            "seq_steps": ["Request Hits Gateway", "Redis Lua Token Check", "Token Available? Decr", "Quota Exceeded -> 429", "Async Refill Background"],
            "sysctl_file": "rate_limit.lua",
            "sysctl_body": "local key = KEYS[1]\\nlocal capacity = tonumber(ARGV[1])\\nlocal current = tonumber(redis.call('get', key) or capacity)\\nif current > 0 then\\n  redis.call('decr', key)\\n  return 1\\nelse\\n  return 0\\nend",
            "metric_1": ("EVALUATION TIME", "< 1.8ms Redis Lua"),
            "metric_2": ("BURST TOLERANCE", "100% Burst Safe"),
        })

    # 4. Postgres B-Tree vs UUIDv4 / UUIDv7
    elif any(k in lookup for k in ["sql_index", "btree", "uuid", "uuidv4", "uuidv7"]):
        profile.update({
            "title": "Postgres B-Trees vs Random UUIDs",
            "subtitle": "Random 128-bit page splits and cache thrashing vs sequential UUIDv7.",
            "kpi_1": ("KEY LOCALITY", "Random 128-bit"),
            "kpi_2": ("PAGE SPLIT RATE", "50% on Insert"),
            "kpi_3": ("CACHE HIT RATIO", "Drops 99% -> 62%"),
            "bottleneck_title": "B-Tree Page Split Amplification",
            "bottleneck_sub": "Why random 128-bit UUID inserts thrash disk buffer pools.",
            "fail_pattern": "UUIDv4 values are uniformly random across 128 bits, forcing Postgres to insert into random B-Tree leaf pages across gigabytes of disk.",
            "specimen_file": "postgres_io_stall.log",
            "specimen_body": "[IO_STALL] Buffer pool miss: page split on btree leaf pg_catalog.idx_orders_uuid<br>[WARN] Random disk seek read latency spiked to 48.2ms",
            "fail_timeline": "As the index exceeds RAM buffer pool size, every insert triggers a random disk seek and expensive 50% B-Tree page splits.",
            "solution_title": "Time-Ordered Sequential UUIDv7",
            "solution_sub": "Preserving global uniqueness with append-only leaf page locality.",
            "topology": {
                "ingress_label": "App Mutations",
                "ingress_metric": "Insert UUID",
                "worker_label": "Postgres Engine",
                "worker_metric": "B-Tree Walker",
                "queue_label": "WAL Buffer",
                "queue_metric": "Sequential Log",
                "store_label": "B-Tree Leaf Pages",
                "store_metric": "UUIDv7 Append",
            },
            "invariant": "Time-ordered UUIDv7 keys preserve uniqueness while ensuring append-only locality at the right edge of B-Tree pages.",
            "rule_1": ("Switch to UUIDv7 or ULID", "Embed millisecond timestamps in primary keys to eliminate random B-Tree page fragmentation."),
            "rule_2": ("Tune Index Fillfactor to 85", "Reserve headroom inside B-Tree pages for concurrent page growth without cascading splits."),
            "gain": "10x faster insert throughput and 80% reduction in disk I/O write amplification.",
            "cost": "Timestamp exposure in primary key reveals creation time (use separate surrogate key if creation time is sensitive).",
            "seq_steps": ["Generate UUIDv7 (ms TS)", "App Ingestion Pipeline", "WAL Sequential Write", "Right-Edge BTree Append", "Buffer Cache Retained"],
            "sysctl_file": "postgres_btree.sql",
            "sysctl_body": "-- Benchmark: UUIDv7 vs UUIDv4 B-Tree Fragmentation\\nCREATE EXTENSION IF NOT EXISTS pgcrypto;\\n-- UUIDv7 preserves sequential append locality\\nALTER TABLE orders ALTER COLUMN id SET DEFAULT uuid_generate_v7();",
            "metric_1": ("INSERT THROUGHPUT", "10x Faster Append"),
            "metric_2": ("BUFFER HIT RATIO", "99.4% in RAM"),
        })

    # 5. WebSockets & C10M Concurrency
    elif any(k in lookup for k in ["websocket", "socket", "10m", "c10m"]):
        profile.update({
            "title": "10 Million Sockets: Scaling WebSockets",
            "subtitle": "Epoll event loops, memory footprints (2.4KB vs 2MB), and reconnect storms.",
            "kpi_1": ("SCALE TARGET", "10M Sockets"),
            "kpi_2": ("RAM / SOCKET", "2.4 KB Pool"),
            "kpi_3": ("THROUGHPUT", "1.5M msg/s"),
            "bottleneck_title": "Kernel & Thread Collapse",
            "bottleneck_sub": "Why thread-per-connection blocking models collapse under scale.",
            "fail_pattern": "Operating system threads allocate 2MB stack space per connection. 100k threads demand 200GB RAM, triggering OOM-killer.",
            "specimen_file": "kernel_panic.log",
            "specimen_body": "[ERR_FD_EXHAUSTED] accept(): too many open files (max=65535)<br>[OOM_KILLER] Invoked oom-killer: gfp_mask=0x100cca(GFP_HIGHUSER)",
            "fail_timeline": "p99 latency spikes from 12ms to 6,200ms. Keepalive probes timeout, generating a recursive reconnect avalanche.",
            "solution_title": "Decoupled Epoll Event Mesh",
            "solution_sub": "Stateless epoll connection workers connected via partitioned stream buffers.",
            "topology": {
                "ingress_label": "L4 Proxy (IP Hash)",
                "ingress_metric": "1M rps",
                "worker_label": "Epoll Edge Tier",
                "worker_metric": "10M Conns",
                "queue_label": "Partitioned Bus",
                "queue_metric": "64 Partitions",
                "store_label": "Raft Store",
                "store_metric": "p99 3.2ms",
            },
            "invariant": "Workers register socket file descriptors with non-blocking epoll event loops, reducing memory from 2MB to 2.4KB per socket.",
            "rule_1": ("Set ulimit -n 1048576", "Prevent default Linux 1024 file descriptor exhaustion on socket creation."),
            "rule_2": ("Enforce Heartbeat Jitter", "Stagger ping/pong intervals by +/- 20% to avoid synchronized heartbeat bursts."),
            "gain": "100x Concurrency density; sub-5ms broadcast to 10M subscribers.",
            "cost": "Requires strict TCP socket buffer tuning and partitioned backpressure buffers.",
            "seq_steps": ["TCP SYN Handshake", "HTTP 101 Upgrade", "Epoll Registration", "Pub/Sub Broadcast", "Client Frame ACK"],
            "sysctl_file": "/etc/sysctl.conf",
            "sysctl_body": "fs.file-max = 2097152<br>net.ipv4.tcp_max_syn_backlog = 65536<br>net.core.somaxconn = 65535<br>net.ipv4.tcp_rmem = 4096 87380 16777216",
            "metric_1": ("RESTORED p99 LATENCY", "3.2ms (STABLE)"),
            "metric_2": ("MEMORY PER SOCKET", "2.4 KB (-99.8%)"),
        })

    # 6. LinkedIn Automation Studio / Autonomous Content Engine
    elif any(k in lookup for k in ["linkedin_studio", "autonomous_studio", "studio", "how_i_built", "automation_studio"]):
        profile.update({
            "title": "Automating 60fps Content in Python",
            "subtitle": "Replacing manual Canva & Figma drag-and-drop toil with deterministic code.",
            "kpi_1": ("BUILD TIME", "15s / Deck"),
            "kpi_2": ("CLOUD COST", "$0 / Zero SaaS"),
            "kpi_3": ("ACCURACY", "100% Code-Driven"),
            "bottleneck_title": "The Manual Content Toil",
            "bottleneck_sub": "Why manual carousel editing in Figma/Canva wastes 45 minutes per post.",
            "fail_pattern": "Engineers spend 45 minutes manually aligning text boxes, kerning fonts, and adjusting layout drift across multiple slides.",
            "specimen_file": "studio_pipeline.py",
            "specimen_body": "# Deterministic Autonomous Studio Pipeline<br>pdf = await render_carousel(topic, slides=3, crf=18)<br>video = await render_manim(topic, fps=60, pts=1.4)<br>await approval_gate.stage(pdf, video)",
            "fail_timeline": "Manual post creation causes creator burnout. Inconsistency across slides leads to broken visual hierarchy.",
            "solution_title": "Headless Studio Architecture",
            "solution_sub": "Discord mobile bot triggering Playwright HTML rendering and Manim CE compilation.",
            "topology": {
                "ingress_label": "Discord Bot",
                "ingress_metric": "1-Tap Trigger",
                "worker_label": "Topic Engine",
                "worker_metric": "Adaptive Depth",
                "queue_label": "Playwright / Manim",
                "queue_metric": "60fps & PDF",
                "store_label": "Approval Gate",
                "store_metric": "Mobile 1-Tap",
            },
            "invariant": "Every technical post, multi-page PDF carousel, and 60fps animation compiles in under 15 seconds with zero SaaS fees.",
            "rule_1": ("Never Hand-Draw Architecture", "Code SVGs and Manim scenes deterministically to eliminate layout drift."),
            "rule_2": ("Enforce Mobile Approval Gates", "Never auto-publish without a private Discord staging channel and 1-tap approve/reject gates."),
            "gain": "Turns 45 minutes of manual Canva tweaking into 15 seconds from your phone.",
            "cost": "Requires local Playwright, Manim, and FFmpeg toolchains rather than simple cloud wrappers.",
            "seq_steps": ["Discord Topic Trigger", "Adaptive Layout Synthesis", "Playwright PDF Render", "FFmpeg Pacing Adjust", "Mobile Approval Delivery"],
            "sysctl_file": "studio_manifest.yaml",
            "sysctl_body": "studio:<br>  viewport: { width: 1080, height: 1350 }<br>  video: { fps: 60, codec: libx264, crf: 18 }<br>  approval_timeout: 86400s",
            "metric_1": ("PIPELINE SPEED", "14.2s End-to-End"),
            "metric_2": ("OUTPUT STANDARD", "1080p 60fps Crisp"),
        })

    # Apply user feedback customization if provided
    if feedback:
        fb_clean = feedback.strip()
        profile["rule_1"] = (
            f"Refined Constraint: {html_lib.escape(fb_clean[:32])}",
            f"Addressed user architectural feedback: {html_lib.escape(fb_clean)}"
        )
        profile["feedback_note"] = html_lib.escape(fb_clean)

    return profile


def build_adaptive_slides(
    topic_id: str,
    title: str,
    slide_count: Optional[int] = None,
    accent: str = "#38bdf8",
    angle_content: Optional[str] = None,
    senior_question: Optional[str] = None,
    feedback: Optional[str] = None,
    custom_instructions: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Builds a high-density, publication-grade carousel narrative strictly
    between 3 and 5 slides, completely eliminating empty canvas void.
    """
    clean_title = (title or topic_id).strip()
    count = slide_count or resolve_carousel_slide_count(topic_id, title)
    count = max(3, min(5, count))

    effective_feedback = feedback or custom_instructions
    profile = resolve_topic_profile(topic_id, title, angle_content=angle_content, feedback=effective_feedback)
    topic_title = profile.get("title", clean_title)
    topic_sub = profile.get("subtitle", "")

    topo = profile["topology"]

    feedback_html = ""
    if profile.get("feedback_note"):
        feedback_html = f"""
        <div class="narrative-block highlight" style="border-color: #10b981; background: rgba(16, 185, 129, 0.08);">
          <span class="block-tag" style="color: #10b981;">User Feedback Adjustment</span>
          <p class="block-text">{profile['feedback_note']}</p>
        </div>
        """

    if count == 3:
        return [
            {
                "slide_number": 1,
                "badge": "MENTAL MODEL 101",
                "title": topic_title,
                "subtitle": topic_sub,
                "stage_html": f"""
                <div class="scale-matrix">
                  <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_1'][0]}</span><span class="scale-kpi-val">{profile['kpi_1'][1]}</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_2'][0]}</span><span class="scale-kpi-val">{profile['kpi_2'][1]}</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_3'][0]}</span><span class="scale-kpi-val">{profile['kpi_3'][1]}</span></div>
                </div>
                {feedback_html}
                <div class="narrative-block highlight">
                  <span class="block-tag">Core Principle</span>
                  <p class="block-text">{profile['invariant']}</p>
                </div>
                <div class="config-specimen">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">{profile['specimen_file']}</span></div>
                  <div class="specimen-body">{profile['specimen_body']}</div>
                </div>
                """,
                "metric_1_label": profile['metric_1'][0],
                "metric_1_val": profile['metric_1'][1],
                "metric_2_label": profile['metric_2'][0],
                "metric_2_val": profile['metric_2'][1],
                "swipe_hint": "Swipe for Mechanism →",
            },
            {
                "slide_number": 2,
                "badge": "ARCHITECTURE & MECHANISM",
                "title": f"The Mechanism: {profile['solution_title']}",
                "subtitle": profile['solution_sub'],
                "stage_html": f"""
                {render_full_width_topology(width=880, height=220, ingress_label=topo['ingress_label'], ingress_metric=topo.get('ingress_metric'), worker_label=topo['worker_label'], worker_metric=topo.get('worker_metric'), queue_label=topo['queue_label'], queue_metric=topo.get('queue_metric'), store_label=topo['store_label'], store_metric=topo.get('store_metric'), accent=accent)}
                <div class="tradeoff-grid" style="margin: 4px 0;">
                  <div class="tradeoff-card" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);">
                    <span class="tradeoff-tag" style="color: var(--accent);">INGRESS PIPELINE</span>
                    <span class="tradeoff-text" style="color: #f1f5f9; font-weight: 600;">{topo['ingress_label']} ({topo.get('ingress_metric', 'Active')})</span>
                  </div>
                  <div class="tradeoff-card" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);">
                    <span class="tradeoff-tag" style="color: #10b981;">CORE INVARIANT</span>
                    <span class="tradeoff-text" style="color: #f1f5f9; font-weight: 600;">{topo['store_label']} ({topo.get('store_metric', 'Deterministic')})</span>
                  </div>
                </div>
                <div class="narrative-block highlight">
                  <span class="block-tag">Architectural Invariant</span>
                  <p class="block-text">{profile['invariant']}</p>
                </div>
                """,
                "metric_1_label": profile['metric_1'][0],
                "metric_1_val": profile['metric_1'][1],
                "metric_2_label": profile['metric_2'][0],
                "metric_2_val": profile['metric_2'][1],
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
                  <div class="playbook-content"><span class="playbook-title">{profile['rule_1'][0]}</span><span class="playbook-sub">{profile['rule_1'][1]}</span></div>
                </div>
                <div class="playbook-card">
                  <span class="playbook-num">RULE 2</span>
                  <div class="playbook-content"><span class="playbook-title">{profile['rule_2'][0]}</span><span class="playbook-sub">{profile['rule_2'][1]}</span></div>
                </div>
                <div class="config-specimen" style="margin: 4px 0;">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">{profile.get('sysctl_file', 'production_rules.env')}</span></div>
                  <div class="specimen-body">{profile.get('sysctl_body', 'VERIFY_FAILOVER=true<br>CIRCUIT_BREAKER_MAX_RETRIES=3<br>TIMEOUT_MS=250')}</div>
                </div>
                <div class="tradeoff-grid">
                  <div class="tradeoff-card gain"><span class="tradeoff-tag" style="color: #10b981;">ARCHITECTURAL GAIN</span><span class="tradeoff-text">{profile['gain']}</span></div>
                  <div class="tradeoff-card cost"><span class="tradeoff-tag" style="color: #f59e0b;">KNOWN TRADE-OFF</span><span class="tradeoff-text">{profile['cost']}</span></div>
                </div>
                """,
                "metric_1_label": profile['metric_1'][0],
                "metric_1_val": profile['metric_1'][1],
                "metric_2_label": profile['metric_2'][0],
                "metric_2_val": profile['metric_2'][1],
                "swipe_hint": "Save & Share for Reference",
            },
        ]

    elif count == 5:
        return [
            {
                "slide_number": 1,
                "badge": "SCALE BENCHMARK",
                "title": topic_title,
                "subtitle": topic_sub,
                "stage_html": f"""
                <div class="scale-matrix">
                  <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_1'][0]}</span><span class="scale-kpi-val">{profile['kpi_1'][1]}</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_2'][0]}</span><span class="scale-kpi-val">{profile['kpi_2'][1]}</span></div>
                  <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_3'][0]}</span><span class="scale-kpi-val">{profile['kpi_3'][1]}</span></div>
                </div>
                {feedback_html}
                <div class="narrative-block highlight">
                  <span class="block-tag">The Core Challenge</span>
                  <p class="block-text">{profile['fail_pattern']}</p>
                </div>
                <div class="narrative-block">
                  <span class="block-tag">System Blueprint Journey</span>
                  <p class="block-text">Swipe left to inspect the failure bottleneck, decoupled topology, protocol flow, and production runbook.</p>
                </div>
                """,
                "metric_1_label": profile['metric_1'][0],
                "metric_1_val": profile['metric_1'][1],
                "metric_2_label": profile['metric_2'][0],
                "metric_2_val": profile['metric_2'][1],
                "swipe_hint": "Swipe for Naive Bottleneck →",
            },
            {
                "slide_number": 2,
                "badge": "ANATOMY OF FAILURE",
                "title": f"The Bottleneck: {profile['bottleneck_title']}",
                "subtitle": profile['bottleneck_sub'],
                "stage_html": f"""
                <div class="narrative-block" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
                  <span class="block-tag" style="color: #ef4444;">Failure Pattern</span>
                  <p class="block-text">{profile['fail_pattern']}</p>
                </div>
                <div class="config-specimen">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">{profile['specimen_file']}</span></div>
                  <div class="specimen-body">{profile['specimen_body']}</div>
                </div>
                <div class="narrative-block" style="border-color: #f59e0b; background: rgba(245, 158, 11, 0.08);">
                  <span class="block-tag" style="color: #f59e0b;">Degradation Timeline</span>
                  <p class="block-text">{profile['fail_timeline']}</p>
                </div>
                """,
                "metric_1_label": "UNHANDLED FAILURE",
                "metric_1_val": "Critical Alert",
                "metric_2_label": "p99 IMPACT",
                "metric_2_val": "Severe Degradation",
                "swipe_hint": "Swipe for Decoupled Mesh →",
            },
            {
                "slide_number": 3,
                "badge": "DISTRIBUTED TOPOLOGY",
                "title": f"The Solution: {profile['solution_title']}",
                "subtitle": profile['solution_sub'],
                "stage_html": f"""
                {render_full_width_topology(width=880, height=220, ingress_label=topo['ingress_label'], ingress_metric=topo.get('ingress_metric'), worker_label=topo['worker_label'], worker_metric=topo.get('worker_metric'), queue_label=topo['queue_label'], queue_metric=topo.get('queue_metric'), store_label=topo['store_label'], store_metric=topo.get('store_metric'), accent=accent)}
                <div class="narrative-block highlight">
                  <span class="block-tag">Architectural Invariant</span>
                  <p class="block-text">{profile['invariant']}</p>
                </div>
                """,
                "metric_1_label": profile['metric_1'][0],
                "metric_1_val": profile['metric_1'][1],
                "metric_2_label": profile['metric_2'][0],
                "metric_2_val": profile['metric_2'][1],
                "swipe_hint": "Swipe for Protocol Flow →",
            },
            {
                "slide_number": 4,
                "badge": "PROTOCOL FLOW & TRADE-OFFS",
                "title": "Temporal Flow & Senior Trade-Offs",
                "subtitle": "The complete execution lifecycle and its architectural costs.",
                "stage_html": f"""
                {render_sequence_flow_svg(profile['seq_steps'], width=880, height=75, accent=accent)}
                <div class="tradeoff-grid">
                  <div class="tradeoff-card gain">
                    <span class="tradeoff-tag" style="color: #10b981;">ARCHITECTURAL GAIN</span>
                    <span class="tradeoff-text">{profile['gain']}</span>
                  </div>
                  <div class="tradeoff-card cost">
                    <span class="tradeoff-tag" style="color: #f59e0b;">OPERATIONAL GOTCHA</span>
                    <span class="tradeoff-text">{profile['cost']}</span>
                  </div>
                </div>
                """,
                "metric_1_label": profile['metric_1'][0],
                "metric_1_val": profile['metric_1'][1],
                "metric_2_label": profile['metric_2'][0],
                "metric_2_val": profile['metric_2'][1],
                "swipe_hint": "Swipe for Production Runbook →",
            },
            {
                "slide_number": 5,
                "badge": "PRODUCTION RUNBOOK",
                "title": "Staff Engineer Runbook",
                "subtitle": "Exact parameters and operational rules for production readiness.",
                "stage_html": f"""
                <div class="config-specimen">
                  <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">{profile['sysctl_file']}</span></div>
                  <div class="specimen-body">{profile['sysctl_body']}</div>
                </div>
                <div class="playbook-card">
                  <span class="playbook-num">RULE 1</span>
                  <div class="playbook-content"><span class="playbook-title">{profile['rule_1'][0]}</span><span class="playbook-sub">{profile['rule_1'][1]}</span></div>
                </div>
                <div class="playbook-card">
                  <span class="playbook-num">RULE 2</span>
                  <div class="playbook-content"><span class="playbook-title">{profile['rule_2'][0]}</span><span class="playbook-sub">{profile['rule_2'][1]}</span></div>
                </div>
                """,
                "metric_1_label": "RUNBOOK STATUS",
                "metric_1_val": "Production Ready",
                "metric_2_label": "RESILIENCE MODEL",
                "metric_2_val": "Active-Active Verified",
                "swipe_hint": "Save & Share for Reference",
            },
        ]

    # Default 4-slide structure (Incident Post-Mortem & Architecture)
    return [
        {
            "slide_number": 1,
            "badge": "SYSTEM ARCHITECTURE",
            "title": topic_title,
            "subtitle": topic_sub,
            "stage_html": f"""
            <div class="scale-matrix">
              <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_1'][0]}</span><span class="scale-kpi-val">{profile['kpi_1'][1]}</span></div>
              <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_2'][0]}</span><span class="scale-kpi-val">{profile['kpi_2'][1]}</span></div>
              <div class="scale-kpi"><span class="scale-kpi-label">{profile['kpi_3'][0]}</span><span class="scale-kpi-val">{profile['kpi_3'][1]}</span></div>
            </div>
            {feedback_html}
            <div class="narrative-block highlight">
              <span class="block-tag">The Core Challenge</span>
              <p class="block-text">{profile['fail_pattern']}</p>
            </div>
            <div class="narrative-block">
              <span class="block-tag">Architectural Blueprint</span>
              <p class="block-text">Swipe left to dissect the failure mode, the decoupled topology, and the staff checklist.</p>
            </div>
            """,
            "metric_1_label": profile['metric_1'][0],
            "metric_1_val": profile['metric_1'][1],
            "metric_2_label": profile['metric_2'][0],
            "metric_2_val": profile['metric_2'][1],
            "swipe_hint": "Swipe for Failure Mode →",
        },
        {
            "slide_number": 2,
            "badge": "INCIDENT POST-MORTEM",
            "title": f"The Bottleneck: {profile['bottleneck_title']}",
            "subtitle": profile['bottleneck_sub'],
            "stage_html": f"""
            <div class="narrative-block" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
              <span class="block-tag" style="color: #ef4444;">Failure Pattern</span>
              <p class="block-text">{profile['fail_pattern']}</p>
            </div>
            <div class="config-specimen">
              <div class="specimen-header"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div><span class="specimen-title">{profile['specimen_file']}</span></div>
              <div class="specimen-body">{profile['specimen_body']}</div>
            </div>
            <div class="narrative-block" style="border-color: #f59e0b; background: rgba(245, 158, 11, 0.08);">
              <span class="block-tag" style="color: #f59e0b;">Degradation Timeline</span>
              <p class="block-text">{profile['fail_timeline']}</p>
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
            "title": f"The Solution: {profile['solution_title']}",
            "subtitle": profile['solution_sub'],
            "stage_html": f"""
            {render_full_width_topology(width=880, height=220, ingress_label=topo['ingress_label'], ingress_metric=topo.get('ingress_metric'), worker_label=topo['worker_label'], worker_metric=topo.get('worker_metric'), queue_label=topo['queue_label'], queue_metric=topo.get('queue_metric'), store_label=topo['store_label'], store_metric=topo.get('store_metric'), accent=accent)}
            <div class="narrative-block highlight">
              <span class="block-tag">Architectural Invariant</span>
              <p class="block-text">{profile['invariant']}</p>
            </div>
            """,
            "metric_1_label": profile['metric_1'][0],
            "metric_1_val": profile['metric_1'][1],
            "metric_2_label": profile['metric_2'][0],
            "metric_2_val": profile['metric_2'][1],
            "swipe_hint": "Swipe for Staff Checklist →",
        },
        {
            "slide_number": 4,
            "badge": "PRODUCTION PLAYBOOK",
            "title": "Staff Engineer Checklist",
            "subtitle": "Guiding rules to audit your distributed architecture before hitting production.",
            "stage_html": f"""
            <div class="playbook-card">
              <span class="playbook-num">RULE 1</span>
              <div class="playbook-content"><span class="playbook-title">{profile['rule_1'][0]}</span><span class="playbook-sub">{profile['rule_1'][1]}</span></div>
            </div>
            <div class="playbook-card">
              <span class="playbook-num">RULE 2</span>
              <div class="playbook-content"><span class="playbook-title">{profile['rule_2'][0]}</span><span class="playbook-sub">{profile['rule_2'][1]}</span></div>
            </div>
            <div class="tradeoff-grid">
              <div class="tradeoff-card gain">
                <span class="tradeoff-tag" style="color: #10b981;">ARCHITECTURAL GAIN</span>
                <span class="tradeoff-text">{profile['gain']}</span>
              </div>
              <div class="tradeoff-card cost">
                <span class="tradeoff-tag" style="color: #f59e0b;">KNOWN CEILING</span>
                <span class="tradeoff-text">{profile['cost']}</span>
              </div>
            </div>
            """,
            "metric_1_label": profile['metric_1'][0],
            "metric_1_val": profile['metric_1'][1],
            "metric_2_label": profile['metric_2'][0],
            "metric_2_val": profile['metric_2'][1],
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
    raw_placeholders = {
        "{{STAGE_HTML}}",
        "{{THEME_ACCENT}}",
        "{{THEME_GLOW}}",
        "{{CANVAS_WIDTH}}",
        "{{CANVAS_HEIGHT}}",
        "{{SLIDE_NUMBER}}",
        "{{TOTAL_SLIDES}}",
    }
    for placeholder, val in replacements.items():
        val_str = str(val) if placeholder in raw_placeholders else html_lib.escape(str(val))
        html = html.replace(placeholder, val_str)
    return html


async def generate_carousel_async(
    topic_id: str,
    title: str,
    slides_data: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[Path] = None,
    theme: str = "cyan",
    overwrite: bool = False,
    slide_count: Optional[int] = None,
    angle_content: Optional[str] = None,
    senior_question: Optional[str] = None,
    feedback: Optional[str] = None,
    custom_instructions: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Asynchronously generates an adaptive 3-to-5 slide carousel:
    - 3, 4, or 5 PNG slide images (1080x1350 4:5 vertical carousel format)
    - 1 compiled multi-page PDF document for LinkedIn
    """
    target_dir = output_dir or THUMBNAILS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    theme_cfg = CAROUSEL_THEMES.get(theme, CAROUSEL_THEMES["cyan"])
    slides = slides_data or build_adaptive_slides(
        topic_id,
        title,
        slide_count=slide_count,
        accent=theme_cfg["accent"],
        angle_content=angle_content,
        senior_question=senior_question,
        feedback=feedback,
        custom_instructions=custom_instructions,
    )
    canvas_spec = CANVAS_ASPECT_RATIOS["portrait"]
    width = canvas_spec["width"]
    height = canvas_spec["height"]

    safe_topic_id = Path(topic_id).name
    pdf_path = (target_dir / f"{safe_topic_id}_Carousel_{theme}.pdf").resolve()
    if not pdf_path.is_relative_to(target_dir.resolve()):
        raise ValueError(f"Security: Destination path '{pdf_path}' escapes output directory '{target_dir}'")
    slide_paths: List[Path] = []
    pil_images: List[Image.Image] = []

    from src.engines.html_renderer import render_html_to_image

    for slide in slides:
        num = slide.get("slide_number", 1)
        slide_png = (target_dir / f"{safe_topic_id}_Slide_{num}_{theme}.png").resolve()
        if not slide_png.is_relative_to(target_dir.resolve()):
            raise ValueError(f"Security: Destination path '{slide_png}' escapes output directory '{target_dir}'")
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
    angle_content: Optional[str] = None,
    senior_question: Optional[str] = None,
    feedback: Optional[str] = None,
    custom_instructions: Optional[str] = None,
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
                    angle_content=angle_content,
                    senior_question=senior_question,
                    feedback=feedback,
                    custom_instructions=custom_instructions,
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
                angle_content=angle_content,
                senior_question=senior_question,
                feedback=feedback,
                custom_instructions=custom_instructions,
            )
        )
