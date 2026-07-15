"""CSV and text reports for H4/D1 structural research."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from sqre.h4_d1_structural_research.models import (
    H4D1StructuralResearchResult,
    PriceOutcomeProfile,
    ScenarioInventoryRow,
    SequenceResearchProfile,
    StateResearchProfile,
    TimeframeResearchSummary,
    TransitionResearchProfile,
)


INVENTORY_COLUMNS = [
    "Scenario_ID",
    "Timeframe",
    "Status",
    "OHLC_Rows",
    "Structures_Detected",
    "States_Generated",
    "Unique_States",
    "Most_Common_State",
    "Average_Forward_Range_Pips",
    "Direction_Alignment_Rate",
    "Low_Sample_Conditions_Research",
    "Low_Sample_Conditions_Price_Outcome",
    "Market_States_File_Available",
    "Transitions_File_Available",
    "Condition_Summaries_File_Available",
    "Price_Outcomes_File_Available",
    "Price_Outcome_Summary_File_Available",
    "Sequence_Outcomes_File_Available",
]

STATE_COLUMNS = [
    "Timeframe",
    "Market_State",
    "Scenario_Count",
    "Scenarios_Present",
    "Total_State_Count",
    "Average_State_Count_Per_Scenario",
    "State_Frequency_Ratio",
    "Average_State_Confidence",
    "Scenario_Count_CV",
    "State_Sample_Adequacy_Flag",
    "State_Scenario_Consistency_Flag",
    "State_Profile_Diagnostic",
]

TRANSITION_COLUMNS = [
    "Timeframe",
    "From_State",
    "To_State",
    "Transition_Label",
    "Scenario_Count",
    "Scenarios_Present",
    "Total_Transition_Count",
    "Average_Transition_Count_Per_Scenario",
    "Transition_Frequency_Ratio",
    "Scenario_Count_CV",
    "Transition_Sample_Adequacy_Flag",
    "Transition_Consistency_Flag",
    "Transition_Profile_Diagnostic",
]

PRICE_COLUMNS = [
    "Timeframe",
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Scenario_Count",
    "Scenarios_Present",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Scenario",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Favorable_Displacement_Pips",
    "Average_Adverse_Displacement_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Scenario_Sensitivity_Flag",
    "Sample_Adequacy_Flag",
    "Outcome_Profile_Diagnostic",
]

SEQUENCE_COLUMNS = [
    "Timeframe",
    "Sequence_Label",
    "Scenario_Count",
    "Scenarios_Present",
    "Total_Sequence_Count",
    "Average_Sequence_Count_Per_Scenario",
    "Sequence_Sample_Adequacy_Flag",
    "Sequence_Profile_Diagnostic",
]

TIMEFRAME_COLUMNS = [
    "Timeframe",
    "Scenario_Count",
    "Completed_Scenario_Count",
    "Total_OHLC_Rows",
    "Average_Structures_Detected",
    "Structure_Count_CV",
    "Average_States_Generated",
    "Average_Unique_States",
    "Most_Common_State_Mode",
    "Average_Forward_Range_Pips",
    "Forward_Range_CV",
    "Average_Direction_Alignment_Rate",
    "Average_Low_Sample_Conditions_Research",
    "Average_Low_Sample_Conditions_Price_Outcome",
    "State_Profile_Count",
    "Transition_Profile_Count",
    "Price_Outcome_Profile_Count",
    "Sequence_Profile_Count",
    "Structural_Maturity_Flag",
    "Research_Sample_Quality_Flag",
    "Scenario_Sensitivity_Flag",
    "Timeframe_Research_Diagnostic",
    "Recommended_Follow_Up",
]


def write_h4_d1_outputs(output_dir: Path | str, result: H4D1StructuralResearchResult) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "inventory": root / "h4_d1_scenario_inventory.csv",
        "state_profiles": root / "h4_d1_state_research_profiles.csv",
        "transition_profiles": root / "h4_d1_transition_research_profiles.csv",
        "price_outcome_profiles": root / "h4_d1_price_outcome_profiles.csv",
        "sequence_profiles": root / "h4_d1_sequence_research_profiles.csv",
        "timeframe_summary": root / "h4_d1_timeframe_research_summary.csv",
    }
    _write_rows(paths["inventory"], result.inventory_rows, INVENTORY_COLUMNS)
    _write_rows(paths["state_profiles"], result.state_profiles, STATE_COLUMNS)
    _write_rows(paths["transition_profiles"], result.transition_profiles, TRANSITION_COLUMNS)
    _write_rows(paths["price_outcome_profiles"], result.price_outcome_profiles, PRICE_COLUMNS)
    _write_rows(paths["sequence_profiles"], result.sequence_profiles, SEQUENCE_COLUMNS)
    _write_rows(paths["timeframe_summary"], result.timeframe_summaries, TIMEFRAME_COLUMNS)
    return paths


def write_h4_d1_research_report(path: Path | str, result: H4D1StructuralResearchResult) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(result), encoding="utf-8")


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_row_dict(row, columns) for row in rows], columns=columns).to_csv(path, index=False)


def _row_dict(row: object, columns: list[str]) -> dict[str, Any]:
    raw = asdict(row)
    return {column: raw.get(_snake(column), "") for column in columns}


def _build_report(result: H4D1StructuralResearchResult) -> str:
    lines = [
        "SQRE H4/D1 Structural Research Report",
        "====================================",
        "",
        "Generated At",
        "------------",
        datetime.now(timezone.utc).isoformat(),
        "",
        "Input Validation Summary",
        "------------------------",
        result.input_validation_summary,
        "",
        "Validation Output Directory",
        "---------------------------",
        result.validation_output_dir,
        "",
        "Scenarios Loaded",
        "----------------",
        str(result.scenarios_loaded),
        "",
        "Files Available",
        "---------------",
        *_file_availability_lines(result.inventory_rows),
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        *_summary_lines(result.timeframe_summaries),
        "",
        "Scenario Inventory",
        "------------------",
        *_inventory_lines(result.inventory_rows),
        "",
        "H4 Structural Research Review",
        "-----------------------------",
        *_timeframe_review_lines("H4", result),
        "",
        "D1 Structural Research Review",
        "-----------------------------",
        *_timeframe_review_lines("D1", result),
        "",
        "State Profile Review",
        "--------------------",
        *_top_state_lines(result.state_profiles),
        "",
        "Transition Profile Review",
        "-------------------------",
        *_top_transition_lines(result.transition_profiles),
        "",
        "Price Outcome Research Review",
        "-----------------------------",
        *_top_price_lines(result.price_outcome_profiles),
        "",
        "Sequence Research Review",
        "------------------------",
        *_sequence_lines(result.sequence_profiles),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        *_readiness_lines(result.timeframe_summaries),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        "- D1 regime-normalized price outcome research",
        "- H4 state/transition outcome deep dive",
        "- H4/D1 condition-family aggregation",
        "- Research reference-store design",
        "- Continued monitoring of H1/M15 as secondary context",
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
        "- Findings depend on available H4/D1 historical samples.",
        "- Findings are descriptive.",
        "- No comparative ordering is produced.",
        "- No production calibration decision is made.",
        "- No operational decision is produced.",
        "",
    ]
    return "\n".join(lines)


def _file_availability_lines(rows: list[ScenarioInventoryRow]) -> list[str]:
    if not rows:
        return ["- No scenarios loaded."]
    return [
        f"- {row.scenario_id}: states={row.market_states_file_available}, transitions={row.transitions_file_available}, "
        f"conditions={row.condition_summaries_file_available}, price_summary={row.price_outcome_summary_file_available}, "
        f"sequences={row.sequence_outcomes_file_available}"
        for row in rows
    ]


def _summary_lines(rows: list[TimeframeResearchSummary]) -> list[str]:
    return [f"- {row.timeframe}: {row.timeframe_research_diagnostic}" for row in rows] or [
        "- No timeframe summaries available."
    ]


def _inventory_lines(rows: list[ScenarioInventoryRow]) -> list[str]:
    return [
        f"- {row.scenario_id} ({row.timeframe}): status={row.status}, ohlc_rows={row.ohlc_rows}, "
        f"structures={row.structures_detected}, states={row.states_generated}"
        for row in rows
    ] or ["- No scenario inventory rows available."]


def _timeframe_review_lines(timeframe: str, result: H4D1StructuralResearchResult) -> list[str]:
    summary = next((row for row in result.timeframe_summaries if row.timeframe == timeframe), None)
    if summary is None:
        return [f"- No {timeframe} rows available."]
    return [
        f"- {timeframe} scenarios={summary.scenario_count}, completed={summary.completed_scenario_count}.",
        f"- State profiles={summary.state_profile_count}, transition profiles={summary.transition_profile_count}.",
        f"- Price outcome profiles={summary.price_outcome_profile_count}, sequence profiles={summary.sequence_profile_count}.",
        f"- Sample quality={summary.research_sample_quality_flag}, scenario sensitivity={summary.scenario_sensitivity_flag}.",
        f"- Diagnostic: {summary.timeframe_research_diagnostic}",
    ]


def _top_state_lines(rows: list[StateResearchProfile]) -> list[str]:
    top = sorted(rows, key=lambda row: row.total_state_count, reverse=True)[:10]
    return [
        f"- {row.timeframe} {row.market_state}: count={row.total_state_count}, "
        f"frequency={row.state_frequency_ratio:.4f}, consistency={row.state_scenario_consistency_flag}"
        for row in top
    ] or ["- No state profiles available."]


def _top_transition_lines(rows: list[TransitionResearchProfile]) -> list[str]:
    top = sorted(rows, key=lambda row: row.total_transition_count, reverse=True)[:10]
    return [
        f"- {row.timeframe} {row.transition_label}: count={row.total_transition_count}, "
        f"frequency={row.transition_frequency_ratio:.4f}, consistency={row.transition_consistency_flag}"
        for row in top
    ] or ["- No transition profiles available."]


def _top_price_lines(rows: list[PriceOutcomeProfile]) -> list[str]:
    top = sorted(rows, key=lambda row: row.total_sample_size, reverse=True)[:10]
    return [
        f"- {row.timeframe} {row.condition_type} {row.condition_label} window={row.forward_window}: "
        f"sample={row.total_sample_size}, range_cv={row.forward_range_cv:.4f}, "
        f"sensitivity={row.scenario_sensitivity_flag}, adequacy={row.sample_adequacy_flag}"
        for row in top
    ] or ["- No price outcome profiles available."]


def _sequence_lines(rows: list[SequenceResearchProfile]) -> list[str]:
    top = sorted(rows, key=lambda row: row.total_sequence_count, reverse=True)[:10]
    return [
        f"- {row.timeframe} {row.sequence_label}: count={row.total_sequence_count}, "
        f"adequacy={row.sequence_sample_adequacy_flag}"
        for row in top
    ] or ["- No sequence profiles available."]


def _readiness_lines(rows: list[TimeframeResearchSummary]) -> list[str]:
    return [
        f"- {row.timeframe}: {row.structural_maturity_flag}; follow-up={row.recommended_follow_up}"
        for row in rows
    ] or ["- No readiness rows available."]


def _snake(column: str) -> str:
    return column.lower()
