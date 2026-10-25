"""
LinkedIn Automation Studio — Minimalist Linear/Vercel Monochrome Dashboard.
Powered by Streamlit, Playwright, and Manim Community Edition.
Generates 1080x1350 PDF Carousels and 60fps Manim Videos with $0 cloud cost.
"""

import sys
import asyncio
from pathlib import Path

import streamlit as st
from PIL import Image

# Add repository root to Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.engines.carousel_engine import (
    generate_carousel_async,
    resolve_topic_profile,
    CAROUSEL_THEMES,
)
from src.engines.diagram_engine import (
    generate_diagram_package_async,
)
from src.engines.video_engine import (
    render_parameterized_animation_async,
    ANIMATION_REGISTRY,
)

# -----------------------------------------------------------------------------
# Pre-Engineered Curated Topic Pool
# -----------------------------------------------------------------------------
CURATED_TOPICS = {
    "jwt_vs_sessions": {
        "label": "The JWT Revocation Dilemma (Stateful Revocation)",
        "default_title": "The JWT Revocation Dilemma",
        "video_id": "oauth",
    },
    "consistent_hashing": {
        "label": "Consistent Hashing Ring Topology (Zero Rebalance Thundering)",
        "default_title": "Consistent Hashing Ring Topology",
        "video_id": "cache_aside",
    },
    "kafka_vs_rabbitmq": {
        "label": "Kafka vs. RabbitMQ (Queue vs. Log Architecture)",
        "default_title": "Kafka vs RabbitMQ: Queue vs Log",
        "video_id": "sliding_window",
    },
    "redis_cache_stampede": {
        "label": "Redis Cache Stampede & Early Expiry (Probabilistic XFetch)",
        "default_title": "Redis Cache Stampede Mitigation",
        "video_id": "cache_aside",
    },
    "distributed_locking": {
        "label": "Distributed Locks: The Fencing Token Paradox",
        "default_title": "Distributed Locks & Fencing Tokens",
        "video_id": "token_bucket",
    },
    "rate_limiting": {
        "label": "Distributed Rate Limiting at Scale (Token vs Leaky Bucket)",
        "default_title": "Distributed Rate Limiter Mechanics",
        "video_id": "token_bucket",
    },
    "postgres_vacuum_bloat": {
        "label": "Postgres MVCC Vacuum Bloat & Table Contention",
        "default_title": "Postgres MVCC Vacuum Bloat",
        "video_id": "sql_index",
    },
    "read_replica_lag": {
        "label": "Read Replica Lag: The Split-Brain Incident",
        "default_title": "Read Replica Lag & Causality",
        "video_id": "cache_aside",
    },
    "reconnect_storm": {
        "label": "10M WebSockets Reconnect Storm & Jitter Mitigation",
        "default_title": "10M Sockets Reconnect Storm",
        "video_id": "leaky_bucket",
    },
    "database_sharding": {
        "label": "Database Sharding & Cross-Partition Joins",
        "default_title": "Database Sharding Invariants",
        "video_id": "sql_index",
    },
    "raft_consensus": {
        "label": "Raft Consensus: Split Votes & Heartbeat Timeouts",
        "default_title": "Raft Consensus & Split Votes",
        "video_id": "fixed_window",
    },
    "linkedin_studio": {
        "label": "Automating 60fps Content in Python (Zero Canva Toil)",
        "default_title": "Automating 60fps Content in Python",
        "video_id": "token_bucket",
    },
}

