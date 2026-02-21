# Career Quest Map

An AI-guided pathway discovery game for Singapore youth. Career Quest Map turns career exploration into a short, story-driven game that helps users discover strengths, narrow interests, and leave with practical next steps.

---

## Demo Preview

- **Part 1 — The House:** quick self-discovery (5 questions)
- **Part 2 — The Wise Man:** deeper narrowing (12 questions; Poly has an extra question)
- **Analysis:** strengths, work-style tags, short feedback, 3 ranked options
- **Gates:** 3 ranked gates (1/2/3) with explanation and Yes/No decision
- **Dragon quests:** actionable 1-week micro quest and 1-month mini project
- **Quest Booth:** review analysis and quests

---

## Why This Project

Many students must decide early with limited context. Grades show performance, not fit. This project helps users:

- Understand strengths and work style
- Explore realistic pathways matched to fit and growth
- Leave with concrete, low-cost actions (micro-quests and mini projects)

---

## Key Features (Aligned to Code)

### Adaptive Question Flow

Powered by a content engine and optional Azure OpenAI LLM:

- LLM wrapper: `llm_client.py` returns parsed JSON only.
- If no LLM is configured, deterministic fallback content is used (`fallback_content.py`).
- Strict schema validation for all LLM outputs: validators in `validation.py` enforce counts and types.
- Content engine (`content_engine.py`) builds prompts with hard rules and schema hints.

### Part 1 — House (exactly 5 questions)

- Distribution enforced: 2 MCQ, 1 slider (0–10), 1 rating (1–5), 1 text.
- Topics adapt to education status: Secondary/JC vs Poly.

### Part 2 — Wise Man (exactly 12 questions + Poly extra)

- Engine infers exactly 3 fields and generates 12 narrowing questions.
- Distribution enforced: 4 MCQ, 3 slider, 3 rating, 2 text.
- Poly-only MCQ: choice between Work and Go to uni.

### Analysis (Schema C)

Outputs:

- 3 strength tags
- 2–4 work-style tags
- 2–5 feedback lines
- Exactly 3 ranked suggested options
  - For Poly who choose Work: suggested options are careers
  - Otherwise: courses

### Gates (Schema D)

- Player enters a gate scene with 3 ranked options (from analysis).
- Each gate includes: what to study, employment outlook (safe language), impact on people.
- If a gate is a work-path, also includes work-style line and salary outlook (safe ranges).
- **Yes** unlocks Dragon quests; **No** returns to the gates list.

### Dragon Quests & Resources

- **Micro quest:** 1-week, short sessions, tangible deliverable.
- **Mini project:** 1-month, Plan/Build/Review phases, shareable output.
- **Resources:** free and accessible (docs, tutorial, example project, community).

### Quest Log & Orientation

- Guided progression: House → Wise Man → Gates → Gate Scene → Dragon Quest → Quest Booth.
- Game saves intermediate state to an Output folder by default (see `config.py`).

### Game Feel & UI

- Top-down scenes, walking animation, collision rects (`main.py`).
- Dialog screens, multiple choice/slider/rating/text input UI in `game_quizes.py` and `print_questions.py`.
- Asset fallbacks: if an image/audio is missing, the game uses simpler shapes or fallback content.

---

## Project Structure (High Level)

**Root scripts:**

- `main.py` — game loop & scenes (entry point)
- `game_classes.py`, `game_quizes.py`, `print_questions.py` — UI and quiz handling

**Config / state:**

- `config.py` — app configuration & environment variable loading
- `state.py` — typed user profile and game state dataclasses

**Core content & safety:**

- `content_engine.py` — prompt templates, schema hints, and content-generation flow
- `validation.py` — strict validators for every LLM output schema
- `fallback_content.py` — deterministic fallback content when LLM unavailable

**Integrations:**

- `llm_client.py` — Azure OpenAI wrapper that returns parsed JSON

**Data and assets:**

- `options_catalog.json` — curated dataset of courses, careers, fields, and resources
- `images/`, `audio/` — UI and audio assets (game uses fallback shapes if missing)

---

## Tech Stack

- Python 3.12+ (`pyproject.toml` lists `requires-python = ">=3.12"`)
- Pygame for UI
- pygame-widgets (UI helpers)
- python-dotenv (env loading)
- Optional LLM: langchain + Azure OpenAI integration (`langchain-openai`, `langchain-core`, etc.)

See `pyproject.toml` for dependency groups and versions.

---

## Environment Variables (Azure OpenAI)

To enable LLM generation, set these environment variables (or use a `.env` file; `config.py` calls `load_dotenv()`):

| Variable | Description |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint URL |
| `AZURE_OPENAI_API_KEY` | API key |
| `AZURE_OPENAI_API_VERSION` | (optional) default set in `AppConfig` |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name |

> If these are not configured, the game runs using curated fallback content and remains fully playable — no LLM calls are made.

---

## Installation & Running Locally

**1. Create a venv and install dependencies (recommended):**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

**2. Set environment variables (optional, for LLM). Example `.env`:**

```
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

**3. Run the game from the project root:**

```bash
python main.py
```

> The game logs helpful messages if audio/images are not found and uses fallback shapes. The default save directory is `Output` (configured in `config.py`).

---

## Controls

| Action | Keys |
|---|---|
| Movement | Arrow keys or WASD |
| Interact / Advance dialog | Enter |
| Back / Exit screen | Esc |
| Gate decision | Y or N |
| MCQ | Up/Down to change, Enter to confirm, 1–9 quick pick |
| Slider / Rating | Left/Right to change, Enter to confirm |
| Text input | Type then Enter |
| Quit quiz early | Q |

---

## Assets

Place assets under the `images/` and `audio/` folders. If an asset is missing, the game will print a warning and fall back to simple shapes/audio silence.

---

## Data & Curated Catalog

`options_catalog.json` contains:

- Field vocabulary
- Curated poly courses and university courses
- Common resources and subject lists

The content engine references this curated dataset as the authoritative fallback and to keep suggestions realistic.

---

## Reliability & Safety

- All LLM outputs are constrained by strict schema hints and validators in `validation.py`.
- The `ContentEngine` composes explicit hard rules to ensure deterministic structure.
- `fallback_content.py` provides deterministic content when the LLM is unavailable or fails validation.
- Tone and language are constrained to avoid personal data or precise real-world statistics; salary or outlook phrasing uses safe ranges or qualitative wording.

---

## Development Notes & Extension Points

- Cache LLM responses per session to reduce latency (future improvement).
- Expand `options_catalog.json` to include more curated pathways and resources.
- Add export/share options (PDF export of analysis and quests).
- Polish animation and collision blocks for smoother low-end performance.

---

## Credits

Built for **CCDS Tech for Good Hackathon 2026**

**Team:** Zin Hmue Paing, Thiha Htoo Zin, Bhone Min Thant

**License:** MIT (see `pyproject.toml`)
