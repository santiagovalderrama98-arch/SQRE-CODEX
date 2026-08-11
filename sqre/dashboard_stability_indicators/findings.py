"""Findings and readiness for dashboard stability indicators."""

from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.indicator_summary_builder import (
    count_indicator,
    count_reference_warning,
    count_severity,
)
from sqre.dashboard_stability_indicators.models import DashboardStabilityIndicatorsSummary, class_count
from sqre.dashboard_stability_indicators.scope_safety_review import scope_safety_class
from sqre.dashboard_stability_indicators.source_inventory import has_missing_required_inputs


def build_summary(
    config: DashboardStabilityIndicatorsConfig,
    source_inventory: list[object],
    indicator_map: pd.DataFrame,
    reference_cards: pd.DataFrame,
    warning_summary: pd.DataFrame,
    scope_review: pd.DataFrame,
) -> DashboardStabilityIndicatorsSummary:
    scope_class = scope_safety_class(scope_review)
    scope_warnings = class_count(scope_review, "Dashboard_Stability_Scope_Safety_Class", "DASHBOARD_STABILITY_SCOPE_WARNING")
    scope_violations = class_count(scope_review, "Dashboard_Stability_Scope_Safety_Class", "DASHBOARD_STABILITY_SCOPE_VIOLATION")
    stable = count_indicator(indicator_map, "STABLE_EVIDENCE_INDICATOR") + count_indicator(reference_cards, "STABLE_EVIDENCE_INDICATOR")
    partial = count_indicator(indicator_map, "PARTIAL_EVIDENCE_INDICATOR") + count_indicator(reference_cards, "PARTIAL_EVIDENCE_INDICATOR")
    warning = count_indicator(indicator_map, "WARNING_EVIDENCE_INDICATOR") + count_indicator(reference_cards, "WARNING_EVIDENCE_INDICATOR")
    documentation_only = count_indicator(indicator_map, "DOCUMENTATION_ONLY_INDICATOR") + count_indicator(reference_cards, "DOCUMENTATION_ONLY_INDICATOR")
    moderate = count_severity(reference_cards, "MODERATE_STABILITY_WARNING") + count_severity(warning_summary, "MODERATE_STABILITY_WARNING")
    high = count_severity(reference_cards, "HIGH_STABILITY_WARNING") + count_severity(warning_summary, "HIGH_STABILITY_WARNING")
    readiness_class, readiness_flag, diagnostic = _readiness(
        missing_required=has_missing_required_inputs(source_inventory),
        scope_class=scope_class,
        reference_card_count=len(reference_cards),
        stable_count=stable,
        partial_count=partial,
        warning_count=warning,
    )
    return DashboardStabilityIndicatorsSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        stability_dimension_count=len(indicator_map),
        reference_card_count=len(reference_cards),
        stable_evidence_indicator_count=stable,
        partial_evidence_indicator_count=partial,
        warning_evidence_indicator_count=warning,
        documentation_only_indicator_count=documentation_only,
        fallback_dependent_indicator_count=count_reference_warning(reference_cards, "Fallback"),
        directionally_unstable_indicator_count=count_reference_warning(reference_cards, "Directionally"),
        moderate_stability_warning_count=moderate,
        high_stability_warning_count=high,
        scope_safety_class=scope_class,
        scope_warning_count=scope_warnings,
        scope_violation_count=scope_violations,
        dashboard_stability_readiness_class=readiness_class,
        dashboard_stability_readiness_flag=readiness_flag,
        dashboard_stability_diagnostic=diagnostic,
        recommended_follow_up=recommended_follow_up(readiness_flag),
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Stability-aware dashboard usability review",
        "Expanded H4 historical data coverage",
        "Multi-pair stability indicator replication",
        "Directional consistency review",
        "Fallback dependency review",
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
        "Findings depend on local stability documentation and dashboard outputs.",
        "Latest available snapshot may not reflect live market conditions.",
        "Stability indicators are research diagnostics only.",
        "Stability indicators do not imply predictive edge.",
        "Dashboard cards depend on the latest available snapshot.",
        "No operational decision is produced.",
    ]


def scope_statements() -> list[str]:
    return [
        "This phase adds research-only stability indicators to dashboard outputs.",
        "Stability indicators describe evidence quality and stability constraints.",
        "Stability indicators do not generate trading signals.",
        "Stability indicators do not generate operational recommendations.",
        "Stability indicators do not decide whether any context is favorable or unfavorable.",
        "Stability indicators do not perform profitability analysis.",
        "Stability indicators do not create a Decision Engine.",
        "Later phases may refine dashboard usability or extend historical coverage, but this phase does not create production decision logic.",
    ]


def recommended_follow_up(readiness_flag: str) -> str:
    if readiness_flag == "READY_FOR_STABILITY_AWARE_DASHBOARD_REVIEW":
        return "Stability-aware dashboard usability review"
    if readiness_flag == "PARTIAL_READY_FOR_STABILITY_AWARE_DASHBOARD_REVIEW":
        return "Stability-aware dashboard usability review; Expanded H4 historical data coverage"
    if readiness_flag == "NOT_READY_DASHBOARD_STABILITY_INPUT_LIMITED":
        return "Input completeness review; Dashboard prototype regeneration"
    return "Input completeness review"


def _readiness(
    missing_required: bool,
    scope_class: str,
    reference_card_count: int,
    stable_count: int,
    partial_count: int,
    warning_count: int,
) -> tuple[str, str, str]:
    if missing_required:
        return "INPUT_MISSING", "INPUT_COMPLETENESS_REVIEW_REQUIRED", "Required dashboard stability inputs are missing."
    if scope_class == "DASHBOARD_STABILITY_SCOPE_VIOLATION":
        return (
            "DASHBOARD_STABILITY_INDICATORS_INPUT_LIMITED",
            "NOT_READY_DASHBOARD_STABILITY_INPUT_LIMITED",
            "Dashboard stability outputs contain unsafe scope language.",
        )
    if reference_card_count > 0 and stable_count > 0 and warning_count == 0:
        return (
            "DASHBOARD_STABILITY_INDICATORS_READY",
            "READY_FOR_STABILITY_AWARE_DASHBOARD_REVIEW",
            "Dashboard stability indicators are ready for research dashboard review.",
        )
    if reference_card_count > 0 and (partial_count > 0 or warning_count > 0):
        return (
            "PARTIAL_DASHBOARD_STABILITY_INDICATORS_READY",
            "PARTIAL_READY_FOR_STABILITY_AWARE_DASHBOARD_REVIEW",
            "Dashboard stability indicators are ready with explicit caution labels.",
        )
    return (
        "DASHBOARD_STABILITY_INDICATORS_INPUT_LIMITED",
        "NOT_READY_DASHBOARD_STABILITY_INPUT_LIMITED",
        "Dashboard stability indicators have limited dashboard card inputs.",
    )
