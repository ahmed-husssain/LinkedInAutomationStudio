# 📜 Non-Negotiable Engineering Rules & System Invariants

## 1. Purpose & Authority

This document defines the **binding, inviolable engineering laws** governing **LinkedIn Automation Studio**. Every contributor, human engineer, and autonomous AI agent modifying this codebase MUST comply with these rules. 

Violations will be automatically blocked by GitHub Actions CI, CodeRabbit AI reviews, and pre-commit checks.

---

## 2. The Nine Non-Negotiable Laws

### Rule 1: Zero Secrets in Git Commits (The Steel Vault)
* **The Law:** Never commit API keys, bot tokens, passwords, webhooks, or private tokens into git history under ANY circumstance.
* **Enforcement:**
  - All credentials must be read strictly from environment variables via `os.getenv()`.
  - `.env` must remain in `.gitignore`.
  - Commits containing potential keys will be rejected by CI security scans (Bandit / secret detection).
  - Use `.env.example` with dummy values (`DISCORD_BOT_TOKEN="your_token_here"`) for documentation.

### Rule 2: Universal Collision-Free Design (Safe Zone Invariant)
* **The Law:** Visual elements must never collide with system UI overlays, scrubbers, or mobile status bars.
* **Enforcement:**
  - **Manim Motion Graphics:** Region $Y \in [-3.6, -1.8]$ is strictly reserved for the progress bar and timestamp HUD. ALL visual components (servers, queues, labels) must be placed at **$Y \ge -1.8$**.
  - **PDF Carousels:** The top 120px ($Y \le 120$) and bottom 120px ($Y \ge 1230$) of the 1080x1350 canvas are reserved for system badges and pagination. No body copy or cards may bleed into these zones.

### Rule 3: Ponytail Senior Minimalism (YAGNI)
* **The Law:** Reach for the Python standard library before external packages. Write 1 line of clean code before 50 lines of speculative abstraction.
* **Enforcement:**
  - Do not introduce new heavy dependencies (e.g. LangChain, Celery, Redis) when standard library features (`collections.OrderedDict`, `subprocess`, `dataclasses`, `json`) achieve the goal.
  - No speculative generic factories or unused wrappers. Build strictly what is needed for the current requirement.
  - Review all pull requests against Ponytail principles (`/ponytail-review`).

### Rule 4: Test Integrity & Adversarial Verification
* **The Law:** Never comment out, weaken, or delete a test simply to make CI pass.
* **Enforcement:**
  - All existing adversarial tests in [`tests/`](file:///D:/LinkedInAutomationStudio/tests/) must pass (`pytest tests/`).
  - New features must include adversarial unit tests covering edge cases: empty strings, zero division, non-ASCII characters, extreme lengths, and API failure modes.
  - All tests must complete synchronously in under 15 seconds.

### Rule 5: Bounded LRU & Resource Safety
* **The Law:** Unbounded in-memory collections (`set()`, `dict()`, `list()`) that grow indefinitely during 24/7 daemon runs are strictly forbidden.
* **Enforcement:**
  - Any cache, message tracker, or queue must use an explicit size bound (e.g. `BoundedMessageTracker` capped at 1,000 items with LRU eviction).
  - Memory consumption of the background bot process must remain flat ($\le 150 \text{ MB}$).

### Rule 6: Atomic State Persistence
* **The Law:** Application state files (such as `data/publish_state.json`) must never be written directly with `open('file', 'w')`.
* **Enforcement:**
  - All state writes must use an atomic pattern: write first to a temporary file on the same filesystem (`tempfile.NamedTemporaryFile(delete=False)`), flush to disk (`f.flush()`, `os.fsync()`), and execute an atomic rename (`os.replace()`).
  - This eliminates zero-byte file corruption if the system crashes mid-write.

### Rule 7: Zero Font Tofu (Deterministic Vector Drawing)
* **The Law:** Never insert colored Unicode emoji characters (`👉`, `⚡`, `💬`, `❌`, `✅`) into Pillow canvas text strings.
* **Enforcement:**
  - Standard fonts on headless environments lack emoji glyphs, resulting in ugly missing-glyph tofu boxes (`[]`).
  - Draw bullet indicators and icons using programmatic geometric vectors (`draw.line`, `draw.polygon`, `draw.ellipse`) or clean ASCII arrows (`->`, `>>`).

### Rule 8: Zero-Truncation Mobile Dropdowns
* **The Law:** User-facing options in Discord mobile menus must never be truncated awkwardly with raw slices.
* **Enforcement:**
  - Discord select option labels are capped at 100 characters (effectively 38 chars on small mobile screens before UI truncation).
  - Any text splitting must use `text_splitter.split_for_select_option()` which splits strictly across **natural word boundaries** between label and description.

### Rule 9: Safe Degradation & Offline Fallbacks
* **The Law:** If an external service (Google Gemini API, LinkedIn REST API) is unavailable or rate-limited, the application must degrade gracefully without crashing.
* **Enforcement:**
  - The multi-agent orchestrator must catch API exceptions and fall back to high-quality curated offline topics in [`src/config/topics.py`](file:///D:/LinkedInAutomationStudio/src/config/topics.py).
  - The LinkedIn client must fall back to Safe Simulation Mode if credentials are absent.

### Rule 10: Mandatory Pre-Implementation Consequence & Risk Disclosure (The Transparency Invariant)
* **The Law:** Never implement any new feature, architectural modification, or refactoring without proactively presenting the downstream consequences, risks, and mitigations in plain, beginner-friendly terms *first*.
* **Enforcement:**
  - Before executing non-trivial code changes, the AI agent or contributor MUST present an upfront impact breakdown covering:
    1. **What changes:** Exact files and behaviors affected.
    2. **Downstream consequences & risks:** Potential negative side-effects (e.g. disk space accumulation, AI parsing edge cases, caching issues, performance impact) explained simply.
    3. **Concrete mitigations:** The exact safeguards implemented to neutralize those risks.
    4. **Safety net:** How the system falls back if anything unexpected occurs.
  - All major changes and their risk assessments must be logged in [`docs/consequences_matrix.md`](file:///D:/LinkedInAutomationStudio/docs/consequences_matrix.md).

