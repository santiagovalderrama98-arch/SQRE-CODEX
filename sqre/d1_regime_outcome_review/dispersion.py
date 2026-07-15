"""Outcome dispersion rules."""

from __future__ import annotations

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig


def dispersion_class(forward_range_cv: float, outcome_magnitude_cv: float, config: D1RegimeOutcomeReviewConfig) -> str:
    if forward_range_cv >= config.high_dispersion_threshold or outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "HIGH"
    if (
        forward_range_cv >= config.moderate_dispersion_threshold
        or outcome_magnitude_cv >= config.moderate_dispersion_threshold
    ):
        return "MODERATE"
    return "LOW"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
