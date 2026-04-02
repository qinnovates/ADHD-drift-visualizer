# ADHD Drift Visualizer

## What This Is
A Python library + dashboard that visualizes cognitive drift in chat sessions. Maps how someone pivots between topics, how far they drift, and where they come back. Built for ADHD-aware conversation analysis using semantic embeddings and multi-signal scoring.

**Not a diagnostic instrument.** Visualizes context-switching patterns — nothing more.

## Build Commands
```bash
pip install -e ".[dev]"                    # Dev deps (pytest, ruff)
pip install -e ".[ui]"                     # Dashboard deps (flask)
pip install -e ".[voyage]"                 # Voyage AI embeddings
pip install -e ".[openai]"                 # OpenAI API embeddings
pip install -e ".[local]"                  # Offline MiniLM embeddings
ADHD_DRIFT_EMBEDDINGS=local pytest         # Run tests with local embeddings
ruff check src/                            # Lint
adhd-drift demo                            # Run demo session
adhd-drift serve                           # Launch dashboard at :3457
adhd-drift analyze session.md --human      # Analyze a chat log
adhd-drift history MEMORY.md               # Cross-session patterns
```

## Architecture
```
src/adhd_drift/
├── engine.py          # DriftEngine — main orchestrator
├── scorer.py          # 4-signal composite scoring (reweighted for conversation)
├── classifier.py      # 5-tier classification (Anchored → Deep Shift)
├── tracker.py         # Cumulative drift + pivot detection
├── recovery.py        # Recovery score + refocus suggestions
├── embeddings.py      # Pluggable: Voyage AI / OpenAI / local MiniLM
├── signals.py         # Specificity shift detection
├── topics.py          # Topic extraction + labeling
├── types.py           # Shared types and dataclasses
├── cli.py             # CLI entry point (adhd-drift command)
├── demo.py            # Sample ADHD-style conversation
├── history.py         # Cross-session analysis from memory files
└── parsers/
    ├── claude.py      # Claude Code JSONL parser
    ├── chatgpt.py     # ChatGPT export JSON parser
    └── markdown.py    # Generic markdown conversation parser

ui/
├── dashboard.html     # Single-file dashboard (vanilla HTML/CSS/JS + Canvas)
└── server.py          # Flask dev server
```

## Key Types
- `ChatMessage` — one message in a conversation (text, role, metadata)
- `DriftScore` — per-message score with 4 signal components + topic label
- `DriftClassification` — enum: ANCHORED / BRANCHING / TANGENT / WANDERING / DEEP_SHIFT
- `SessionReport` — full session with pivots, topic sequence, focus streaks

## Signals (two distinct measurements)
- **Semantic distance** (0.35) — global drift from *baseline* (first message)
- **Topic divergence** (0.35) — local shift from *previous message*
- **Specificity shift** (0.15) — vagueness detection
- **Velocity** (0.15) — acceleration of drift

## Embedding Provider
Auto-detected from env vars:
1. `VOYAGE_API_KEY` set → Voyage AI embeddings
2. `OPENAI_API_KEY` set → OpenAI text-embedding-3-small
3. Neither → local MiniLM (requires `sentence-transformers`)
Override: `ADHD_DRIFT_EMBEDDINGS=voyage|openai|local`

## Rules
- Pure math in src/. No IO, no network calls in scoring engine
- UI is separate from engine — engine returns data, UI renders it
- All thresholds configurable, never hardcoded
- Embeddings are lazy-loaded, provider auto-detected
- Non-judgmental framing: pivots are data, not deficits
- No red in the color scheme — WANDERING uses yellow (#FFD60A)
