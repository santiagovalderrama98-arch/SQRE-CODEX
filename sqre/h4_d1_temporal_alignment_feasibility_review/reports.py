"""CSV and text report writers for H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_temporal_alignment_feasibility_review.findings import (
    descriptive_findings,
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.h4_d1_temporal_alignment_feasibility_review.models import TemporalAlignmentFeasibilityResult


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
KEY_COLUMNS = [
    "Source_Name",
    "Source_Type",
    "File_Name",
    "Rows_Loaded",
    "Timestamp_Columns",
    "Start_Time_Columns",
    "End_Time_Columns",
    "Scenario_ID_Columns",
    "Timeframe_Columns",
    "Condition_Only_Columns",
    "Regime_Columns",
    "Temporal_Key_Status",
    "Temporal_Key_Diagnostic",
]
CANDIDATE_COLUMNS = [
    "Candidate_ID",
    "H4_Source_Name",
    "D1_Source_Name",
    "H4_Key_Status",
    "D1_Key_Status",
    "Potential_Alignment_Method",
    "Alignment_Feasibility_Class",
    "Alignment_Confidence_Class",
    "Candidate_Diagnostic",
]
MISSING_COLUMNS = [
    "Missing_Key_ID",
    "Source_Name",
    "Source_Type",
    "Missing_Key_Type",
    "Current_Key_Status",
    "Required_Key_For_Same_Time_Alignment",
    "Required_Source_Action",
    "Missing_Key_Diagnostic",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Source_Count",
    "Loaded_Source_Count",
    "H4_Source_Count",
    "D1_Source_Count",
    "Sources_With_Exact_Timestamp_Count",
    "Sources_With_Start_End_Time_Count",
    "Sources_With_Scenario_Period_Key_Count",
    "Sources_With_Condition_Only_Key_Count",
    "H4_Temporal_Key_Status",
    "D1_Temporal_Key_Status",
    "Candidate_Count",
    "Ready_Exact_Timestamp_Candidate_Count",
    "Ready_Interval_Overlap_Candidate_Count",
    "Ready_Scenario_Period_Candidate_Count",
    "Condition_Only_Not_Temporal_Candidate_Count",
    "Input_Limited_Candidate_Count",
    "Dominant_Alignment_Feasibility_Class",
    "Temporal_Alignment_Readiness_Flag",
    "Temporal_Alignment_Diagnostic",
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


def write_review_outputs(result: TemporalAlignmentFeasibilityResult) -> TemporalAlignmentFeasibilityResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_d1_temporal_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_temporal_key_inventory.csv", result.temporal_key_inventory, KEY_COLUMNS)
    _write_rows(
        result.output_dir / "h4_d1_temporal_alignment_candidate_review.csv",
        result.alignment_candidates,
        CANDIDATE_COLUMNS,
    )
    _write_rows(result.output_dir / "h4_d1_missing_temporal_keys_review.csv", result.missing_keys, MISSING_COLUMNS)
    _write_rows(
        result.output_dir / "h4_d1_temporal_alignment_feasibility_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: TemporalAlignmentFeasibilityResult) -> str:
    lines = [
        "SQRE H4/D1 Temporal Alignment Feasibility Review",
        "================================================",
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
        "Temporal Key Inventory",
        "----------------------",
        *_row_lines(result.temporal_key_inventory, "source_name", "temporal_key_status", "temporal_key_diagnostic"),
        "",
        "Alignment Candidate Review",
        "--------------------------",
        *_row_lines(result.alignment_candidates, "candidate_id", "alignment_feasibility_class", "candidate_diagnostic"),
        "",
        "Missing Temporal Keys Review",
        "----------------------------",
        *_row_lines(result.missing_keys, "missing_key_id", "required_source_action", "missing_key_diagnostic"),
        "",
        "Feasibility Summary",
        "-------------------",
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
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _input_directory_lines(result: TemporalAlignmentFeasibilityResult) -> list[str]:
    roots = sorted({str(Path(row.path).parent) for row in result.source_inventory})
    return [f"- {root}" for root in roots]


def _summary_lines(result: TemporalAlignmentFeasibilityResult) -> list[str]:
    if result.summary is None:
        return ["No summary row was produced."]
    summary = result.summary
    return [
        f"Source count: {summary.source_count}",
        f"Loaded source count: {summary.loaded_source_count}",
        f"H4 temporal key status: {summary.h4_temporal_key_status}",
        f"D1 temporal key status: {summary.d1_temporal_key_status}",
        f"Candidate count: {summary.candidate_count}",
        f"Dominant alignment feasibility class: {summary.dominant_alignment_feasibility_class}",
        f"Temporal alignment readiness flag: {summary.temporal_alignment_readiness_flag}",
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
