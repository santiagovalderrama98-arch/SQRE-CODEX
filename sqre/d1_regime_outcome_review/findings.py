"""Findings for D1 regime outcome review."""

from __future__ import annotations

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.sample_adequacy import ratio


def d1_review_diagnostic(
    input_count: int,
    research_ready_count: int,
    regime_sensitive_count: int,
    low_sample_count: int,
    config: D1RegimeOutcomeReviewConfig,
) -> str:
    if input_count == 0:
        return "D1 outcome review requires further descriptive analysis"
    if ratio(low_sample_count, input_count) >= config.low_sample_share_threshold:
        return "D1 condition universe remains sample constrained"
    if research_ready_count > regime_sensitive_count:
        return "D1 has a usable descriptive condition subset for deeper research"
    if regime_sensitive_count > research_ready_count:
        return "D1 condition outcomes require regime-sensitive review before aggregation"
    return "D1 outcome review requires further descriptive analysis"
