"""Summary findings for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.dashboard_panel_builder import first_value
from sqre.research_dashboard_prototype.models import DashboardSourceInventoryRow, ResearchDashboardSummary
from sqre.research_dashboard_prototype.source_inventory import has_missing_required_inputs


def build_summary(
    frames: dict[str, pd.DataFrame],
    source_inventory: list[DashboardSourceInventoryRow],
    reference_cards: pd.DataFrame,
    evidence_panel: pd.DataFrame,
    behavior_panel: pd.DataFrame,
    fallback_panel: pd.DataFrame,
    diagnostic_panel: pd.DataFrame,
    config: ResearchDashboardPrototypeConfig,
) -> ResearchDashboardSummary:
    snapshot_summary = frames.get("snapshot_research_summary", pd.DataFrame())
    snapshot_context = frames.get("snapshot_context", pd.DataFrame())
    reference_store = frames.get("reference_store", pd.DataFrame())
    missing_required = has_missing_required_inputs(source_inventory)
    snapshot_query_count = int(first_value(snapshot_summary, ["Snapshot_Query_Count"], len(frames.get("snapshot_query_requests", pd.DataFrame()))))
    snapshot_result_count = int(first_value(snapshot_summary, ["Snapshot_Result_Count"], len(frames.get("snapshot_reference_results", pd.DataFrame()))))
    coverage = float(first_value(snapshot_summary, ["Snapshot_Reference_Coverage_Ratio"], 0.0) or 0.0)
    readiness_class, readiness_flag, diagnostic = _readiness(
        missing_required=missing_required,
        reference_card_count=len(reference_cards),
        snapshot_query_count=snapshot_query_count,
        coverage=coverage,
        source_flag=str(first_value(snapshot_summary, ["Current_Market_State_Snapshot_Readiness_Flag"], "")),
    )
    return ResearchDashboardSummary(
        symbol=str(first_value(snapshot_summary, ["Symbol"], config.symbol)),
        h4_timeframe=str(first_value(snapshot_summary, ["H4_Timeframe"], config.h4_timeframe)),
        d1_timeframe=str(first_value(snapshot_summary, ["D1_Timeframe"], config.d1_timeframe)),
        snapshot_mode=str(first_value(snapshot_context, ["Snapshot_Mode"], first_value(snapshot_summary, ["Snapshot_Mode"], "INPUT_MISSING"))),
        snapshot_source=str(first_value(snapshot_context, ["Snapshot_Source"], first_value(snapshot_summary, ["Snapshot_Source"], "INPUT_MISSING"))),
        research_reference_count=int(first_value(snapshot_summary, ["Research_Reference_Count"], len(reference_store))),
        snapshot_query_count=snapshot_query_count,
        snapshot_result_count=snapshot_result_count,
        snapshot_reference_coverage_ratio=round(coverage, 4),
        reference_card_count=len(reference_cards),
        evidence_panel_row_count=len(evidence_panel),
        behavior_panel_row_count=len(behavior_panel),
        fallback_panel_row_count=len(fallback_panel),
        diagnostic_panel_row_count=len(diagnostic_panel),
        primary_snapshot_query_match_level=str(first_value(snapshot_summary, ["Primary_Snapshot_Query_Match_Level"], "")),
        primary_snapshot_horizon=str(first_value(snapshot_summary, ["Primary_Snapshot_Horizon"], "")),
        dashboard_readiness_class=readiness_class,
        dashboard_readiness_flag=readiness_flag,
        dashboard_diagnostic=diagnostic,
        recommended_follow_up=recommended_follow_up(readiness_flag),
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Manual research dashboard review",
        "Dashboard usability refinement",
        "Reference stability validation",
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
    ]


def scope_statements() -> list[str]:
    return [
        "This phase creates a research-only dashboard prototype.",
        "The dashboard summarizes local snapshot research outputs.",
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
    if readiness_flag == "READY_FOR_MANUAL_RESEARCH_REVIEW":
        return "Manual research dashboard review; Reference stability validation"
    if readiness_flag == "PARTIAL_READY_FOR_MANUAL_RESEARCH_REVIEW":
        return "Dashboard usability refinement; Reference stability validation"
    return "Input completeness review; Reference stability validation"


def _readiness(
    missing_required: bool,
    reference_card_count: int,
    snapshot_query_count: int,
    coverage: float,
    source_flag: str,
) -> tuple[str, str, str]:
    if missing_required or snapshot_query_count == 0:
        return (
            "INPUT_MISSING",
            "INPUT_COMPLETENESS_REVIEW_REQUIRED",
            "Required dashboard inputs are missing or incomplete.",
        )
    if source_flag == "READY_FOR_RESEARCH_DASHBOARD_PROTOTYPE" and reference_card_count > 0 and coverage > 0:
        return (
            "RESEARCH_DASHBOARD_PROTOTYPE_READY",
            "READY_FOR_MANUAL_RESEARCH_REVIEW",
            "Local snapshot research outputs are ready for manual dashboard review.",
        )
    if reference_card_count > 0:
        return (
            "PARTIAL_RESEARCH_DASHBOARD_PROTOTYPE_READY",
            "PARTIAL_READY_FOR_MANUAL_RESEARCH_REVIEW",
            "Dashboard prototype has partial descriptive reference coverage.",
        )
    return (
        "RESEARCH_DASHBOARD_INPUT_LIMITED",
        "NOT_READY_DASHBOARD_INPUT_LIMITED",
        "Dashboard prototype has limited snapshot reference inputs.",
    )
