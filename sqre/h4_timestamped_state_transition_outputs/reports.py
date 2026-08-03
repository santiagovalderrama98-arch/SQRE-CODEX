"""Output writers for H4 timestamped state/transition output generation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_state_transition_outputs.findings import (
    descriptive_findings,
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.h4_timestamped_state_transition_outputs.models import H4TimestampedStateTransitionResult


SOURCE_COLUMNS = [
    "Source_Name",
    "Source_Type",
    "Path",
    "Exists",
    "Load_Status",
    "Rows_Loaded",
    "Timestamp_Columns",
    "Scenario_Columns",
    "State_Columns",
    "Transition_Columns",
    "Diagnostic",
]
SCENARIO_COLUMNS = [
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Period_Start",
    "Period_End",
    "Scenario_Status",
    "Raw_OHLC_File",
    "Raw_OHLC_Available",
    "Existing_State_Output_Available",
    "Existing_Transition_Output_Available",
    "Regeneration_Attempted",
    "Regeneration_Status",
    "Timestamped_State_Row_Count",
    "Timestamped_Transition_Row_Count",
    "Scenario_Output_Coverage_Class",
    "Scenario_Diagnostic",
]
STATE_COLUMNS = [
    "H4_Timestamped_State_ID",
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Scenario_Period_Start",
    "Scenario_Period_End",
    "State_Start_Time",
    "State_End_Time",
    "State_Event_Time",
    "State_Event_Date",
    "Market_State",
    "State_Confidence",
    "Structure_ID",
    "Structure_Direction",
    "Structural_Efficiency",
    "Structural_Confidence",
    "State_Row_Source",
    "State_Row_Diagnostic",
]
TRANSITION_COLUMNS = [
    "H4_Timestamped_Transition_ID",
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Scenario_Period_Start",
    "Scenario_Period_End",
    "Transition_Time",
    "Transition_Date",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Source_State_Start_Time",
    "Source_State_End_Time",
    "Target_State_Start_Time",
    "Target_State_End_Time",
    "Source_State_Confidence",
    "Target_State_Confidence",
    "Transition_Row_Source",
    "Transition_Row_Diagnostic",
]
COVERAGE_COLUMNS = [
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Period_Start",
    "Period_End",
    "Expected_State_Count",
    "Expected_Transition_Count",
    "Timestamped_State_Row_Count",
    "Timestamped_Transition_Row_Count",
    "State_Temporal_Key_Complete_Row_Count",
    "Transition_Temporal_Key_Complete_Row_Count",
    "State_Coverage_Ratio",
    "Transition_Coverage_Ratio",
    "Coverage_Class",
    "Coverage_Diagnostic",
]
MISSING_COLUMNS = [
    "Missing_Output_ID",
    "Scenario_ID",
    "Missing_Output_Type",
    "Current_Source_Status",
    "Required_Source_Action",
    "Missing_Output_Diagnostic",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "Timeframe",
    "Scenario_Count",
    "Source_Inventory_Row_Count",
    "Timestamped_State_Row_Count",
    "Timestamped_Transition_Row_Count",
    "Scenario_With_Full_Timestamped_Output_Count",
    "Scenario_With_Partial_Timestamped_Output_Count",
    "Scenario_With_Missing_Timestamped_Output_Count",
    "Regenerated_Scenario_Count",
    "Regeneration_Failed_Scenario_Count",
    "Dominant_Output_Coverage_Class",
    "H4_Timestamped_State_Transition_Readiness_Flag",
    "H4_Timestamped_State_Transition_Diagnostic",
    "Recommended_Follow_Up",
]
FORBIDDEN_REPORT_TERMS = [
    "buy",
    "sell",
    "entry",
    "exit",
    "trade signal",
    "trade setup",
    "take profit",
    "stop loss",
    "profitable",
    "opportunity",
    "predicts",
    "optimal",
    "should trade",
]


def write_review_outputs(result: H4TimestampedStateTransitionResult) -> H4TimestampedStateTransitionResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(
        result.output_dir / "h4_timestamped_state_transition_source_inventory.csv",
        result.source_inventory,
        SOURCE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_timestamped_state_transition_scenario_inventory.csv",
        result.scenario_inventory,
        SCENARIO_COLUMNS,
    )
    _write_rows(result.output_dir / "h4_timestamped_market_states.csv", result.market_state_rows, STATE_COLUMNS)
    _write_rows(
        result.output_dir / "h4_timestamped_state_transitions.csv",
        result.transition_rows,
        TRANSITION_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_timestamped_state_transition_coverage_review.csv",
        result.coverage_review,
        COVERAGE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_timestamped_state_transition_missing_output_review.csv",
        result.missing_output_review,
        MISSING_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_timestamped_state_transition_generation_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4TimestampedStateTransitionResult) -> str:
    lines = [
        "SQRE H4 Timestamped State/Transition Output Generation",
        "======================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        *_input_directory_lines(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        *_row_lines(result.source_inventory, "source_name", "load_status", "diagnostic"),
        "",
        "Scenario Inventory",
        "------------------",
        *_row_lines(result.scenario_inventory, "scenario_id", "scenario_output_coverage_class", "scenario_diagnostic"),
        "",
        "Timestamped Market States",
        "-------------------------",
        f"Rows generated: {len(result.market_state_rows)}",
        "",
        "Timestamped State Transitions",
        "-----------------------------",
        f"Rows generated: {len(result.transition_rows)}",
        "",
        "Coverage Review",
        "---------------",
        *_row_lines(result.coverage_review, "scenario_id", "coverage_class", "coverage_diagnostic"),
        "",
        "Missing Output Review",
        "---------------------",
        *_row_lines(result.missing_output_review, "missing_output_id", "required_source_action", "missing_output_diagnostic"),
        "",
        "Generation Summary",
        "------------------",
        *_summary_lines(result),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        *descriptive_findings(result.summary),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        *[f"- {line}" for line in potential_follow_up_areas()],
        "",
        "Do Not Change Yet",
        "-----------------",
        *[f"- {line}" for line in do_not_change_yet_lines()],
        "",
        "Limitations",
        "-----------",
        *[f"- {line}" for line in limitation_lines()],
        "",
        "Scope Statements",
        "----------------",
        "- This phase generates H4 timestamped state and transition outputs only.",
        "- This phase does not build the final H4 timestamped context table.",
        "- This phase does not align H4 to D1.",
        "- This phase does not perform same-time H4/D1 interpretation.",
        "- Generated timestamps are future alignment keys only.",
        "- H4/D1 same-time review must occur in a later phase.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _input_directory_lines(result: H4TimestampedStateTransitionResult) -> list[str]:
    roots = sorted({str(Path(row.path).parent) for row in result.source_inventory})
    if not roots:
        return ["No input directories were discovered."]
    return [f"- {root}" for root in roots[:12]]


def _summary_lines(result: H4TimestampedStateTransitionResult) -> list[str]:
    if result.summary is None:
        return ["No summary row was produced."]
    summary = result.summary
    return [
        f"Scenario count: {summary.scenario_count}",
        f"Source inventory row count: {summary.source_inventory_row_count}",
        f"Timestamped state row count: {summary.timestamped_state_row_count}",
        f"Timestamped transition row count: {summary.timestamped_transition_row_count}",
        f"Dominant output coverage class: {summary.dominant_output_coverage_class}",
        f"H4 timestamped state transition readiness flag: {summary.h4_timestamped_state_transition_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def _row_lines(rows: list[object], id_attr: str, status_attr: str, diagnostic_attr: str) -> list[str]:
    if not rows:
        return ["No rows available."]
    return [
        f"- {getattr(row, id_attr)}: {getattr(row, status_attr)}; {getattr(row, diagnostic_attr)}"
        for row in rows[:8]
    ]


def _validate_report_text(report_text: str) -> None:
    lowered = report_text.lower()
    for term in FORBIDDEN_REPORT_TERMS:
        if term in lowered:
            raise ValueError(f"Forbidden report term found: {term}")
