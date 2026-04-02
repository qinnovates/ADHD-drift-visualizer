"""Recovery scoring — how easy is it to get back on track?"""

from __future__ import annotations

from adhd_drift.types import ChatMessage, DriftScore


def recovery_score(
    current_drift: float,
    steps_since_focused: int,
) -> float:
    """Compute how recoverable the current drift state is.

    Returns 0.0 = far from original thread, 1.0 = close to original thread.
    """
    if current_drift < 0.1:
        return 1.0

    distance_penalty = min(steps_since_focused * 0.1, 0.5)

    raw = 1.0 - current_drift - distance_penalty
    return max(0.0, min(1.0, raw))


def refocus_suggestions(
    message: ChatMessage,
    score: DriftScore,
) -> list[str]:
    """Generate actionable suggestions to refocus the conversation.

    Framed constructively — ADHD-aware, not judgmental.
    """
    suggestions = []

    if score.signals.semantic_distance > 0.5:
        suggestions.append(
            "Circle back: what was the original question or goal?"
        )

    if score.signals.specificity_shift > 0.5:
        suggestions.append(
            "Get concrete: name a specific file, number, or next action"
        )

    if score.signals.velocity > 0.5:
        suggestions.append(
            "You've covered several topics quickly. Which one has a deadline?"
        )

    if score.is_pivot:
        suggestions.append(
            f"Topic shifted to '{score.topic_label}'. Intentional pivot or tangent?"
        )

    if score.composite_score > 0.6 and not suggestions:
        suggestions.append(
            "You've gone deep on something new. Park it or commit: is this the new focus?"
        )

    return suggestions
