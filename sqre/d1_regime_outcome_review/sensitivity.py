"""Regime sensitivity rules."""

from __future__ import annotations

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig


VALID_SENSITIVITY_FLAGS = {"STABLE", "MODERATE", "HIGH"}


def sensitivity_class(
    existing_flag: str,
    forward_range_cv: float,
    outcome_magnitude_cv: float,
    config: D1RegimeOutcomeReviewConfig,
) -> str:
    normalized = str(existing_flag).strip().upper()
    if normalized in VALID_SENSITIVITY_FLAGS:
        return normalized
    if forward_range_cv >= config.high_sensitivity_threshold or outcome_magnitude_cv >= config.high_sensitivity_threshold:
        return "HIGH"
    if (
        forward_range_cv >= config.moderate_sensitivity_threshold
        or outcome_magnitude_cv >= config.moderate_sensitivity_threshold
    ):
        return "MODERATE"
    return "STABLE"
