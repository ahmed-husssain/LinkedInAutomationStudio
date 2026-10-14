# LinkedIn Automation Studio — Operations & Runbook

## 1. Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Dependencies installed: `discord.py`, `pillow`, `python-dotenv`, `pytest`

### Running the Discord Studio Bot
To start the Discord Bot Studio with auto-reconnect and background polling:
```powershell
cd D:\LinkedInAutomationStudio
python main.py
```
Or directly as a module:
```powershell
python -m src.bot.client
```

---

## 2. Configuration (`.env`)
The application loads credentials from `D:\LinkedInAutomationStudio\.env`:

| Key | Description | Default |
|-----|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord Bot token from Developer Portal | Required |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn OAuth 2.0 User Token | Optional (Simulation mode used if empty) |
| `LINKEDIN_AUTHOR_URN` | LinkedIn Author URN (`urn:li:person:<ID>`) | Optional |
| `LINKEDIN_COOLDOWN_HOURS`| Cooldown between posts | `20.0` |
| `DISCORD_POLL_INTERVAL` | Poller scan frequency in seconds | `1.5` |
| `MESSAGE_CACHE_MAX_SIZE` | LRU cache capacity for message IDs | `1000` |

---

## 3. Running the Adversarial Test Suite
To execute all adversarial unit and integration tests:
```powershell
cd D:\LinkedInAutomationStudio
python -m pytest tests -v
```

To run a specific test suite:
```powershell
python -m pytest tests/test_text_splitter_adversarial.py -v
python -m pytest tests/test_safety_guard_adversarial.py -v
python -m pytest tests/test_copy_engine_adversarial.py -v
python -m pytest tests/test_poller_adversarial.py -v
python -m pytest tests/test_diagram_engine_adversarial.py -v
python -m pytest tests/test_integration_adversarial.py -v
```

---

## 4. Key Operational Features & Commands

### Discord Commands & Mobile Controls
- **`!daily` / `!topics` / `!start`:** Opens the daily interactive topic menu with dynamic re-rolling.
- **Natural Language Interaction:**
  - Type any topic keyword (e.g. `oauth`, `token bucket`, `rate limiter`, `message queue`, `idempotency`, `sql index`, `bloom filter`, `circuit breaker`, `sharding`).
  - Type `change thumbnail` or `cover` to open the 4-theme palette generator.
  - Type `simpler` or `confusing` to get an instant step-by-step beginner breakdown.
  - Type `different question` to cycle discussion questions.

### Account Safety Guardrails
- **Max 1 Post Per 20 Hours:** Strictly enforced by `LinkedInSafetyGuard`.
- **Atomic State Persistence:** State is written to `data/publish_state.json` via atomic file replacement, preventing 0-byte corruptions.
- **Safe Simulation Mode:** If no LinkedIn API token is configured, the bot safely operates in simulation mode with instant delivery.