# -----------------------------------------------------------------------------
# Streamlit App Configuration & Linear / Vercel Monochrome Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LinkedIn Automation Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Linear / Vercel Monochrome Design System */
    .stApp {
        background-color: #000000;
        color: #ededed;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    }

    /* Prevent Streamlit floating header from covering top content */
    header[data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Container Constrained Width for Calm Focus with generous top clearance */
    .block-container {
        max-width: 900px !important;
        padding-top: 5rem !important;
        padding-bottom: 4rem !important;
    }

    /* Minimal Header */
    .hero-container {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #1a1a1a;
    }
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: #111111;
        color: #888888;
        border: 1px solid #262626;
        margin-bottom: 12px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .hero-sub {
        color: #737373;
        font-size: 0.95rem;
        font-weight: 400;
        max-width: 580px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Apple-style Interactive Press */
    button, .stButton>button {
        transition: transform 120ms cubic-bezier(0.16, 1, 0.3, 1), background-color 150ms ease !important;
    }
    button:active, .stButton>button:active {
        transform: scale(0.98) !important;
    }

    /* Vercel Primary Button */
    .stButton>button[kind="primary"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: 1px solid #ffffff !important;
        padding: 0.65rem 1.5rem !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #e5e5e5 !important;
        border-color: #e5e5e5 !important;
    }

    /* Secondary Buttons */
    .stButton>button[kind="secondary"] {
        background-color: #0f0f0f !important;
        color: #d4d4d4 !important;
        border: 1px solid #222222 !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-color: #333333 !important;
    }

    /* Card Containers */
    .specimen-card {
        background: #080808;
        border: 1px solid #1a1a1a;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1rem !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #555555 !important;
        box-shadow: none !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0a0a0a;
        padding: 4px;
        border-radius: 12px;
        border: 1px solid #1c1c1c;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 6px 16px;
        color: #737373;
        font-size: 0.85rem;
        font-weight: 500;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #080808 !important;
        border: 1px solid #1c1c1c !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        color: #888888 !important;
    }
    .streamlit-expanderContent {
        background-color: #080808 !important;
        border: 1px solid #1c1c1c !important;
        border-top: none !important;
        border-bottom-left-radius: 10px !important;
        border-bottom-right-radius: 10px !important;
    }

    /* Code Block */
    pre, code {
        background-color: #050505 !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 8px !important;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        color: #d4d4d4 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "current_slide_idx" not in st.session_state:
    st.session_state.current_slide_idx = 0
if "generated_diagram" not in st.session_state:
    st.session_state.generated_diagram = None
if "generated_carousel" not in st.session_state:
    st.session_state.generated_carousel = None
if "generated_video" not in st.session_state:
    st.session_state.generated_video = None
if "generated_post" not in st.session_state:
    st.session_state.generated_post = None
if "selected_topic_input" not in st.session_state:
    st.session_state.selected_topic_input = "The JWT Revocation Dilemma (Stateful Revocation)"

# -----------------------------------------------------------------------------
# Calm Editorial Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <span class="badge-pill">Staff-Level Engineering Studio</span>
        <div class="hero-title">LinkedIn Automation Studio</div>
        <div class="hero-sub">Generate publication-grade 2D architecture blueprints, 1080x1350 PDF carousels, and 60fps vector animations in seconds.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Single-Column Hero Stage (Ruthless Restraint)
# -----------------------------------------------------------------------------
topic_input_val = st.text_input(
    "What architecture concept are you breaking down?",
    value=st.session_state.selected_topic_input,
    placeholder="e.g. Distributed Consensus in Raft, 10M WebSockets Reconnect Storm...",
    help="Type any software design topic or select a quick-preset below.",
)
st.session_state.selected_topic_input = topic_input_val

# Quick-Select Presets
col_p1, col_p2, col_p3, col_p4 = st.columns(4)
with col_p1:
    if st.button("⚡ JWT Dilemma", use_container_width=True):
        st.session_state.selected_topic_input = CURATED_TOPICS["jwt_vs_sessions"]["label"]
        st.rerun()
with col_p2:
    if st.button("⚡ Consistent Hashing", use_container_width=True):
        st.session_state.selected_topic_input = CURATED_TOPICS["consistent_hashing"]["label"]
        st.rerun()
with col_p3:
    if st.button("⚡ Kafka vs RabbitMQ", use_container_width=True):
        st.session_state.selected_topic_input = CURATED_TOPICS["kafka_vs_rabbitmq"]["label"]
        st.rerun()
with col_p4:
    if st.button("⚡ Cache Stampede", use_container_width=True):
        st.session_state.selected_topic_input = CURATED_TOPICS["redis_cache_stampede"]["label"]
        st.rerun()

# -----------------------------------------------------------------------------
# Progressive Disclosure: Collapsible Design Parameters
# -----------------------------------------------------------------------------
with st.expander("⚙️ Customize Parameters (Visual Theme, Deck Length, Video Engine)", expanded=False):
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        topic_mode = st.radio(
            "Topic Preset Library",
            ["Curated System Architecture Presets", "Custom Engineering Topic"],
            index=0 if any(cfg["label"] == st.session_state.selected_topic_input for cfg in CURATED_TOPICS.values()) else 1,
            horizontal=True,
        )
        theme_choice = st.selectbox(
            "Visual Palette Accent",
            options=list(CAROUSEL_THEMES.keys()),
            format_func=lambda t: f"{t.capitalize()} Accent",
        )
    with col_opt2:
        format_choice = st.radio(
            "Primary Visual Focus",
            [
                "📐 2D Architecture Blueprint & Post (Recommended)",
                "📑 1080x1350 PDF Carousel (Document Deck)",
                "🎬 60fps Manim 2D Animation (MP4 Video)",
            ],
        )
        slide_count = st.select_slider(
            "Carousel Deck Length",
            options=[3, 4, 5],
            value=4,
            help="3 = Fast takeaway, 4 = Incident breakdown, 5 = Deep architectural runbook",
        )

# Derive topic ID and Title
matched_key = None
for k, cfg in CURATED_TOPICS.items():
    if cfg["label"].lower() in topic_input_val.lower() or cfg["default_title"].lower() in topic_input_val.lower():
        matched_key = k
        break

if matched_key:
    topic_id = matched_key
    topic_title = CURATED_TOPICS[matched_key]["default_title"]
    video_id = CURATED_TOPICS[matched_key]["video_id"]
else:
    topic_title = topic_input_val.strip() or "System Architecture Topology"
    topic_id = (
        topic_title.lower()
        .replace(" ", "_")
        .replace(":", "")
        .replace("-", "_")
    )
    video_id = "token_bucket"

st.write("")
generate_btn = st.button("🚀 Generate LinkedIn Content Package", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Generation Logic
# -----------------------------------------------------------------------------
def run_async(coro):
    """Executes an async coroutine safely inside Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


if generate_btn:
    with st.spinner("Synthesizing architecture invariants & compiling high-res assets..."):
        output_dir = ROOT_DIR / "data" / "published"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 2D Architecture Blueprint (PNG + D2 Script + Excalidraw Whiteboard)
        diagram_res = run_async(
            generate_diagram_package_async(
                topic_id=topic_id,
                title=topic_title,
                output_dir=output_dir,
                theme=theme_choice,
                overwrite=True,
            )
        )
        st.session_state.generated_diagram = diagram_res

        # 2. 4-Slide PDF Carousel Deck
        carousel_res = run_async(
            generate_carousel_async(
                topic_id=topic_id,
                title=topic_title,
                output_dir=output_dir,
                theme=theme_choice,
                slide_count=slide_count,
                overwrite=True,
            )
        )
        st.session_state.generated_carousel = carousel_res
        st.session_state.current_slide_idx = 0

        # 3. Video generation (if video is primary focus)
        if "Animation" in format_choice or "Video" in format_choice:
            rendered_video_path = run_async(
                render_parameterized_animation_async(
                    animation_id=video_id,
                    force_render=False,
                )
            )
            st.session_state.generated_video = rendered_video_path
        else:
            st.session_state.generated_video = None

        # 4. Authentic developer post copy
        profile = resolve_topic_profile(topic_id, topic_title)
        post_copy = f"""Why your architecture might be quietly failing under peak load: {profile['title']}

Most teams start with the naive approach:
{profile['fail_pattern']}

At scale, the breakdown is brutal:
- {profile['fail_timeline']}

The staff-level mental model:
{profile['invariant']}

Two production invariants to enforce:
1. {profile['rule_1'][0]}: {profile['rule_1'][1]}
2. {profile['rule_2'][0]}: {profile['rule_2'][1]}

Architecture Trade-Off:
Gain: {profile['gain']}
Cost: {profile['cost']}

Senior Discussion:
{profile.get('senior_question', 'How does your team protect against partition rebalancing storms during peak traffic?')}

#SystemDesign #DistributedSystems #SoftwareEngineering #Backend #SoftwareArchitecture"""

        st.session_state.generated_post = post_copy
        st.toast("LinkedIn Content Package compiled successfully!", icon="✅")

# -----------------------------------------------------------------------------
# Deliverables Stage: Apple Segmented Switcher
# -----------------------------------------------------------------------------
if st.session_state.generated_diagram or st.session_state.generated_carousel or st.session_state.generated_video:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    tab_diag, tab_deck, tab_vid, tab_copy = st.tabs([
        "📐 2D Architecture Blueprint",
        "📑 4-Slide Carousel Deck",
        "🎬 60fps Motion Video",
        "📋 LinkedIn Post Copy",
    ])

    with tab_diag:
        if st.session_state.generated_diagram:
            res = st.session_state.generated_diagram
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="font-family:ui-monospace; font-size:0.8rem; color:#888;">TOPOLOGY: 1080x1080 RETINA CARD</span>
                    <span style="font-family:ui-monospace; font-size:0.8rem; color:#4ade80;">READY TO PUBLISH</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_img, col_actions = st.columns([1.3, 1], gap="medium")
            with col_img:
                img = Image.open(res["png_path"])
                st.image(img, use_container_width=True)

            with col_actions:
                st.markdown("#### Deliverable Assets")
                st.markdown("Declarative architecture diagrams formatted for technical LinkedIn posts.")

                with open(res["png_path"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Blueprint PNG",
                        data=f.read(),
                        file_name=res["png_path"].name,
                        mime="image/png",
                        use_container_width=True,
                        type="primary",
                    )

                st.link_button(
                    label="🚀 Open in D2 Playground (1-Click)",
                    url=res["d2_url"],
                    use_container_width=True,
                )

                with open(res["excalidraw_file"], "rb") as f:
                    st.download_button(
                        label="✏️ Download Excalidraw Whiteboard (.excalidraw)",
                        data=f.read(),
                        file_name=res["excalidraw_file"].name,
                        mime="application/json",
                        use_container_width=True,
                    )

                with st.expander("View Declarative D2 Code", expanded=False):
                    st.code(res["d2_script"], language="yaml")

    with tab_deck:
        if st.session_state.generated_carousel:
            c_res = st.session_state.generated_carousel
            slides = c_res.get("slide_images", [])

            if slides:
                cur_idx = st.session_state.current_slide_idx
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-family:ui-monospace; font-size:0.8rem; color:#888;">SLIDE {cur_idx + 1} OF {len(slides)} (1080x1350)</span>
                        <span style="font-family:ui-monospace; font-size:0.8rem; color:#38bdf8;">PDF DOCUMENT READY</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_slide_img, col_deck_actions = st.columns([1.3, 1], gap="medium")
                with col_slide_img:
                    st.image(slides[cur_idx], use_container_width=True)

                    nav_prev, nav_count, nav_next = st.columns([1, 2, 1])
                    with nav_prev:
                        if st.button("← Previous", use_container_width=True, key="btn_prev_slide"):
                            st.session_state.current_slide_idx = (cur_idx - 1) % len(slides)
                            st.rerun()
                    with nav_count:
                        st.markdown(
                            f"<div style='text-align:center; padding-top:8px; font-family:ui-monospace; color:#888; font-size:0.85rem;'>Slide {cur_idx + 1} / {len(slides)}</div>",
                            unsafe_allow_html=True,
                        )
                    with nav_next:
                        if st.button("Next →", use_container_width=True, key="btn_next_slide"):
                            st.session_state.current_slide_idx = (cur_idx + 1) % len(slides)
                            st.rerun()

                with col_deck_actions:
                    st.markdown("#### Carousel Document Deck")
                    st.markdown("Export as a native LinkedIn PDF document for maximum algorithm engagement.")

                    with open(c_res["pdf_path"], "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download Complete {len(slides)}-Slide PDF",
                            data=f.read(),
                            file_name=c_res["pdf_path"].name,
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary",
                        )

                    st.markdown("---")
                    st.markdown(
                        """
                        **LinkedIn Publishing Tip:**
                        Upload the PDF as a document. LinkedIn automatically renders document files into a native, swipeable carousel widget.
                        """
                    )

    with tab_vid:
        if st.session_state.generated_video and Path(st.session_state.generated_video).exists():
            v_path = Path(st.session_state.generated_video)
            col_v_play, col_v_actions = st.columns([1.3, 1], gap="medium")
            with col_v_play:
                st.video(str(v_path))
            with col_v_actions:
                st.markdown("#### 60fps Vector Animation")
                st.markdown("Rendered via Manim Community Edition with 60fps smooth physics.")
                with open(v_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download 60fps MP4",
                        data=f.read(),
                        file_name=v_path.name,
                        mime="video/mp4",
                        use_container_width=True,
                        type="primary",
                    )
        else:
            st.info("💡 To generate a 60fps Manim video alongside your blueprint, expand 'Customize Parameters' and select '60fps Manim 2D Animation'.")

    with tab_copy:
        if st.session_state.generated_post:
            st.markdown("#### Formatted LinkedIn Post Copy")
            st.code(st.session_state.generated_post, language="markdown")
else:
    # Quiet Minimalist Feature Summary (Zero Clutter Before Action)
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:#080808; border:1px solid #1a1a1a; border-radius:14px; padding:24px;">
            <div style="font-family:ui-monospace; font-size:0.75rem; color:#888; text-transform:uppercase; margin-bottom:12px; letter-spacing:0.05em;">
                PUBLICATION SUITE CAPABILITIES
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:16px;">
                <div style="border-left: 2px solid #38bdf8; padding-left:12px;">
                    <div style="font-weight:600; font-size:0.9rem; color:#fff;">2D Architecture Blueprint</div>
                    <div style="font-size:0.8rem; color:#737373; margin-top:4px;">1080x1080 card + D2 script + Excalidraw file</div>
                </div>
                <div style="border-left: 2px solid #818cf8; padding-left:12px;">
                    <div style="font-weight:600; font-size:0.9rem; color:#fff;">4-Slide Carousel Deck</div>
                    <div style="font-size:0.8rem; color:#737373; margin-top:4px;">1080x1350 PDF document formatted for LinkedIn</div>
                </div>
                <div style="border-left: 2px solid #34d399; padding-left:12px;">
                    <div style="font-weight:600; font-size:0.9rem; color:#fff;">60fps Vector Video</div>
                    <div style="font-size:0.8rem; color:#737373; margin-top:4px;">Manim mathematical motion simulation</div>
                </div>
                <div style="border-left: 2px solid #f59e0b; padding-left:12px;">
                    <div style="font-weight:600; font-size:0.9rem; color:#fff;">LinkedIn Post Copy</div>
                    <div style="font-size:0.8rem; color:#737373; margin-top:4px;">Staff-level mental model & discussion hook</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
