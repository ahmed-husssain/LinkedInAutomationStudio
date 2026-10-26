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

```
User Topic (Streamlit Web Studio / Discord Autopilot)
       │
       ▼
[ Content Strategist Agent ] ──► Brainstorms technical hook, failure modes & slide blueprint
       │
       ▼
[ Adversarial Critic Gate ] ◄── Python ast.parse() validation: rejects syntax errors & hallucinations
       │ (Score < 80? Auto-repair loop)
       ▼
[ High-Performance Compilers ]
   ├── 📑 Playwright Vector Engine (1080x1350 4:5 document PDF carousel)
   ├── 🎬 Manim CE Cairo Pipeline (1080p 60fps mathematical animation MP4)
   └── 📊 Diagram Engine (1080x1080 multi-theme vector technical schematics)
       │
       ▼
[ Deliverable Gateways ] ──► Streamlit Web Studio (1-Click Download) + Discord Delivery Gateway
```

---

## 🛡️ Security & Zero Secrets

- All API keys and secrets reside strictly in `.env` (excluded by `.gitignore`).
- CI/CD secret scanning verifies that `.env` files and hardcoded credentials can never be committed.
- In-memory message deduplication utilizes bounded LRU trackers (`BoundedMessageTracker`) to prevent memory leaks in 24/7 autonomous loops.
- All state modifications use atomic writes (`tempfile` + `os.replace`) to eliminate file corruption.

---

## ⚡ Quick Start

For a detailed walkthrough, read the **[Complete Setup Guide](docs/setup_guide.md)**.

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/ahmed-husssain/LinkedInAutomationStudio.git
cd LinkedInAutomationStudio

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials

```bash
cp .env.example .env
```
Fill in your credentials in `.env`:
* `DISCORD_BOT_TOKEN`: From the [Discord Developer Portal](https://discord.com/developers/applications) (enable **Message Content Intent**).
* `GEMINI_API_KEY`: From [Google AI Studio](https://aistudio.google.com/).

### 3. Launch Studio

#### Option A: Interactive Web Studio (Recommended)
```bash
streamlit run app.py
```
Open `http://localhost:8501` to preview 1080×1350 carousels, tweak parameters, and export vector PDFs and 60fps Manim videos with $0 cloud cost.

#### Option B: Autopilot Discord Bot
```bash
python main.py
```

### 4. Run Test Suite

```bash
python -m pytest -v
```

---

## 🤝 Contributing & Good First Issues

We are building the open-source standard for engineering communication. If you want to contribute, check out these curated issues:

* **[Issue #12: New Manim Animation Scenes](https://github.com/ahmed-husssain/LinkedInAutomationStudio/issues/12)** (`Python` · `Manim CE`)  
  Add animated scenes for distributed systems: Raft consensus elections, two-phase commit, and token bucket rate limiters.
* **[Issue #15: Web Studio UI & Slide Previewer](https://github.com/ahmed-husssain/LinkedInAutomationStudio/issues/15)** (`Streamlit` · `Frontend`)  
  Build live parameter tweaking, hot-reload slide preview canvas, and dynamic theme palette switcher.
* **[Issue #21: Critic Evaluation & Pytest Suites](https://github.com/ahmed-husssain/LinkedInAutomationStudio/issues/21)** (`pytest` · `AST` · `Evals`)  
  Extend the Adversarial Critic with automated Python code linting, race-condition checks, and benchmarks.

👉 **Explore all issues:** [https://github.com/ahmed-husssain/LinkedInAutomationStudio/issues](https://github.com/ahmed-husssain/LinkedInAutomationStudio/issues)

---

## 🤖 CI/CD & Security Audits

- **GitHub Actions (`.github/workflows/ci.yml`):**
  - Static security audit with `bandit` on `src/`, `app.py`, and `main.py` (0 High issues required).
  - Secret leak prevention guard.
  - Python syntax and linting validation with `flake8`.
  - Automated 100+ test suite on all pushes and PRs.
- **CodeRabbit (`.coderabbit.yaml`):**
  - Automated PR reviews enforcing collision-free visual design system rules, zero secrets, and senior minimalism.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
