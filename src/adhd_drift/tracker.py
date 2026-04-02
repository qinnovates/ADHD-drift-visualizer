"""Cumulative drift tracking with decay function."""

from __future__ import annotations

import math


def decay_weight(steps_ago: int, half_life: float = 5.0) -> float:
    """Exponential decay: recent steps matter more than old ones.

    half_life controls how fast old drift fades.
    Default: drift from 5 steps ago has half the influence of current step.
    """
    return math.exp(-0.693 * steps_ago / half_life)


def cumulative_drift(
    step_scores: list[float],
    half_life: float = 5.0,
) -> float:
    """Compute cumulative drift at the current step.

    Uses decay-weighted sum: recent drift matters more.
    Normalized to [0, 1] range.
    """
    if not step_scores:
        return 0.0

    n = len(step_scores)
    weighted_sum = 0.0
    weight_sum = 0.0

    for i, score in enumerate(step_scores):
        steps_ago = n - 1 - i
        w = decay_weight(steps_ago, half_life)
        weighted_sum += score * w
        weight_sum += w

    if weight_sum == 0.0:
        return 0.0

    return min(1.0, weighted_sum / weight_sum)


def detect_pivot_points(
    step_scores: list[float],
    velocity_threshold: float = 0.12,
) -> list[int]:
    """Identify messages where topic shifted sharply.

    A pivot point is where the delta between consecutive scores exceeds the threshold.
    Lower threshold than cognitive-drift (0.12 vs 0.15) to catch conversational pivots.
    """
    pivot_points = []
    for i in range(1, len(step_scores)):
        delta = step_scores[i] - step_scores[i - 1]
        if delta > velocity_threshold:
            pivot_points.append(i)
    return pivot_points


def drift_velocity_trend(step_scores: list[float]) -> str:
    """Characterize the overall drift trajectory.

    Returns: "accelerating", "stable", "decelerating", or "refocused".
    """
    if len(step_scores) < 3:
        return "stable"

    recent = step_scores[-3:]
    deltas = [recent[i + 1] - recent[i] for i in range(len(recent) - 1)]
    avg_delta = sum(deltas) / len(deltas)

    if step_scores[-1] < 0.1 and max(step_scores) > 0.3:
        return "refocused"
    elif avg_delta > 0.05:
        return "accelerating"
    elif avg_delta < -0.05:
        return "decelerating"
    else:
        return "stable"


def longest_focus_streak(classifications: list[str]) -> int:
    """Find the longest consecutive run of FOCUSED or EXPLORING messages."""
    focused_states = {"anchored", "branching"}
    max_streak = 0
    current_streak = 0

    for cls in classifications:
        if cls in focused_states:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return max_streak
