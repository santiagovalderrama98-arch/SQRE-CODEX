"""Reports for D1 regime-normalized research."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from sqre.d1_regime_normalized_research.findings import summary_diagnostic
from sqre.d1_regime_normalized_research.models import (
    D1RegimeConditionProfile,
    D1RegimeResearchResult,
    D1RegimeResearchSummary,
    D1RegimeScenarioInventoryRow,
)


INVENTORY_COLUMNS = [
    "Scenario_ID",
    "Timeframe",
    "Status",
    "Regime_ID",
    "Regime_Label",
    "OHLC_Rows",
    "Structures_Detected",
    "States_Generated",
    "Unique_States",
    "Most_Common_State",
    "Average_Forward_Range_Pips",
    "Direction_Alignment_Rate",
    "Low_Sample_Conditions_Research",
    "Low_Sample_Conditions_Price_Outcome",
    "Price_Outcome_Summary_File_Available",
    "Price_Outcomes_File_Available",
    "Market_States_File_Available",
    "Transitions_File_Available",
]

CONDITION_OUTCOME_COLUMNS = [
    "Regime_ID",
    "Regime_Label",
    "Scenario_ID",
    "Timeframe",
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Sample_Size",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Favorable_Displacement_Pips",
    "Average_Adverse_Displacement_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Sample_Adequacy_Flag",
]

PROFILE_COLUMNS = [
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Regime_Count",
    "Regimes_Present",
    "Scenario_Count",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Regime",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips_Avg",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Close_Return_CV",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Direction_Alignment_CV",
    "Min_Forward_Range_Pips",
    "Max_Forward_Range_Pips",
    "Range_Dispersion_Pips",
    "Min_Outcome_Magnitude_Pips",
    "Max_Outcome_Magnitude_Pips",
    "Outcome_Magnitude_Dispersion_Pips",
    "Sample_Adequacy_Flag",
    "Regime_Coverage_Flag",
    "Regime_Sensitivity_Flag",
    "Condition_Profile_Diagnostic",
    "Recommended_Follow_Up",
]

SUMMARY_COLUMNS = [
    "Timeframe",
    "Scenario_Count",
    "Regime_Count",
    "Completed_Scenario_Count",
    "Total_OHLC_Rows",
    "Average_Structures_Detected",
    "Average_Unique_States",
    "Most_Common_State_Mode",
    "Condition_Profile_Count",
    "State_Condition_Profile_Count",
    "Transition_Condition_Profile_Count",
    "Average_Regime_Count_Per_Profile",
    "Adequate_Profile_Count",
    "Low_Sample_Profile_Count",
    "Stable_Outcome_Profile_Count",
    "Moderate_Sensitivity_Profile_Count",
    "High_Sensitivity_Profile_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Rate",
    "Research_Readiness_Flag",
    "Regime_Sensitivity_Profile",
    "Recommended_Follow_Up",
]


def write_d1_regime_outputs(output_dir: Path | str, result: D1RegimeResearchResult) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "scenario_inventory": root / "d1_regime_scenario_inventory.csv",
        "condition_outcomes": root / "d1_regime_condition_outcomes.csv",
        "normalized_condition_profiles": root / "d1_regime_normalized_condition_profiles.csv",
        "state_outcome_profiles": root / "d1_regime_state_outcome_profiles.csv",
        "transition_outcome_profiles": root / "d1_regime_transition_outcome_profiles.csv",
        "research_summary": root / "d1_regime_research_summary.csv",
    }
    _write_rows(paths["scenario_inventory"], result.inventory_rows, INVENTORY_COLUMNS)
    _write_rows(paths["condition_outcomes"], result.condition_outcomes, CONDITION_OUTCOME_COLUMNS)
    _write_rows(paths["normalized_condition_profiles"], result.condition_profiles, PROFILE_COLUMNS)
    _write_rows(paths["state_outcome_profiles"], result.state_profiles, PROFILE_COLUMNS)
    _write_rows(paths["transition_outcome_profiles"], result.transition_profiles, PROFILE_COLUMNS)
    _write_rows(paths["research_summary"], [result.summary] if result.summary else [], SUMMARY_COLUMNS)
    return paths


def write_d1_regime_research_report(path: Path | str, result: D1RegimeResearchResult) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(result), encoding="utf-8")


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_row_dict(row, columns) for row in rows], columns=columns).to_csv(path, index=False)


def _row_dict(row: object, columns: list[str]) -> dict[str, Any]:
    raw = asdict(row)
    return {column: raw.get(_snake(column), "") for column in columns}


def _build_report(result: D1RegimeResearchResult) -> str:
    summary = result.summary
    lines = [
        "SQRE D1 Regime-Normalized Price Outcome Research Report",
        "======================================================",
        "",
        "Generated At",
        "------------",
        datetime.now(timezone.utc).isoformat(),
        "",
        "Config",
        "------",
        result.config_path,
        "",
        "Input Validation Summary",
        "------------------------",
        result.input_validation_summary,
        "",
        "Validation Output Directory",
        "---------------------------",
        result.validation_output_dir,
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        summary_diagnostic(summary),
        "",
        "Scenario / Regime Inventory",
        "---------------------------",
        *_inventory_lines(result.inventory_rows),
        "",
        "Condition Outcome Coverage",
        "--------------------------",
        *_coverage_lines(summary),
        "",
        "State Outcome Regime Review",
        "---------------------------",
        *_profile_lines(result.state_profiles),
        "",
        "Transition Outcome Regime Review",
        "--------------------------------",
        *_profile_lines(result.transition_profiles),
        "",
        "Regime Sensitivity Review",
        "-------------------------",
        *_sensitivity_lines(result.condition_profiles),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        *_readiness_lines(summary),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        "- D1 regime-normalized state outcome deep dive",
        "- D1 transition outcome regime analysis",
        "- H4 state/transition outcome deep dive",
        "- H4/D1 condition-family aggregation",
        "- Research reference-store design",
        "",
        "Do Not Change Yet",
        "-----------------",
        "- No production defaults were modified.",
        "- No thresholds were modified.",
        "- No production taxonomy was modified.",
        "- No Decision Engine was added.",
        "- No operational logic was added.",
        "",
        "Limitations",
        "-----------",
        "- Regimes are scenario-period labels, not macroeconomic causal classifications.",
        "- Findings depend on available D1 historical samples.",
        "- Findings are descriptive.",
        "- No comparative ordering is produced.",
        "- No production calibration decision is made.",
        "- No operational decision is produced.",
    ]
    return "\n".join(lines) + "\n"


def _inventory_lines(rows: list[D1RegimeScenarioInventoryRow]) -> list[str]:
    if not rows:
        return ["- No D1 scenarios loaded."]
    return [
        (
            f"- {row.scenario_id}: regime={row.regime_id}, label={row.regime_label}, "
            f"status={row.status}, price_summary={row.price_outcome_summary_file_available}, "
            f"states={row.market_states_file_available}, transitions={row.transitions_file_available}"
        )
        for row in rows
    ]


def _coverage_lines(summary: D1RegimeResearchSummary | None) -> list[str]:
    if summary is None:
        return ["- No condition profiles generated."]
    return [
        f"- Total profiles: {summary.condition_profile_count}",
        f"- State profiles: {summary.state_condition_profile_count}",
        f"- Transition profiles: {summary.transition_condition_profile_count}",
        f"- Adequate profiles: {summary.adequate_profile_count}",
        f"- Low sample profiles: {summary.low_sample_profile_count}",
        f"- Average regime count per profile: {summary.average_regime_count_per_profile:.4f}",
    ]


def _profile_lines(profiles: list[D1RegimeConditionProfile]) -> list[str]:
    if not profiles:
        return ["- No matching condition profiles available."]
    return [
        (
            f"- {profile.condition_type}/{profile.condition_label}/fw={profile.forward_window}: "
            f"regimes={profile.regime_count}, sensitivity={profile.regime_sensitivity_flag}, "
            f"sample={profile.sample_adequacy_flag}, diagnostic={profile.condition_profile_diagnostic}"
        )
        for profile in profiles[:10]
    ]


def _sensitivity_lines(profiles: list[D1RegimeConditionProfile]) -> list[str]:
    if not profiles:
        return ["- No regime sensitivity profiles available."]
    stable = sum(1 for profile in profiles if profile.regime_sensitivity_flag == "STABLE")
    moderate = sum(1 for profile in profiles if profile.regime_sensitivity_flag == "MODERATE")
    high = sum(1 for profile in profiles if profile.regime_sensitivity_flag == "HIGH")
    return [
        f"- Stable profiles: {stable}",
        f"- Moderate sensitivity profiles: {moderate}",
        f"- High sensitivity profiles: {high}",
    ]


def _readiness_lines(summary: D1RegimeResearchSummary | None) -> list[str]:
    if summary is None:
        return ["- D1 regime-normalized research requires further review."]
    return [
        f"- Readiness: {summary.research_readiness_flag}",
        f"- Regime sensitivity profile: {summary.regime_sensitivity_profile}",
        f"- Follow-up: {summary.recommended_follow_up}",
    ]


def _snake(column: str) -> str:
    return column.lower()
