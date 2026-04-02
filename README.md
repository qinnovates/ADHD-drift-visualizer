<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/header-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/header-light.svg">
    <img alt="ADHD Drift Visualizer" src="docs/assets/header-dark.svg" width="700">
  </picture>
</p>

<p align="center">
  <a href="LICENSE.md"><img src="https://img.shields.io/github/license/qinnovates/ADHD-drift-visualizer?style=flat-square&color=22D3EE" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10+-BF5AF2?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/status-alpha-FF9F0A?style=flat-square" alt="Status">
</p>

---

## The Problem

ADHD conversations don't follow a straight line. You start on auth tokens, pivot to a CSS bug, remember a meeting, circle back, then go deep on architecture. **That's not a bug — it's how your brain works.**

But it's invisible. You finish a session and wonder: *how many topics did I actually touch? Where did I drift? Did I ever come back?*

**ADHD Drift Visualizer answers those questions.** Feed it a chat session and it maps every topic pivot, scores how far you drifted, and shows you the shape of your conversation.

## How It Works

Feed it a conversation. It scores every message for drift from your starting topic and builds a relational graph of how your thinking moved.

```mermaid
graph LR
    A["Message 1<br><b>Auth tokens</b>"] -->|pivot| B["Message 3<br><b>CSS bug</b>"]
    A -->|stay| A2["Message 2<br><b>Auth refresh</b>"]
    B -->|pivot| C["Message 5<br><b>Meeting prep</b>"]
    C -->|return| D["Message 7<br><b>Auth debate</b>"]
    D -->|pivot| E["Message 10<br><b>DB migration</b>"]
    D -->|stay| D2["Message 8<br><b>Auth arch</b>"]
    E -->|return| F["Message 12<br><b>Auth fix</b>"]

    style A fill:#39FF14,stroke:#248A3D,color:#000
    style A2 fill:#39FF14,stroke:#248A3D,color:#000
    style B fill:#FF9F0A,stroke:#C77800,color:#000
    style C fill:#BF5AF2,stroke:#8944AB,color:#fff
    style D fill:#FF9F0A,stroke:#C77800,color:#000
    style D2 fill:#00E5FF,stroke:#0071A4,color:#000
    style E fill:#FFD60A,stroke:#B8A000,color:#000
    style F fill:#39FF14,stroke:#248A3D,color:#000
```

### Signal Pipeline

Four signals measure different aspects of each message, then combine into one drift score:

```mermaid
graph TD
    MSG["New Message"] --> S1["Semantic Distance<br><i>Global: vs first message</i><br>weight: 0.35"]
    MSG --> S2["Topic Divergence<br><i>Local: vs previous message</i><br>weight: 0.35"]
    MSG --> S3["Specificity Shift<br><i>Vague or concrete?</i><br>weight: 0.15"]
    MSG --> S4["Velocity<br><i>How fast drift accelerates</i><br>weight: 0.15"]
    S1 --> SCORE["Composite Score<br>0.0 — 1.0"]
    S2 --> SCORE
    S3 --> SCORE
    S4 --> SCORE
    SCORE --> CLASS["Classification"]
    SCORE --> GRAPH["3D Topic Graph"]
    SCORE --> CURVE["Drift Curve"]

    style MSG fill:#58a6b8,stroke:#3d7a8a,color:#000
    style SCORE fill:#00E5FF,stroke:#0071A4,color:#000
    style CLASS fill:#FF9F0A,stroke:#C77800,color:#000
    style GRAPH fill:#BF5AF2,stroke:#8944AB,color:#fff
    style CURVE fill:#39FF14,stroke:#248A3D,color:#000
```

### 5-Tier Classification

Each message gets classified — no judgment, just a description of distance from the starting topic:

```mermaid
graph LR
    subgraph " "
    direction LR
    T1["ANCHORED<br>0.0 – 0.1"]
    T2["BRANCHING<br>0.1 – 0.3"]
    T3["TANGENT<br>0.3 – 0.6"]
    T4["WANDERING<br>0.6 – 0.8"]
    T5["DEEP SHIFT<br>0.8 – 1.0"]
    end

    T1 --> T2 --> T3 --> T4 --> T5

    style T1 fill:#39FF14,stroke:#248A3D,color:#000
    style T2 fill:#00E5FF,stroke:#0071A4,color:#000
    style T3 fill:#FF9F0A,stroke:#C77800,color:#000
    style T4 fill:#FFD60A,stroke:#B8A000,color:#000
    style T5 fill:#BF5AF2,stroke:#8944AB,color:#fff
```

### Pivots are data, not deficits

The visualizer doesn't judge. A session with 8 pivots isn't "worse" than one with 0. It's **different**. The goal is awareness — see your patterns, understand them, and use that knowledge however you want.

> [!IMPORTANT]
> This tool is **not a diagnostic instrument**. It does not diagnose, treat, or assess any medical or psychological condition. It visualizes context-switching patterns in conversations — nothing more.

## Quick Start

```bash
git clone https://github.com/qinnovates/ADHD-drift-visualizer.git
cd ADHD-drift-visualizer
pip install -e ".[ui,voyage]"   # or [ui,openai] or [ui,local]

# Run the demo
adhd-drift demo

# Analyze a chat session
adhd-drift analyze session.md --human

# Launch the dashboard
adhd-drift serve
# Open http://127.0.0.1:3457
```

