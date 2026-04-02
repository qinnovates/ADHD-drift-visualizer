"""Parser for Claude Code session JSONL files.

Claude Code stores conversation history in ~/.claude/history.jsonl.
Each line is a JSON object with role, content, and metadata.
"""

from __future__ import annotations

import json
from pathlib import Path

from adhd_drift.types import ChatMessage


def parse_claude_session(path: str | Path) -> list[ChatMessage]:
    """Parse a Claude Code JSONL session file into ChatMessages.

    Extracts user and assistant messages, skipping tool calls and system messages.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Session file not found: {path}")

    messages: list[ChatMessage] = []
    index = 0

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = entry.get("role", "")
            if role not in ("user", "assistant"):
                continue

            content = _extract_text_content(entry)
            if not content or len(content.strip()) < 5:
                continue

            messages.append(ChatMessage(
                index=index,
                text=content,
                role=role,
                timestamp=entry.get("timestamp", ""),
                metadata={"source": "claude"},
            ))
            index += 1

    return messages


def _extract_text_content(entry: dict) -> str:
    """Extract text content from a Claude message entry.

    Content can be a string or a list of content blocks.
    """
    content = entry.get("content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
        return "\n".join(text_parts)

    return ""
