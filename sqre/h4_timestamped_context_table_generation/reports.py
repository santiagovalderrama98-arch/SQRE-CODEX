"""Output writers for H4 timestamped context table generation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_context_table_generation.findings import (
    descriptive_findings,
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.h4_timestamped_context_table_generation.models import H4TimestampedContextGenerationResult


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
    "OHLC_File",
    "Scenario_Status",
    "States_Generated",
    "Transitions_Generated",
    "Timestamped_State_Source_Available",
    "Timestamped_Transition_Source_Available",
    "Timestamped_Context_Row_Count",
    "Scenario_Context_Coverage_Class",
    "Scenario_Diagnostic",
]
CONTEXT_COLUMNS = [
    "H4_Timestamped_Context_ID",
    "Aggregate_Context_ID",
    "Symbol",
    "Timeframe",
    "Scenario_ID",
    "Scenario_Period_Start",
    "Scenario_Period_End",
    "H4_Event_Time",
    "H4_Event_Date",
    "H4_Source_State",
    "H4_Target_State",
    "H4_Transition_Label",
    "H4_Forward_Window",
    "H4_Temporal_Key_Class",
    "H4_D1_Alignment_Date_Key",
    "Aggregate_Context_Match_Method",
    "Aggregate_Context_Match_Confidence",
    "Context_Row_Diagnostic",
]
COVERAGE_COLUMNS = [
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Period_Start",
    "Period_End",
    "Expected_Transition_Count",
    "Timestamped_Context_Row_Count",
    "Aggregate_Context_Matched_Row_Count",
    "Aggregate_Context_Unmatched_Row_Count",
    "Temporal_Key_Complete_Row_Count",
    "Temporal_Key_Incomplete_Row_Count",
    "Coverage_Ratio",
    "Coverage_Class",
    "Coverage_Diagnostic",
]
MISSING_COLUMNS = [
    "Missing_Context_ID",
    "Scenario_ID",
    "Missing_Source_Type",
    "Missing_Source_Diagnostic",
    "Required_Source_Action",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "Timeframe",
    "Scenario_Count",
    "Timestamped_Source_Count",
    "Timestamped_Context_Row_Count",
    "Aggregate_Context_Matched_Row_Count",
    "Aggregate_Context_Unmatched_Row_Count",
    "Temporal_Key_Complete_Row_Count",
    "Temporal_Key_Incomplete_Row_Count",
    "Full_Coverage_Scenario_Count",
    "Partial_Coverage_Scenario_Count",
    "Low_Coverage_Scenario_Count",
    "Missing_Coverage_Scenario_Count",
    "Dominant_Coverage_Class",
    "H4_Timestamped_Context_Readiness_Flag",
    "H4_Timestamped_Context_Diagnostic",
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


def write_review_outputs(result: H4TimestampedContextGenerationResult) -> H4TimestampedContextGenerationResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_timestamped_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_rows(result.output_dir / "h4_timestamped_scenario_inventory.csv", result.scenario_inventory, SCENARIO_COLUMNS)
    _write_rows(result.output_dir / "h4_timestamped_context_rows.csv", result.context_rows, CONTEXT_COLUMNS)
    _write_rows(result.output_dir / "h4_timestamped_context_coverage_review.csv", result.coverage_review, COVERAGE_COLUMNS)
    _write_rows(result.output_dir / "h4_timestamped_missing_context_review.csv", result.missing_context_review, MISSING_COLUMNS)
    _write_rows(
        result.output_dir / "h4_timestamped_context_generation_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4TimestampedContextGenerationResult) -> str:
    lines = [
        "SQRE H4 Timestamped Context Table Generation",
        "============================================",
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
        *_row_lines(result.scenario_inventory, "scenario_id", "scenario_context_coverage_class", "scenario_diagnostic"),
        "",
        "Timestamped Context Rows",
        "------------------------",
        f"Rows generated: {len(result.context_rows)}",
        "",
        "Coverage Review",
        "---------------",
        *_row_lines(result.coverage_review, "scenario_id", "coverage_class", "coverage_diagnostic"),
        "",
        "Missing Context Review",
        "----------------------",
        *_row_lines(result.missing_context_review, "missing_context_id", "required_source_action", "missing_source_diagnostic"),
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
        "- This phase generates H4 timestamped context rows only.",
        "- This phase does not align H4 to D1 yet.",
        "- This phase does not perform same-time H4/D1 interpretation.",
        "- H4_D1_Alignment_Date_Key is only a future alignment key.",
        "- Same-time H4/D1 comparison must be performed in a later phase.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _input_directory_lines(result: H4TimestampedContextGenerationResult) -> list[str]:
    roots = sorted({str(Path(row.path).parent) for row in result.source_inventory})
    if not roots:
        return ["No input directories were discovered."]
    return [f"- {root}" for root in roots[:12]]


def _summary_lines(result: H4TimestampedContextGenerationResult) -> list[str]:
    if result.summary is None:
        return ["No summary row was produced."]
    summary = result.summary
    return [
        f"Scenario count: {summary.scenario_count}",
        f"Timestamped source count: {summary.timestamped_source_count}",
        f"Timestamped context row count: {summary.timestamped_context_row_count}",
        f"Dominant coverage class: {summary.dominant_coverage_class}",
        f"H4 timestamped context readiness flag: {summary.h4_timestamped_context_readiness_flag}",
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