## Features

| Feature | Description |
|---------|-------------|
| **4-Signal Scoring** | Multi-signal drift scoring optimized for conversation topic tracking |
| **Topic Labeling** | Auto-extracts topic labels for each message |
| **Pivot Detection** | Identifies exact messages where topic shifted |
| **Focus Streak** | Longest run of anchored/branching messages |
| **Topic Flow** | Visual timeline of topic changes with color-coded drift |
| **Refocus Suggestions** | ADHD-aware, non-judgmental suggestions to get back on track |
| **Chat Parsers** | Import from Claude Code, ChatGPT, or markdown conversation logs |
| **Historical Mode** | Analyze MEMORY.md files for cross-session patterns |
| **3D Topic Graph** | Interactive WebGL graph showing how topics connect and where your thinking steers |
| **Dashboard** | Real-time visualization with drift curve, 3D graph, topic flow |
| **Pluggable Embeddings** | Voyage AI, OpenAI, or local — use what you already have |
| **CLI** | `adhd-drift analyze`, `serve`, `demo`, `history` — fits into your workflow |

## Chat Log Formats

Upload or point at any of these:

| Format | File Extension | Source |
|--------|---------------|--------|
| Claude Code JSONL | `.jsonl` | `~/.claude/history.jsonl` |
| ChatGPT Export | `.json` | ChatGPT Settings > Data Controls > Export |
| Markdown | `.md`, `.txt` | Any `User: / Assistant:` formatted conversation |

## Claude Code Skill

If you use [Claude Code](https://claude.ai/code), install the skill for in-session analysis:

```bash
# Install the library
pip install -e /path/to/ADHD-drift-visualizer

# Copy the skill
cp -r skills/adhd-drift ~/.claude/skills/adhd-drift
```

Then use it in any session:

```
/adhd-drift                          # Analyze the current session
"analyze my drift"                   # Same thing, natural language
"what do I keep coming back to"      # Cross-session memory analysis
"show my topic graph"                # Launch 3D interactive graph
```

> [!NOTE]
> The skill asks for consent before reading memory files or conversation history. Your data stays local — nothing is transmitted or persisted beyond the session.

## 3D Topic Graph

The dashboard includes an interactive WebGL topic graph showing how your thinking steers between subjects:

- **Nodes** = topics, sized by how often you visit them
- **Edges** = transitions between topics, with directional particles showing flow
- **Colors** = drift classification (green=anchored, cyan=branching, orange=tangent, yellow=wandering, purple=deep shift)
- **Orbit, zoom, hover** for details

Launch it: `adhd-drift serve` then open `http://127.0.0.1:3457` and load a session.

## Use Cases

- **Self-awareness**: See how your conversations actually flow vs how you think they flow
- **Session retrospectives**: "I touched 7 topics but only completed 2 — what do I prioritize tomorrow?"
- **Pair programming**: Visualize drift in real-time during a coding session
- **Meeting analysis**: Score whether a standup stayed focused or went on tangents

---

<details>
<summary><strong>Architecture</strong></summary>

```
src/adhd_drift/
├── engine.py          # DriftEngine — orchestrates all components
├── scorer.py          # 4-signal composite scoring
├── classifier.py      # 5-tier classification
├── tracker.py         # Cumulative drift + pivot detection
├── recovery.py        # Recovery score + refocus suggestions
├── embeddings.py      # Pluggable embedding providers
├── signals.py         # Specificity shift signal
├── topics.py          # Topic extraction + labeling
├── types.py           # Shared dataclasses and enums
├── demo.py            # Sample session
├── history.py         # Cross-session memory analysis
└── parsers/
    ├── claude.py      # Claude Code JSONL
    ├── chatgpt.py     # ChatGPT export JSON
    └── markdown.py    # Generic markdown

ui/
├── dashboard.html     # Single-file dashboard
└── server.py          # Flask dev server
```

</details>

<details>
<summary><strong>Configuration</strong></summary>

### Signal Weights

| Signal | Default Weight | Tune Up For |
|--------|---------------|-------------|
| `semantic_distance` | 0.35 | Tasks where staying on-topic matters most |
| `topic_divergence` | 0.35 | Detecting subject changes |
| `specificity_shift` | 0.15 | Catching when messages get vague |
| `velocity` | 0.15 | Real-time monitoring, alerting |

### Tolerance Profiles

| Profile | Max Drift | Alert At | Best For |
|---------|-----------|----------|----------|
| Strict | 0.15 | 0.10 | Task-focused deep work |
| Standard | 0.30 | 0.25 | Normal conversation |
| Creative | 0.60 | 0.50 | Brainstorming |
| Freeform | 0.80 | 0.70 | Stream of consciousness |

</details>

---

## Development

```bash
pip install -e ".[dev]"
ADHD_DRIFT_EMBEDDINGS=local pytest
ruff check src/
python -m adhd_drift.demo
```

## License

[MIT](LICENSE.md)

---

<p align="center">Built by <a href="https://github.com/qinnovates">qinnovates</a></p>
