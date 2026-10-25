"""
LinkedIn Automation Studio — 1-Screen Zero-Install Web Dashboard.
Powered by Streamlit, Playwright, and Manim Community Edition.
Generates 1080x1350 PDF Carousels and 60fps Manim Videos with $0 cloud cost.
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List

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
from src.engines.video_engine import (
    render_parameterized_animation_async,
    adjust_video_pacing_async,
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
# Streamlit App Configuration & Modern Styling
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
    /* Dark Slate Glassmorphic Theme */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0f172a 0%, #030712 100%);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .header-box {
        text-align: center;
        padding: 24px 16px 12px 16px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .header-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
    }
    .card-container {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-bottom: 8px;
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
if "generated_carousel" not in st.session_state:
    st.session_state.generated_carousel = None
if "generated_video" not in st.session_state:
    st.session_state.generated_video = None
if "generated_post" not in st.session_state:
    st.session_state.generated_post = None


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-box">
        <span class="badge-pill">Production Media Factory</span>
        <div class="header-title">LinkedIn Automation Studio</div>
        <div class="header-sub">Generate publication-grade 1080x1350 PDF carousels & 60fps Manim vector videos in seconds.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Control Stage: Two-Column Control Panel
# -----------------------------------------------------------------------------
col_control, col_preview = st.columns([1, 1.2], gap="large")

with col_control:
    st.markdown("### 1. Topic & Strategic Angle")
    
    topic_mode = st.radio(
        "Topic Source",
        ["Curated System Architecture Presets", "Custom Engineering Topic"],
        horizontal=True,
        label_visibility="collapsed",
    )
    
    if topic_mode == "Curated System Architecture Presets":
        selected_key = st.selectbox(
            "Select Architecture Topic",
            options=list(CURATED_TOPICS.keys()),
            format_func=lambda k: CURATED_TOPICS[k]["label"],
        )
        topic_id = selected_key
        topic_title = CURATED_TOPICS[selected_key]["default_title"]
        video_id = CURATED_TOPICS[selected_key]["video_id"]
    else:
        topic_title = st.text_input(
            "Enter Topic Title",
            value="Consistent Hashing Ring Topology",
            placeholder="e.g. Distributed Consensus in Raft",
        )
        topic_id = (
            topic_title.lower()
            .replace(" ", "_")
            .replace(":", "")
            .replace("-", "_")
        )
        video_id = "token_bucket"

    st.markdown("---")
    st.markdown("### 2. Format & Aesthetics")

    format_choice = st.radio(
        "Choose Primary Format",
        [
            "📑 1080x1350 PDF Carousel (Document Deck)",
            "🎬 60fps Manim 2D Animation (MP4 Video)",
        ],
    )

    if "Carousel" in format_choice:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            slide_count = st.select_slider(
                "Deck Length",
                options=[3, 4, 5],
                value=4,
                help="3 = Fast takeaway, 4 = Incident breakdown, 5 = Deep architectural runbook",
            )
        with col_c2:
            theme_choice = st.selectbox(
                "Visual Palette",
                options=list(CAROUSEL_THEMES.keys()),
                format_func=lambda t: f"{t.capitalize()} Accent",
            )
    else:
        pacing_choice = st.select_slider(
            "Video Reading Pacing",
            options=["Standard Pacing", "+4s Extended Walkthrough", "+6s Deep Architecture"],
            value="+4s Extended Walkthrough",
            help="Adds calm reading time between packet hops and node transitions.",
        )

    st.markdown("---")
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
    with st.spinner("Compiling technical specimens & rendering visual assets..."):
        output_dir = ROOT_DIR / "data" / "published"
        output_dir.mkdir(parents=True, exist_ok=True)

        if "Carousel" in format_choice:
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
            st.session_state.generated_video = None
        else:
            # Video generation
            pts_factor = 1.0
            if "+4s" in pacing_choice:
                pts_factor = 1.35
            elif "+6s" in pacing_choice:
                pts_factor = 1.60

            rendered_video_path = run_async(
                render_parameterized_animation_async(
                    animation_id=video_id,
                    force_render=False,
                )
            )

            final_video_path = rendered_video_path
            if pts_factor > 1.0:
                paced_name = f"{video_id}_paced_{int(pts_factor * 100)}.mp4"
                paced_path = output_dir / paced_name
                final_video_path = run_async(
                    adjust_video_pacing_async(
                        input_video=rendered_video_path,
                        output_video=paced_path,
                        pts_factor=pts_factor,
                    )
                )

            st.session_state.generated_video = final_video_path
            st.session_state.generated_carousel = None

        # Build authentic developer post copy
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
        st.success("Visual assets compiled successfully!")


# -----------------------------------------------------------------------------
# Preview & Download Stage
# -----------------------------------------------------------------------------
with col_preview:
    st.markdown("### 3. Live Preview Stage")

    # CAROUSEL PREVIEW (Slide-by-Slide PNG Gallery)
    if st.session_state.generated_carousel:
        carousel = st.session_state.generated_carousel
        slides = carousel.get("slides", [])
        pdf_path = carousel.get("pdf")
        total_slides = len(slides)

        if slides:
            curr_idx = st.session_state.current_slide_idx
            curr_idx = max(0, min(total_slides - 1, curr_idx))

            # Slide navigation controls
            nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
            with nav_c1:
                if st.button("◀ Prev Slide", disabled=(curr_idx == 0), use_container_width=True):
                    st.session_state.current_slide_idx -= 1
                    st.rerun()
            with nav_c2:
                st.markdown(
                    f"<div style='text-align: center; font-weight: 700; padding-top: 6px;'>Slide {curr_idx + 1} of {total_slides}</div>",
                    unsafe_allow_html=True,
                )
            with nav_c3:
                if st.button("Next Slide ▶", disabled=(curr_idx >= total_slides - 1), use_container_width=True):
                    st.session_state.current_slide_idx += 1
                    st.rerun()

            # Render active slide PNG
            active_slide_path = slides[curr_idx]
            if Path(active_slide_path).exists():
                img = Image.open(active_slide_path)
                st.image(img, use_container_width=True)

            # 1-Click PDF Download
            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label=f"⬇️ Download 1080x1350 Carousel Deck ({total_slides} Slides PDF)",
                    data=pdf_bytes,
                    file_name=Path(pdf_path).name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )

    # VIDEO PREVIEW (Manim MP4 Player)
    elif st.session_state.generated_video:
        video_path = st.session_state.generated_video
        if Path(video_path).exists():
            st.video(str(video_path))
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            st.download_button(
                label="⬇️ Download 60fps Vector Video (MP4)",
                data=video_bytes,
                file_name=Path(video_path).name,
                mime="video/mp4",
                type="primary",
                use_container_width=True,
            )
    else:
        st.info("Select your topic and format on the left, then click **[Generate LinkedIn Content Package]** to preview.")

    # POST COPY CREATOR KIT
    if st.session_state.generated_post:
        st.markdown("---")
        st.markdown("### 4. LinkedIn Post Copy (Creator Kit)")
        st.text_area(
            "Ready-to-publish developer post caption:",
            value=st.session_state.generated_post,
            height=260,
        )
