"""Evidence and quality classifiers for research query results."""

from __future__ import annotations

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig


def classify_result_quality(match_level: str, sample_size: int, dispersion_pips: float, config: ResearchQueryInterfaceDesignConfig) -> str:
    if match_level == "INPUT_MISSING":
        return "INPUT_MISSING"
    if match_level == "NO_RESEARCH_REFERENCE_QUERY_MATCH":
        return "NO_USABLE_RESEARCH_QUERY_RESULT"
    usable = sample_size >= config.minimum_reference_sample_size
    core = sample_size >= config.minimum_core_reference_sample_size
    controlled = dispersion_pips <= config.maximum_reference_dispersion_pips
    if match_level == "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH" and core and controlled:
        return "HIGH_QUALITY_RESEARCH_QUERY_RESULT"
    if match_level in {"D1_REGIME_CONTEXT_QUERY_MATCH", "D1_MARKET_STATE_CONTEXT_QUERY_MATCH"} and usable:
        return "MODERATE_QUALITY_RESEARCH_QUERY_RESULT" if controlled else "LOW_QUALITY_RESEARCH_QUERY_RESULT"
    if usable:
        return "LOW_QUALITY_RESEARCH_QUERY_RESULT"
    return "NO_USABLE_RESEARCH_QUERY_RESULT"


def classify_evidence(reference_tier: str, sample_size: int, dispersion_pips: float, config: ResearchQueryInterfaceDesignConfig) -> str:
    tier = reference_tier.upper()
    controlled = dispersion_pips <= config.maximum_reference_dispersion_pips
    if tier == "INPUT_MISSING":
        return "INPUT_MISSING"
    if sample_size >= config.minimum_core_reference_sample_size and controlled:
        return "CORE_RESEARCH_REFERENCE_EVIDENCE"
    if tier == "CORE_REFERENCE":
        return "CORE_RESEARCH_REFERENCE_EVIDENCE"
    if sample_size >= config.minimum_reference_sample_size and controlled:
        return "SUPPORTING_RESEARCH_REFERENCE_EVIDENCE"
    if tier == "SUPPORTING_REFERENCE":
        return "SUPPORTING_RESEARCH_REFERENCE_EVIDENCE"
    if sample_size >= config.minimum_reference_sample_size or tier == "WATCHLIST_REFERENCE":
        return "WATCHLIST_RESEARCH_REFERENCE_EVIDENCE"
    return "INSUFFICIENT_RESEARCH_REFERENCE_EVIDENCE"
