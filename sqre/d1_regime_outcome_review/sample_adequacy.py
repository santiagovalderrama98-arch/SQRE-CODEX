"""Sample adequacy rules for D1 outcome review."""

from __future__ import annotations

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig


def sample_adequacy_class(total_sample_size: int, config: D1RegimeOutcomeReviewConfig) -> str:
    return "ADEQUATE" if total_sample_size >= config.minimum_total_sample_size else "LOW_SAMPLE"


def regime_coverage_class(regime_count: int, config: D1RegimeOutcomeReviewConfig) -> str:
    if regime_count >= config.full_regime_count:
        return "FULL"
    if regime_count >= config.minimum_regime_count:
        return "SUFFICIENT"
    return "LIMITED"


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
