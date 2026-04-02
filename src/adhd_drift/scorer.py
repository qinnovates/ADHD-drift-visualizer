"""Composite drift scorer — triangulates 4 signals into a single score per message.

Signals reweighted for conversation topic tracking:
- Semantic distance (0.35) — primary: how far meaning shifted
- Topic divergence (0.35) — primary: is the subject different?
- Specificity shift (0.15) — are messages getting vaguer?
- Velocity (0.15) — how fast is drift accelerating?
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from adhd_drift.types import SignalScores


@dataclass
class SignalWeights:
    """Configurable weights for the 4 drift signals. Must sum to 1.0."""

    semantic_distance: float = 0.35
    topic_divergence: float = 0.35
    specificity_shift: float = 0.15
    velocity: float = 0.15

    def validate(self) -> None:
        total = (
            self.semantic_distance
            + self.topic_divergence
            + self.specificity_shift
            + self.velocity
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Signal weights must sum to 1.0, got {total:.3f}")


def compute_composite_score(signals: SignalScores, weights: SignalWeights | None = None) -> float:
    """Compute weighted composite drift score from individual signals.

    Each signal is in [0, 1]. Output is in [0, 1].
    """
    if weights is None:
        weights = SignalWeights()

    raw = (
        weights.semantic_distance * signals.semantic_distance
        + weights.topic_divergence * signals.topic_divergence
        + weights.specificity_shift * signals.specificity_shift
        + weights.velocity * signals.velocity
    )

    return max(0.0, min(1.0, raw))


def compute_topic_divergence(
    baseline_embedding: np.ndarray,
    step_embedding: np.ndarray,
) -> float:
    """KL-inspired topic divergence using embedding distance."""
    similarity = float(np.dot(baseline_embedding, step_embedding))
    return max(0.0, 1.0 - similarity)


def compute_velocity(
    current_score: float,
    previous_scores: list[float],
) -> float:
    """Measure how fast drift is accelerating.

    Returns 0.0 = stable/decelerating, 1.0 = rapid acceleration.
    """
    if not previous_scores:
        return 0.0

    if len(previous_scores) == 1:
        delta = current_score - previous_scores[0]
        return max(0.0, min(1.0, delta * 2.0))

    recent_delta = current_score - previous_scores[-1]
    prev_delta = previous_scores[-1] - previous_scores[-2]
    acceleration = recent_delta - prev_delta

    return max(0.0, min(1.0, (acceleration + 0.5) / 1.0))
