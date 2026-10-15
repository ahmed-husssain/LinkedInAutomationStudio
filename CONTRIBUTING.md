# 🤝 Contributing to LinkedIn Automation Studio

Thank you for your interest in contributing to **LinkedIn Automation Studio**! We are building an autonomous, multi-agent content generation studio that transforms complex distributed systems architecture into viral, high-retention LinkedIn content for senior engineers.

To keep this codebase world-class, maintainable, and robust, all contributors (human developers and AI assistants) must follow these guidelines.

---

## 🏛️ Core Engineering Philosophy

1. **Ponytail Senior Minimalism (YAGNI):**
   * The best code is the code never written.
   * Reach for Python's standard library (`pathlib`, `secrets`, `dataclasses`, `asyncio`, `urllib`) before adding third-party dependencies.
   * We strictly reject bloated frameworks (CrewAI, LangChain, APScheduler) when a clean, native 10-line loop solves the problem.
   * Prefer boring, readable code over clever abstractions.

2. **Authentic Developer Tone:**
   * Content and copy must sound like a real engineer sharing hard-won production lessons.
   * Strictly avoid corporate AI clichés (*"delve"*, *"game-changer"*, *"testament"*, *"tapestry"*, *"in today's fast-paced world"*).

3. **Universal Collision-Free Design System:**
   * **Videos (Manim):** Dynamic text banners must respect $Y \ge -1.8$ to avoid collisions with Discord/LinkedIn video player scrubbers.
   * **PDF Carousels (Pillow):** All text must wrap at word boundaries using bounding-box measurements (`wrap_text_cleanly`). Never slice strings mid-word with raw indices (`[:N]`).
   * **Font Safety:** Never render raw Unicode emojis or unsupported glyphs directly in PIL (prevents `[]` tofu boxes). Use programmatic vector primitives.

---

## 🚀 Setting Up Local Development

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/ahmed-husssain/LinkedInAutomationStudio.git
cd LinkedInAutomationStudio

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```
Fill in your credentials in `.env`. **NEVER commit your `.env` file to Git.**

### 3. Run the Test Suite

Before making any changes, verify that all 39 tests pass:
```bash
python -m pytest -v
```

---

## 🛠️ Contribution Workflow

1. **Create a Feature Branch:**
   ```bash
   git checkout -b feat/your-feature-name
   # or for bug fixes:
   git checkout -b fix/issue-description
   ```

2. **Write Clean, Minimal Code:**
   * Adhere to [docs/rules.md](docs/rules.md) and [docs/skills.md](docs/skills.md).
   * Keep diffs focused and minimal. Avoid touching unrelated files.

3. **Add or Update Tests:**
   * Every new feature or bug fix must include an adversarial unit or integration test in `tests/`.

4. **Verify Quality & Security Checks:**
   ```bash
   # 1. Run all tests
   python -m pytest -v

   # 2. Run static security audit
   bandit -r src/ -ll --exclude src/animations/

   # 3. Verify Python syntax
   flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source
   ```

5. **Commit & Open a Pull Request:**
   * Write concise, conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`).
   * Open a PR against `main`.

---

## 🤖 CodeRabbit Automated Reviews

Every Pull Request is automatically reviewed by **CodeRabbit AI**:
* CodeRabbit checks for zero secrets, design system safe zones ($Y \ge -1.8$), Ponytail minimalism, and async stability.
* Please address any high-signal feedback provided by CodeRabbit before requesting human review.

---

## 📜 Documentation Reference

For deep context on architecture, agents, and design rules, consult our documentation suite:
* [Architecture Blueprint](docs/architecture.md)
* [Multi-Agent Specification](docs/agents.md)
* [Design System & Visual Canvas Rules](docs/design_system.md)
* [Engineering Rules & Standards](docs/rules.md)
* [Skills & Review Playbook](docs/skills.md)
* [Living Project Memory](docs/memory.md)
