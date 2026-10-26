---
title: LinkedIn Automation Studio
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: false
---

# 🚀 LinkedIn Automation Studio
### The Open-Source Visual Compiler for System Design & Engineering Content

[![GitHub Repository](https://img.shields.io/badge/GitHub-ahmed--husssain%2FLinkedInAutomationStudio-blue?logo=github)](https://github.com/ahmed-husssain/LinkedInAutomationStudio)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-cyan.svg)](https://www.python.org/)
[![Cloud Cost](https://img.shields.io/badge/Cloud%20Cost-%240%20(Local%20%2F%20HF)-brightgreen)](#)

An open-source visual compiler and multi-agent studio engineered to eliminate AI hallucinations in technical content. Instead of wrestling with Figma layers or dragging boxes in Canva, `LinkedInAutomationStudio` verifies architecture logic via native Python `ast.parse()` and compiles 3 publication-ready visual formats automatically for **$0 in cloud fees**:

1. **📑 1080×1350 Vector PDF Carousels** — Native 4:5 vertical document decks with crisp vector typography and real architecture specimens via headless Playwright Chromium.
2. **🎬 60fps Mathematical Explainer Videos** — 1080p 60fps animations engineered with Grant Sanderson's Manim CE (3Blue1Brown) motion engine.
3. **📊 2D System Architecture Schematics** — High-contrast vector SVGs and PNGs ready for RFCs, technical blogs, and documentation.
4. **💡 Senior Developer Post Copy** — Formatted with technical hooks, mental models, and architectural discussion prompts.

> 🌐 **GitHub Repository:** [https://github.com/ahmed-husssain/LinkedInAutomationStudio](https://github.com/ahmed-husssain/LinkedInAutomationStudio)  
> 💻 **Live Studio:** Runs locally via Streamlit or deployable to free Hugging Face Spaces with zero SaaS subscriptions.

---

## 📚 Master Documentation Suite

This repository features a comprehensive **Agent Context Harness** and documentation system to guide both human engineers and autonomous AI agents:

| Document | Purpose & Scope |
| :--- | :--- |
| **[📋 Master Specification (SPEC.md)](SPEC.md)** | **Core Contract!** Non-technical zero-cost web pivot, daily & weekly targets, tech stack evaluation, and quality gates. |
| **[📘 Complete Setup Guide](docs/setup_guide.md)** | Step-by-step guide for local development, Discord Bot, Gemini API, and FFmpeg. |
| **[🏛️ Technical Architecture](docs/architecture.md)** | End-to-end system topology, bounded LRU poller, rendering engines, and data flow. |
| **[📋 Product Requirements (PRD)](docs/prd.md)** | Feature requirements, user personas, acceptance criteria, and anti-goals. |
| **[🗺️ Strategic Roadmap](docs/roadmap.md)** | 4-Phase evolution from MVP to autonomous self-healing media factory. |
| **[🤖 Multi-Agent Roster](docs/agents.md)** | Strategist, Critic, and Orchestrator contracts, Pydantic v2 schemas, and auto-refinement loop. |
| **[🎨 Universal Design System](docs/design_system.md)** | 1080x1350 vertical bounds, Manim $Y \ge -1.8$ HUD safe zone, color tokens, and Zero Font Tofu rules. |
| **[📜 Engineering Rules](docs/rules.md)** | Non-negotiable laws: Zero Secrets, Atomic Persistence, Bounded LRU, and Ponytail YAGNI. |
| **[🛠️ Skills Playbook](docs/skills.md)** | Operational guide for `/ponytail`, `/ponytail-review`, `/ponytail-audit`, and Thermonuclear review. |
| **[🧠 Living Memory Bank](docs/memory.md)** | Historical incidents (Manim scrubber collision, poller memory leak, Bandit fixes) and permanent resolutions. |
| **[⚠️ Consequences & Risk Register](docs/consequences_matrix.md)** | Mandatory pre-implementation impact analysis, failure mode breakdown, and mitigations. |
| **[🤝 Contributing Guide](CONTRIBUTING.md)** | Branching workflow, pull request standards, and CodeRabbit review conventions. |

---

## 🏗️ Multi-Agent Architecture

The studio operates as a deterministic, native Python multi-agent pipeline:
