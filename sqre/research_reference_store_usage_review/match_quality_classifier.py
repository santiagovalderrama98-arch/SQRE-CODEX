"""Classifiers for reference-store lookup quality."""

from __future__ import annotations

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig


def classify_match_quality(
    match_level: str,
    sample_size: int,
    dispersion_pips: float,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> str:
    if match_level == "INPUT_MISSING":
        return "INPUT_MISSING"
    if match_level == "NO_REFERENCE_MATCH":
        return "NO_USABLE_REFERENCE_MATCH"
    usable = sample_size >= config.minimum_reference_sample_size
    core = sample_size >= config.minimum_core_reference_sample_size
    controlled = dispersion_pips <= config.maximum_reference_dispersion_pips
    if match_level == "EXACT_D1_STATE_REGIME_CONTEXT_MATCH" and core and controlled:
        return "HIGH_QUALITY_REFERENCE_MATCH"
    if match_level in {"D1_REGIME_CONTEXT_MATCH", "D1_MARKET_STATE_CONTEXT_MATCH"} and usable:
        return "MODERATE_QUALITY_REFERENCE_MATCH" if controlled else "LOW_QUALITY_REFERENCE_MATCH"
    if usable:
        return "LOW_QUALITY_REFERENCE_MATCH"
    return "NO_USABLE_REFERENCE_MATCH"


def classify_evidence_quality(
    reference_tier: str,
    sample_size: int,
    dispersion_pips: float,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> str:
    tier = reference_tier.upper()
    controlled = dispersion_pips <= config.maximum_reference_dispersion_pips
    if tier == "INPUT_MISSING":
        return "INPUT_MISSING"
    if sample_size >= config.minimum_core_reference_sample_size and controlled:
        return "CORE_REFERENCE_EVIDENCE"
    if tier == "CORE_REFERENCE":
        return "CORE_REFERENCE_EVIDENCE"
    if sample_size >= config.minimum_reference_sample_size and controlled:
        return "SUPPORTING_REFERENCE_EVIDENCE"
    if tier == "SUPPORTING_REFERENCE":
        return "SUPPORTING_REFERENCE_EVIDENCE"
    if sample_size >= config.minimum_reference_sample_size or tier == "WATCHLIST_REFERENCE":
        return "WATCHLIST_REFERENCE_EVIDENCE"
    return "INSUFFICIENT_REFERENCE_EVIDENCE"
