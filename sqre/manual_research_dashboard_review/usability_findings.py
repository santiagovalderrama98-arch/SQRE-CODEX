"""Usability findings for manual research dashboard review."""

from __future__ import annotations

import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.models import ManualDashboardReviewSummary, ReviewSourceInventoryRow
from sqre.manual_research_dashboard_review.source_inventory import has_missing_required_inputs


def build_summary(
    config: ManualResearchDashboardReviewConfig,
    source_inventory: list[ReviewSourceInventoryRow],
    panel_completeness: pd.DataFrame,
    panel_readability: pd.DataFrame,
    field_usefulness: pd.DataFrame,
    redundancy_review: pd.DataFrame,
    scope_safety: pd.DataFrame,
    refinement_recommendations: pd.DataFrame,
) -> ManualDashboardReviewSummary:
    missing_required = has_missing_required_inputs(source_inventory)
    complete = _count(panel_completeness, "Panel_Completeness_Class", "PANEL_COMPLETE")
    partial = _count(panel_completeness, "Panel_Completeness_Class", "PANEL_PARTIAL")
    missing = _count(panel_completeness, "Panel_Completeness_Class", "PANEL_EMPTY") + _count(
        panel_completeness, "Panel_Completeness_Class", "INPUT_MISSING"
    )
    high = _count(panel_readability, "Readability_Class", "HIGH_READABILITY")
    moderate = _count(panel_readability, "Readability_Class", "MODERATE_READABILITY")
    low = _count(panel_readability, "Readability_Class", "LOW_READABILITY") + _count(
        panel_readability, "Readability_Class", "INPUT_MISSING"
    )
    core = _count(field_usefulness, "Field_Usefulness_Class", "CORE_RESEARCH_FIELD")
    supporting = _count(field_usefulness, "Field_Usefulness_Class", "SUPPORTING_RESEARCH_FIELD")
    diagnostic = _count(field_usefulness, "Field_Usefulness_Class", "DIAGNOSTIC_FIELD")
    low_use = _count(field_usefulness, "Field_Usefulness_Class", "REDUNDANT_OR_LOW_USE_FIELD")
    scope_violations = _count(scope_safety, "Scope_Safety_Class", "SCOPE_VIOLATION")
    scope_missing = _count(scope_safety, "Scope_Safety_Class", "INPUT_MISSING")
    scope_class = _scope_class(scope_violations, scope_missing)
    high_reco = _count(refinement_recommendations, "Recommendation_Priority", "HIGH")
    medium_reco = _count(refinement_recommendations, "Recommendation_Priority", "MEDIUM")
    low_reco = _count(refinement_recommendations, "Recommendation_Priority", "LOW")
    readiness_class, readiness_flag, readiness_diagnostic = _readiness(
        missing_required=missing_required,
        missing_panels=missing,
        low_readability=low,
        scope_violations=scope_violations,
        high_priority_recommendations=high_reco,
        complete_panels=complete,
    )
    return ManualDashboardReviewSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        dashboard_source_row_count=len(source_inventory),
        panel_completeness_ready_count=complete,
        panel_completeness_partial_count=partial,
        panel_completeness_missing_count=missing,
        high_readability_panel_count=high,
        moderate_readability_panel_count=moderate,
        low_readability_panel_count=low,
        core_field_count=core,
        supporting_field_count=supporting,
        diagnostic_field_count=diagnostic,
        redundant_or_low_use_field_count=low_use,
        scope_safety_class=scope_class,
        scope_warning_count=scope_missing,
        scope_violation_count=scope_violations,
        recommendation_count=len(refinement_recommendations),
        high_priority_recommendation_count=high_reco,
        medium_priority_recommendation_count=medium_reco,
        low_priority_recommendation_count=low_reco,
        dashboard_usability_readiness_class=readiness_class,
        dashboard_usability_readiness_flag=readiness_flag,
        dashboard_usability_diagnostic=readiness_diagnostic,
        recommended_follow_up=recommended_follow_up(readiness_flag),
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Reference stability validation",
        "Dashboard documentation",
        "Expanded H4 historical data coverage",
        "Multi-pair replication",
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
        "Latest available snapshot may not reflect live market conditions.",
        "H4 source sample may be partial due to provider row limits.",
        "Displayed references do not imply predictive edge.",
        "Dashboard output is descriptive only.",
        "No operational decision is produced.",
        "Usability scoring is rule-based and must be reviewed manually.",
    ]


def scope_statements() -> list[str]:
    return [
        "This phase reviews the dashboard for manual research usability.",
        "This phase may generate a refined static HTML dashboard.",
        "The dashboard summarizes local research outputs only.",
        "The dashboard is not live market data unless explicitly connected in a later phase.",
        "The dashboard retrieves and displays descriptive historical references only.",
        "This phase does not generate trading signals.",
        "This phase does not generate operational recommendations.",
        "This phase does not decide whether any context is favorable or unfavorable.",
        "This phase does not perform profitability analysis.",
        "This phase does not create a Decision Engine.",
        "Later phases may design dashboard usability improvements or live data integration, but this phase does not create production decision logic.",
    ]


def recommended_follow_up(readiness_flag: str) -> str:
    if readiness_flag == "READY_FOR_REPEATED_MANUAL_RESEARCH_USE":
        return "Reference stability validation; Dashboard documentation"
    if readiness_flag == "PARTIAL_READY_FOR_REPEATED_MANUAL_RESEARCH_USE":
        return "Dashboard documentation; Reference stability validation"
    if readiness_flag == "NOT_READY_DASHBOARD_USABILITY_INPUT_LIMITED":
        return "Input completeness review; Dashboard documentation"
    return "Input completeness review"


def _readiness(
    missing_required: bool,
    missing_panels: int,
    low_readability: int,
    scope_violations: int,
    high_priority_recommendations: int,
    complete_panels: int,
) -> tuple[str, str, str]:
    if missing_required:
        return (
            "INPUT_MISSING",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Required dashboard prototype inputs are missing.",
        )
    if missing_panels > 0 or scope_violations > 0:
        return (
            "DASHBOARD_USABILITY_REVIEW_INPUT_LIMITED",
            "NOT_READY_DASHBOARD_USABILITY_INPUT_LIMITED",
            "Dashboard usability review found missing panels or scope safety issues.",
        )
    if complete_panels >= 7 and low_readability == 0 and high_priority_recommendations == 0:
        return (
            "MANUAL_RESEARCH_DASHBOARD_READY",
            "READY_FOR_REPEATED_MANUAL_RESEARCH_USE",
            "Dashboard outputs are ready for repeated manual research review.",
        )
    return (
        "PARTIAL_MANUAL_RESEARCH_DASHBOARD_READY",
        "PARTIAL_READY_FOR_REPEATED_MANUAL_RESEARCH_USE",
        "Dashboard outputs are usable with manual refinement notes.",
    )


def _scope_class(scope_violations: int, scope_missing: int) -> str:
    if scope_violations:
        return "SCOPE_VIOLATION"
    if scope_missing:
        return "SCOPE_WARNING"
    return "SCOPE_SAFE"


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if column not in frame.columns:
        return 0
    return int((frame[column] == value).sum())
