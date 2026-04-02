"""Parser for generic markdown conversation logs.

Supports common formats:
- **User:** / **Assistant:** prefixed lines
- ## User / ## Assistant headers
- > blockquote style
- Simple alternating paragraphs (assumes user/assistant alternation)
"""

from __future__ import annotations

import re
from pathlib import Path

from adhd_drift.types import ChatMessage


_ROLE_PATTERNS = [
    re.compile(r"^\*\*(?:User|Human|Me)\*\*:\s*(.*)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^(?:User|Human|Me):\s*(.*)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^##\s*(?:User|Human|Me)\s*$", re.IGNORECASE),
    re.compile(r"^\*\*(?:Assistant|AI|Claude|ChatGPT|Bot)\*\*:\s*(.*)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^(?:Assistant|AI|Claude|ChatGPT|Bot):\s*(.*)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^##\s*(?:Assistant|AI|Claude|ChatGPT|Bot)\s*$", re.IGNORECASE),
]

_USER_MARKERS = {"user", "human", "me"}
_ASSISTANT_MARKERS = {"assistant", "ai", "claude", "chatgpt", "bot"}


def parse_markdown_conversation(path: str | Path) -> list[ChatMessage]:
    """Parse a markdown conversation file into ChatMessages."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Conversation file not found: {path}")

    text = path.read_text(encoding="utf-8")
    return parse_markdown_text(text)


def parse_markdown_text(text: str) -> list[ChatMessage]:
    """Parse markdown conversation text into ChatMessages."""
    lines = text.split("\n")
    segments = _segment_by_role(lines)

    if not segments:
        segments = _segment_by_paragraphs(text)

    messages: list[ChatMessage] = []
    for i, (role, content) in enumerate(segments):
        content = content.strip()
        if len(content) < 5:
            continue

        messages.append(ChatMessage(
            index=i,
            text=content,
            role=role,
            metadata={"source": "markdown"},
        ))

    return messages


def _segment_by_role(lines: list[str]) -> list[tuple[str, str]]:
    """Split lines into (role, content) segments using role markers."""
    segments: list[tuple[str, str]] = []
    current_role = ""
    current_lines: list[str] = []

    for line in lines:
        detected_role = _detect_role(line)

        if detected_role:
            if current_role and current_lines:
                segments.append((current_role, "\n".join(current_lines)))
            current_role = detected_role
            remaining = _strip_role_prefix(line)
            current_lines = [remaining] if remaining else []
        elif current_role:
            current_lines.append(line)

    if current_role and current_lines:
        segments.append((current_role, "\n".join(current_lines)))

    return segments


def _segment_by_paragraphs(text: str) -> list[tuple[str, str]]:
    """Fall back to splitting by double newlines, alternating roles."""
    paragraphs = re.split(r"\n{2,}", text.strip())
    segments: list[tuple[str, str]] = []

    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        role = "user" if i % 2 == 0 else "assistant"
        segments.append((role, para))

    return segments


def _detect_role(line: str) -> str:
    """Detect if a line starts a new role segment."""
    stripped = line.strip().lower()

    for marker in _USER_MARKERS:
        if stripped.startswith(f"**{marker}**:") or stripped.startswith(f"{marker}:"):
            return "user"
        if stripped == f"## {marker}":
            return "user"

    for marker in _ASSISTANT_MARKERS:
        if stripped.startswith(f"**{marker}**:") or stripped.startswith(f"{marker}:"):
            return "assistant"
        if stripped == f"## {marker}":
            return "assistant"

    return ""


def _strip_role_prefix(line: str) -> str:
    """Remove the role prefix from a line, returning the content."""
    for pattern in _ROLE_PATTERNS:
        match = pattern.match(line.strip())
        if match and match.groups():
            return match.group(1).strip()
        elif match:
            return ""
    return line.strip()
