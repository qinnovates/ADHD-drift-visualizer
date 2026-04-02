"""Parser for ChatGPT export JSON files.

ChatGPT exports conversations as JSON with a specific structure:
{
  "title": "...",
  "mapping": {
    "uuid": {
      "message": {
        "author": {"role": "user"|"assistant"},
        "content": {"parts": ["..."]}
      },
      "parent": "uuid",
      "children": ["uuid"]
    }
  }
}
"""

from __future__ import annotations

import json
from pathlib import Path

from adhd_drift.types import ChatMessage


def parse_chatgpt_export(path: str | Path) -> list[ChatMessage]:
    """Parse a ChatGPT export JSON file into ChatMessages.

    Walks the conversation tree in order, extracting user and assistant messages.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Export file not found: {path}")

    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    if isinstance(data, list):
        all_messages = []
        for conversation in data:
            all_messages.extend(_parse_single_conversation(conversation))
        return all_messages

    return _parse_single_conversation(data)


def _parse_single_conversation(data: dict) -> list[ChatMessage]:
    """Parse a single ChatGPT conversation object."""
    mapping = data.get("mapping", {})
    if not mapping:
        return []

    root_id = None
    for node_id, node in mapping.items():
        if node.get("parent") is None:
            root_id = node_id
            break

    if root_id is None:
        return []

    ordered_nodes: list[dict] = []
    _walk_tree(mapping, root_id, ordered_nodes)

    messages: list[ChatMessage] = []
    index = 0

    for node in ordered_nodes:
        msg = node.get("message")
        if not msg:
            continue

        author = msg.get("author", {})
        role = author.get("role", "")
        if role not in ("user", "assistant"):
            continue

        content = msg.get("content", {})
        parts = content.get("parts", [])
        text = "\n".join(str(p) for p in parts if isinstance(p, str))

        if not text or len(text.strip()) < 5:
            continue

        timestamp = msg.get("create_time", "")
        if isinstance(timestamp, (int, float)):
            from datetime import datetime, timezone

            timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        messages.append(ChatMessage(
            index=index,
            text=text,
            role=role,
            timestamp=str(timestamp),
            metadata={"source": "chatgpt", "title": data.get("title", "")},
        ))
        index += 1

    return messages


def _walk_tree(mapping: dict, node_id: str, result: list[dict]) -> None:
    """Walk the conversation tree depth-first to get messages in order."""
    node = mapping.get(node_id, {})
    result.append(node)
    for child_id in node.get("children", []):
        _walk_tree(mapping, child_id, result)
