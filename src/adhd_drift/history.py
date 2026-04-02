"""Historical analysis — cross-session drift patterns from memory files.

Analyzes Claude Code MEMORY.md or similar memory index files to find
patterns across multiple sessions: recurring topics, chronic drift areas,
topic clusters that always appear together.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from collections import Counter

from adhd_drift.topics import extract_topic_label


@dataclass
class HistoryInsight:
    """Cross-session analysis result."""

    total_entries: int
    topic_frequency: dict[str, int]
    top_topics: list[str]
    topic_clusters: list[list[str]]
    recurring_pivots: list[str]


def analyze_memory_file(path: str | Path) -> HistoryInsight:
    """Analyze a MEMORY.md index file for cross-session patterns.

    Parses the memory index (list of entries with titles and descriptions)
    to identify recurring topics and patterns.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Memory file not found: {path}")

    text = path.read_text(encoding="utf-8")
    entries = _parse_memory_entries(text)

    topic_labels = [extract_topic_label(entry) for entry in entries]
    topic_counts = Counter(topic_labels)

    top_topics = [topic for topic, _ in topic_counts.most_common(10)]

    clusters = _find_topic_clusters(entries, topic_labels)

    recurring = [
        topic for topic, count in topic_counts.items()
        if count >= 3 and topic != "general"
    ]

    return HistoryInsight(
        total_entries=len(entries),
        topic_frequency=dict(topic_counts),
        top_topics=top_topics,
        topic_clusters=clusters,
        recurring_pivots=recurring,
    )


def _parse_memory_entries(text: str) -> list[str]:
    """Extract individual entries from a MEMORY.md file.

    Handles common formats:
    - Markdown list items (- [Title](file.md) -- description)
    - Heading + paragraph blocks
    """
    entries: list[str] = []

    list_pattern = re.compile(r"^[-*]\s+(.+)$", re.MULTILINE)
    matches = list_pattern.findall(text)

    if matches:
        for match in matches:
            clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match)
            clean = re.sub(r"[*_`]", "", clean)
            if len(clean.strip()) > 3:
                entries.append(clean.strip())
    else:
        paragraphs = re.split(r"\n{2,}", text.strip())
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith("#") and len(para) > 10:
                entries.append(para)

    return entries


def _find_topic_clusters(entries: list[str], labels: list[str]) -> list[list[str]]:
    """Find groups of entries that share topic labels.

    Returns clusters of 2+ entries with the same label.
    """
    label_to_entries: dict[str, list[str]] = {}
    for entry, label in zip(entries, labels):
        label_to_entries.setdefault(label, []).append(entry)

    clusters = [
        entries_list
        for label, entries_list in label_to_entries.items()
        if len(entries_list) >= 2 and label != "general"
    ]

    return clusters
