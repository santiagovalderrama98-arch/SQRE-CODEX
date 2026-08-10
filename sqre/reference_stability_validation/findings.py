"""Findings and readiness assessment for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import ReferenceStabilityValidationSummary
from sqre.reference_stability_validation.source_inventory import has_missing_required_inputs


def build_summary(
    config: ReferenceStabilityValidationConfig,
    source_inventory: list[object],
    population: pd.DataFrame,
    horizon: pd.DataFrame,
    granularity: pd.DataFrame,
    sample: pd.DataFrame,
    dispersion: pd.DataFrame,
    match_level: pd.DataFrame,
    dashboard: pd.DataFrame,
    query_results: pd.DataFrame,
    manual_review_summary: pd.DataFrame,
) -> ReferenceStabilityValidationSummary:
    reference_count = _sum(population, "Reference_Count")
    core_count = _sum(population, "Core_Reference_Count")
    supporting_count = _sum(population, "Supporting_Reference_Count")
    query_result_count = len(query_results)
    dashboard_card_count = _sum(dashboard, "Reference_Card_Count")
    stable_horizon = _count(horizon, "Horizon_Stability_Class", "STABLE_ACROSS_HORIZONS")
    partial_horizon = _count(horizon, "Horizon_Stability_Class", "PARTIAL_HORIZON_STABILITY")
    unstable_horizon = _count(horizon, "Horizon_Stability_Class", "HORIZON_UNSTABLE")
    stable_granularity = _count(granularity, "Granularity_Stability_Class", "STABLE_GRANULARITY_CONTEXT")
    partial_granularity = _count(granularity, "Granularity_Stability_Class", "PARTIAL_GRANULARITY_CONTEXT")
    fragmented_granularity = _count(granularity, "Granularity_Stability_Class", "FRAGMENTED_GRANULARITY_CONTEXT")
    stable_sample = _count(sample, "Sample_Adequacy_Class", "STABLE_SAMPLE_SIZE")
    usable_sample = _count(sample, "Sample_Adequacy_Class", "USABLE_SAMPLE_SIZE")
    low_sample = _count(sample, "Sample_Adequacy_Class", "LOW_SAMPLE_SIZE")
    stable_dispersion = _count(dispersion, "Dispersion_Stability_Class", "STABLE_DISPERSION")
    usable_dispersion = _count(dispersion, "Dispersion_Stability_Class", "USABLE_DISPERSION")
    high_dispersion = _count(dispersion, "Dispersion_Stability_Class", "HIGH_DISPERSION")
    stable_match = _count(match_level, "Match_Level_Stability_Class", "STABLE_MATCH_LEVEL_USAGE")
    fallback_match = _count(match_level, "Match_Level_Stability_Class", "FALLBACK_DEPENDENT_MATCH_USAGE")
    scope_status = _scope_status(manual_review_summary)
    readiness_class, readiness_flag, diagnostic = _readiness(
        missing_required=has_missing_required_inputs(source_inventory),
        reference_count=reference_count,
        query_result_count=query_result_count,
        dashboard_card_count=dashboard_card_count,
        low_sample=low_sample,
        stable_sample=stable_sample,
        high_dispersion=high_dispersion,
        stable_dispersion=stable_dispersion,
        fallback_match=fallback_match,
        stable_match=stable_match,
    )
    return ReferenceStabilityValidationSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        reference_count=reference_count,
        core_reference_count=core_count,
        supporting_reference_count=supporting_count,
        query_result_count=query_result_count,
        dashboard_reference_card_count=dashboard_card_count,
        stable_horizon_count=stable_horizon,
        partial_horizon_count=partial_horizon,
        unstable_horizon_count=unstable_horizon,
        stable_granularity_count=stable_granularity,
        partial_granularity_count=partial_granularity,
        fragmented_granularity_count=fragmented_granularity,
        stable_sample_group_count=stable_sample,
        usable_sample_group_count=usable_sample,
        low_sample_group_count=low_sample,
        stable_dispersion_group_count=stable_dispersion,
        usable_dispersion_group_count=usable_dispersion,
        high_dispersion_group_count=high_dispersion,
        stable_match_level_count=stable_match,
        fallback_dependent_match_level_count=fallback_match,
        scope_safety_status=scope_status,
        dominant_reference_stability_readiness_class=readiness_class,
        reference_stability_readiness_flag=readiness_flag,
        reference_stability_diagnostic=diagnostic,
        recommended_follow_up=recommended_follow_up(readiness_flag),
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Reference stability documentation",
        "Expanded H4 historical data coverage",
        "Multi-pair reference stability replication",
        "Dashboard stability indicators",
        "Live data snapshot integration design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No provider behavior was changed.",
        "No trading signals were produced.",
        "No operational recommendations were produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local research outputs.",
        "H4 source sample may be partial due to provider row limits.",
        "Stability classifications are research diagnostics only.",
        "Stable reference groups do not imply predictive edge.",
        "Dashboard reference stability may depend on the latest available snapshot.",
        "No operational decision is produced.",
    ]


def scope_statements() -> list[str]:
    return [
        "This phase validates reference stability for research review.",
        "This phase evaluates historical reference robustness across horizons, context granularity, sample size, dispersion, and match levels.",
        "This phase does not generate trading signals.",
        "This phase does not generate operational recommendations.",
        "This phase does not decide whether any context is favorable or unfavorable.",
        "This phase does not perform profitability analysis.",
        "This phase does not create a Decision Engine.",
        "Reference stability findings are descriptive research diagnostics only.",
        "Later phases may document stable reference usage or extend historical coverage, but this phase does not create production decision logic.",
    ]


def recommended_follow_up(readiness_flag: str) -> str:
    if readiness_flag == "READY_FOR_REFERENCE_STABILITY_DOCUMENTATION":
        return "Reference stability documentation; Dashboard stability indicators"
    if readiness_flag == "PARTIAL_READY_FOR_REFERENCE_STABILITY_DOCUMENTATION":
        return "Reference stability documentation; Expanded H4 historical data coverage"
    if readiness_flag == "NOT_READY_REFERENCE_SAMPLE_CONSTRAINED":
        return "Expanded H4 historical data coverage; Multi-pair reference stability replication"
    if readiness_flag == "NOT_READY_REFERENCE_INPUT_LIMITED":
        return "Input completeness review; Reference store regeneration"
    return "Input completeness review"


def _readiness(
    missing_required: bool,
    reference_count: int,
    query_result_count: int,
    dashboard_card_count: int,
    low_sample: int,
    stable_sample: int,
    high_dispersion: int,
    stable_dispersion: int,
    fallback_match: int,
    stable_match: int,
) -> tuple[str, str, str]:
    if missing_required:
        return "INPUT_MISSING", "INPUT_COMPLETENESS_REVIEW_REQUIRED", "Required reference stability inputs are missing."
    if reference_count == 0 or query_result_count == 0:
        return (
            "REFERENCE_STABILITY_INPUT_LIMITED",
            "NOT_READY_REFERENCE_INPUT_LIMITED",
            "Reference stability validation has limited reference or query inputs.",
        )
    if low_sample > stable_sample:
        return (
            "REFERENCE_STABILITY_SAMPLE_CONSTRAINED",
            "NOT_READY_REFERENCE_SAMPLE_CONSTRAINED",
            "Reference stability validation is dominated by low sample groups.",
        )
    if stable_sample > 0 and stable_dispersion > high_dispersion and stable_match >= fallback_match and dashboard_card_count > 0:
        return (
            "REFERENCE_STABILITY_VALIDATED",
            "READY_FOR_REFERENCE_STABILITY_DOCUMENTATION",
            "Reference groups show stable research diagnostics for documentation.",
        )
    return (
        "PARTIAL_REFERENCE_STABILITY_VALIDATED",
        "PARTIAL_READY_FOR_REFERENCE_STABILITY_DOCUMENTATION",
        "Reference groups are usable with partial stability constraints.",
    )


def _scope_status(manual_review_summary: pd.DataFrame) -> str:
    if manual_review_summary.empty or "Scope_Safety_Class" not in manual_review_summary.columns:
        return "OPTIONAL_INPUT_MISSING"
    value = str(manual_review_summary["Scope_Safety_Class"].iloc[0]).strip()
    return value or "OPTIONAL_INPUT_MISSING"


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column].astype(str).str.upper() == value.upper()).sum())


def _sum(frame: pd.DataFrame, column: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum())
