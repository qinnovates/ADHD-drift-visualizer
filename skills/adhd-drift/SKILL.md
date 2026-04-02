---
name: adhd-drift
version: 0.1.0
description: |
  Analyze cognitive drift and context-switching patterns in chat sessions and memory files.
  Shows 3D topic graphs of how thinking steers between subjects. Works with Claude Code
  memory, ChatGPT exports, or any conversation log. Use when asked to "analyze my drift",
  "how scattered was this session", "show my topic graph", "what do I keep coming back to",
  or "map my conversation patterns".
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(adhd-drift:*)
  - Bash(python:*)
  - Agent
  - AskUserQuestion
---

# ADHD Drift Visualizer — Claude Code Skill

Analyze context-switching patterns in conversations and memory files. Produces drift scores,
topic graphs, and cross-session pattern detection.

**Not a diagnostic instrument.** This visualizes context-switching patterns — nothing more.
Pivots are data, not deficits.

## CONSENT GATE (MANDATORY — run before ANY analysis)

Before reading any memory files, conversation history, or session data, you MUST:

1. **Explain what will be scanned:**
   ```
   ADHD Drift Analysis — Data Access Request

   To analyze your conversation patterns, I need to read:
   - [specific files listed here — e.g., "~/.claude/projects/.../memory/MEMORY.md"]
   - OR: "the conversation in this current session"
   - OR: "the uploaded file you provided"

   This data stays local. Nothing is transmitted, stored, or persisted
   beyond this session. The analysis runs entirely on your machine.
   ```

2. **Ask for explicit consent:**
   Use AskUserQuestion: "Proceed with drift analysis on these files? (yes/no)"

3. **If declined:** Respect immediately. Do not ask again. Suggest the demo instead:
   `adhd-drift demo`

4. **If approved:** Proceed with analysis. Never re-ask for the same files in the same session.

**Exception:** If the user explicitly says "analyze my drift" or "scan my memory" — that IS
consent. No gate needed for explicit requests. The gate is for when YOU proactively suggest
scanning files the user hasn't mentioned.

## When This Skill Activates

| User Says | What To Do |
|-----------|-----------|
| "analyze my drift" / "how scattered was I" | Analyze current session messages |
| "show my topic graph" | Run analysis + launch dashboard with 3D graph |
| "what do I keep coming back to" | Cross-session history analysis on MEMORY.md |
| "map my conversation" | Full session analysis + topic flow |
| "analyze this file" + attachment | Parse the file and analyze |

## Analysis Modes

### Mode 1: Current Session Analysis

Analyze the conversation happening right now.

1. Collect user/assistant messages from the current session
2. Write them to a temp markdown file
3. Run: `adhd-drift analyze /tmp/current-session.md --human`
4. Present the results with the topic flow and key stats
5. Offer to launch the dashboard: `adhd-drift serve`

### Mode 2: Memory File Analysis (Cross-Session)

Analyze patterns across multiple sessions using memory files.

1. **Consent gate** (if not already given)
2. Locate memory file:
   - Global: `~/.claude/projects/-Users-*/memory/MEMORY.md`
   - Project: `~/.claude/projects/-Users-*-Documents-PROJECTS*/memory/MEMORY.md`
3. Run: `adhd-drift history <path-to-MEMORY.md>`
4. Present: recurring topics, topic clusters, chronic pivots
5. Frame constructively: "Topics you keep returning to" not "things you can't finish"

### Mode 3: File Analysis

User provides a chat log file.

1. Auto-detect format from extension (.jsonl, .json, .md, .txt)
2. Run: `adhd-drift analyze <file> --human`
3. Present results
4. Offer dashboard: `adhd-drift serve`

### Mode 4: Dashboard Launch

User wants the visual 3D graph.

1. Run: `adhd-drift serve`
2. Tell user: "Dashboard running at http://127.0.0.1:3457"
3. If they have a session to load, use the API:
   ```bash
   curl -X POST http://127.0.0.1:3457/api/demo  # or upload via dashboard
   ```

## Output Format

Present results as a concise summary, not a wall of data:

```
Session Drift Analysis
======================
Messages: 13  |  Pivots: 8  |  Peak: 0.86 (msg 4)
Focus streak: 2  |  Trend: accelerating

Topic flow: auth tokens -> CSS bug -> meeting prep -> auth debate -> db migration -> auth fix

Key observations:
- You pivoted 8 times across 5 distinct topics
- Longest focus was 2 consecutive messages on auth tokens
- Meeting prep was the biggest drift (0.86) from your starting topic
- You circled back to auth 3 times — it's clearly the priority

[Launch 3D graph: adhd-drift serve]
```

## Framing Rules

- **Never say "you were scattered"** — say "you covered N topics"
- **Never say "you lost focus"** — say "the topic shifted at message N"
- **Never prescribe** — describe patterns and let the user decide what to do
- **Acknowledge productive pivots** — "you circled back to X, showing it's a priority"
- **Use neutral language** — ANCHORED, BRANCHING, TANGENT, WANDERING, DEEP SHIFT
- **No red in severity** — wandering is yellow, not red

## Requirements

The `adhd-drift` CLI must be installed:
```bash
pip install -e /Users/mac/Documents/PROJECTS/ADHD-drift-visualizer
```

If not installed, tell the user and offer to install it.
