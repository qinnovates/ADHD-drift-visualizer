"""Signal extraction for ADHD drift scoring.

Signals are optimized for conversation topic tracking, not AI hallucination
detection. Citation density is dropped — replaced by specificity shift
(measures whether messages are getting vaguer or more concrete over time).
"""

from __future__ import annotations

import re

from adhd_drift.types import ChatMessage


_VAGUE_PATTERNS = [
    r"\bi dunno\b",
    r"\bwhatever\b",
    r"\banyway\b",
    r"\bkinda\b",
    r"\bsort of\b",
    r"\bmaybe\b",
    r"\bI guess\b",
    r"\boff topic\b",
    r"\brandom thought\b",
    r"\boh wait\b",
    r"\bactually\b",
    r"\bnvm\b",
    r"\bnever\s?mind\b",
    r"\bsidetrack\b",
]
_VAGUE_RE = [re.compile(p, re.IGNORECASE) for p in _VAGUE_PATTERNS]

_SPECIFIC_PATTERNS = [
    r"\b\d+\.?\d*\s*%",
    r"\b\d{4}\b",
    r"\b(?:v|version)\s*\d+\.\d+",
    r"\b(?:file|line|function|class|method|module)\s+\S+",
    r"\bhttps?://\S+",
    r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+){2,}\b",
]
_SPECIFIC_RE = [re.compile(p) for p in _SPECIFIC_PATTERNS]


def specificity_shift(message: ChatMessage) -> float:
    """Measure how specific vs vague the message is.

    Returns inverted score: 0.0 = highly specific, 1.0 = pure tangent-speak.
    """
    text = message.text
    if not text.strip():
        return 0.5

    word_count = max(len(text.split()), 1)

    vague_hits = sum(1 for p in _VAGUE_RE if p.search(text))
    specific_hits = sum(1 for p in _SPECIFIC_RE if p.search(text))

    vague_density = vague_hits / (word_count / 20.0)
    specific_density = specific_hits / (word_count / 20.0)

    raw = (min(vague_density, 1.0) - min(specific_density, 1.0) + 1.0) / 2.0
    return max(0.0, min(1.0, raw))
