"""Topic extraction and labeling for conversation messages.

Uses embedding clustering to identify topic shifts and generate
human-readable labels from the most distinctive terms in each cluster.
"""

from __future__ import annotations

import re
from collections import Counter

import numpy as np

from adhd_drift.embeddings import embed_batch, cosine_distance


# Common words to skip when generating topic labels
_STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "don", "now", "and", "but", "or", "if", "while", "that", "this",
    "it", "its", "i", "me", "my", "you", "your", "we", "our", "they",
    "them", "their", "what", "which", "who", "whom", "these", "those",
    "am", "he", "she", "him", "her", "his", "about", "up", "like",
    "yeah", "yes", "no", "ok", "okay", "sure", "right", "well", "also",
    "got", "get", "let", "thing", "things", "want", "going", "think",
    "know", "really", "actually", "basically", "literally", "maybe",
})


def extract_topic_label(text: str, max_words: int = 3) -> str:
    """Extract a short topic label from message text.

    Uses term frequency with stop word filtering to pick the most
    distinctive words. Returns lowercased label.
    """
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    filtered = [w for w in words if w not in _STOP_WORDS]

    if not filtered:
        return "general"

    counts = Counter(filtered)
    top_words = [word for word, _ in counts.most_common(max_words)]
    return " ".join(top_words)


def detect_topic_shift(
    current_embedding: np.ndarray,
    previous_embedding: np.ndarray,
    threshold: float = 0.3,
) -> bool:
    """Detect if a topic shift occurred between two messages."""
    distance = cosine_distance(current_embedding, previous_embedding)
    return distance > threshold


def label_session_topics(
    messages: list[str],
    shift_threshold: float = 0.3,
) -> list[str]:
    """Assign topic labels to a sequence of messages.

    Messages within the same topic cluster share a label derived from the
    first message in that cluster. A new cluster starts when semantic
    distance exceeds shift_threshold.
    """
    if not messages:
        return []

    embeddings = embed_batch(messages)
    labels: list[str] = []
    current_cluster_start = 0
    current_label = extract_topic_label(messages[0])

    labels.append(current_label)

    for i in range(1, len(messages)):
        distance = cosine_distance(embeddings[current_cluster_start], embeddings[i])

        if distance > shift_threshold:
            current_cluster_start = i
            current_label = extract_topic_label(messages[i])

        labels.append(current_label)

    return labels


def most_visited_topic(labels: list[str]) -> str:
    """Return the topic label that appeared most frequently."""
    if not labels:
        return "none"
    counts = Counter(labels)
    return counts.most_common(1)[0][0]
