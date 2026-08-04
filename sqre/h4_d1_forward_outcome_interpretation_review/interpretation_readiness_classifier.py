"""Readiness classification for H4/D1 forward outcome interpretation."""

from __future__ import annotations


def classify_readiness(
    outcome_profile_count: int,
    interpretable_count: int,
    moderate_count: int,
    sample_constrained_count: int,
    high_dispersion_count: int,
) -> tuple[str, str, str, str]:
    if outcome_profile_count == 0:
        return (
            "INPUT_MISSING",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Forward outcome profile inputs are missing or empty.",
            "REVIEW_INPUT_COMPLETENESS",
        )
    if interpretable_count > 0:
        return (
            "INTERPRETABLE_OUTCOME_PROFILE",
            "READY_FOR_RESEARCH_REFERENCE_STORE_DESIGN",
            "Some outcome profiles are interpretable for descriptive research reference design.",
            "RESEARCH_REFERENCE_STORE_DESIGN",
        )
    if moderate_count > 0:
        return (
            "MODERATELY_INTERPRETABLE_OUTCOME_PROFILE",
            "PARTIAL_READY_FOR_RESEARCH_REFERENCE_STORE_DESIGN",
            "Outcome profiles have partial descriptive interpretability.",
            "OUTCOME_INTERPRETATION_STABILITY_REVIEW",
        )
    if high_dispersion_count >= sample_constrained_count and high_dispersion_count > 0:
        return (
            "NOT_INTERPRETABLE_HIGH_DISPERSION",
            "NOT_READY_INTERPRETATION_DISPERSION_LIMITED",
            "Outcome interpretation is limited by high dispersion.",
            "OUTCOME_INTERPRETATION_STABILITY_REVIEW",
        )
    return (
        "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED",
        "NOT_READY_INTERPRETATION_SAMPLE_CONSTRAINED",
        "Outcome interpretation is constrained by sample size.",
        "EXPANDED_H4_HISTORICAL_DATA_COVERAGE",
    )
