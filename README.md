# 🚀 LinkedIn Automation Studio

An autonomous, multi-agent content generation and publishing studio engineered to create viral, top 1% system architecture and backend engineering content for LinkedIn. Delivers ready-to-publish packages directly to Discord:
1. **Interactive 6-Slide PDF Carousels** (1080x1350 vertical document decks for 3x reach).
2. **2D Animated Motion Graphics** (1080x1080 square 60fps Manim CE videos).
3. **High-Contrast Architecture Diagrams** (1080x1080 Pillow technical covers).
4. **Authentic Developer Post Copy** (Crafted with hook, mental model, and senior discussion prompts).

---

## 📚 Master Documentation Suite

This repository features a comprehensive **Agent Context Harness** and documentation system to guide both human engineers and autonomous AI agents:

| Document | Purpose & Scope |
| :--- | :--- |
| **[📘 Complete Setup Guide](docs/setup_guide.md)** | **Start here!** Step-by-step beginner guide for Discord Bot, Gemini API, FFmpeg, and running the studio. |
| **[🏛️ Technical Architecture](docs/architecture.md)** | End-to-end system topology, bounded LRU poller, rendering engines, and data flow. |
| **[📋 Product Requirements (PRD)](docs/prd.md)** | Feature requirements, user personas, acceptance criteria, and anti-goals. |
| **[🗺️ Strategic Roadmap](docs/roadmap.md)** | 4-Phase evolution from MVP to autonomous self-healing media factory. |
| **[🤖 Multi-Agent Roster](docs/agents.md)** | Strategist, Critic, and Orchestrator contracts, Pydantic v2 schemas, and auto-refinement loop. |
| **[🎨 Universal Design System](docs/design_system.md)** | 1080x1350 vertical bounds, Manim $Y \ge -1.8$ HUD safe zone, color tokens, and Zero Font Tofu rules. |
| **[📜 Engineering Rules](docs/rules.md)** | Non-negotiable laws: Zero Secrets, Atomic Persistence, Bounded LRU, and Ponytail YAGNI. |
| **[🛠️ Skills Playbook](docs/skills.md)** | Operational guide for `/ponytail`, `/ponytail-review`, `/ponytail-audit`, and Thermonuclear review. |
| **[🧠 Living Memory Bank](docs/memory.md)** | Historical incidents (Manim scrubber collision, poller memory leak, Bandit fixes) and permanent resolutions. |
| **[🤝 Contributing Guide](CONTRIBUTING.md)** | Branching workflow, pull request standards, and CodeRabbit review conventions. |

---

## 🏗️ Multi-Agent Architecture

The studio operates as a zero-bloat, native Python multi-agent system:

```
User Prompt (Discord / Autopilot)
       │
       ▼
[ Content Strategist Agent ] ──► Brainstorms authentic hook, mental model & slide breakdown
       │
       ▼
[ Staff Engineer Critic Agent ] ◄── Adversarial review: kills buzzwords, fact-checks mechanics
       │ (Score < 80? Auto-refinement loop)
       ▼
[ Multi-Modal Renderers ]
   ├── 📑 PDF Carousel Architect (1080x1350 Pillow document compiler)
   ├── 🎬 Base Studio Scene (1080x1080 Manim CE 2D motion graphics)
   └── 📊 Diagram Engine (1080x1080 multi-theme vector technical covers)
       │
       ▼
[ Discord Delivery Gateway ] ──► 1-tap interactive post delivery & camera-roll downloads
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

### 3. Run Test Suite

```bash
python -m pytest -v
```

### 4. Launch Studio Discord Bot

```bash
python main.py
```

---

## 🤖 CI/CD & CodeRabbit AI Review

- **GitHub Actions (`.github/workflows/ci.yml`):**
  - Static security audit with `bandit` (0 High issues required).
  - Secret leak prevention guard.
  - Python syntax validation with `flake8`.
  - Automated 39-test adversarial test suite on all pushes and PRs.
- **CodeRabbit (`.coderabbit.yaml`):**
  - Automated PR reviews enforcing collision-free visual design system rules, zero secrets, and senior minimalism.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
