"""Output writers for H4/D1 same-time alignment."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_same_time_alignment_table.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_lines,
)
from sqre.h4_d1_same_time_alignment_table.h4_state_alignment_builder import STATE_ALIGNMENT_COLUMNS
from sqre.h4_d1_same_time_alignment_table.h4_transition_alignment_builder import TRANSITION_ALIGNMENT_COLUMNS
from sqre.h4_d1_same_time_alignment_table.models import H4D1SameTimeAlignmentResult


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
COVERAGE_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Row_Count",
    "Aligned_H4_Transition_Row_Count",
    "Unaligned_H4_Transition_Row_Count",
    "H4_State_Row_Count",
    "Aligned_H4_State_Row_Count",
    "Unaligned_H4_State_Row_Count",
    "D1_State_Row_Count",
    "Transition_Alignment_Ratio",
    "State_Alignment_Ratio",
    "Transition_Alignment_Coverage_Class",
    "State_Alignment_Coverage_Class",
    "Overall_Alignment_Coverage_Class",
    "Coverage_Diagnostic",
]
UNMATCHED_COLUMNS = [
    "Unmatched_ID",
    "Unmatched_Source_Type",
    "H4_Source_ID",
    "H4_Timestamp",
    "H4_Date",
    "Missing_Match_Type",
    "Current_Status",
    "Required_Source_Action",
    "Unmatched_Diagnostic",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Row_Count",
    "Aligned_H4_Transition_Row_Count",
    "Unaligned_H4_Transition_Row_Count",
    "H4_State_Row_Count",
    "Aligned_H4_State_Row_Count",
    "Unaligned_H4_State_Row_Count",
    "D1_State_Row_Count",
    "Transition_Alignment_Ratio",
    "State_Alignment_Ratio",
    "Dominant_Alignment_Coverage_Class",
    "H4_D1_Same_Time_Alignment_Readiness_Flag",
    "H4_D1_Same_Time_Alignment_Diagnostic",
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


def write_outputs(result: H4D1SameTimeAlignmentResult) -> H4D1SameTimeAlignmentResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_d1_same_time_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(
        result.output_dir / "h4_transition_d1_same_time_alignment.csv",
        result.transition_alignment,
        TRANSITION_ALIGNMENT_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_state_d1_same_time_alignment.csv",
        result.state_alignment,
        STATE_ALIGNMENT_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_same_time_alignment_coverage_review.csv",
        [result.coverage_review] if result.coverage_review else [],
        COVERAGE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_unmatched_alignment_review.csv",
        result.unmatched_review,
        UNMATCHED_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_same_time_alignment_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4D1SameTimeAlignmentResult) -> str:
    lines = [
        "SQRE H4/D1 Same-Time Alignment Table",
        "====================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        *_input_directories(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        *_row_lines(result.source_inventory, "source_name", "load_status", "diagnostic"),
        "",
        "H4 Transition to D1 Same-Time Alignment",
        "---------------------------------------",
        f"Rows generated: {len(result.transition_alignment)}",
        "",
        "H4 State to D1 Same-Time Alignment",
        "----------------------------------",
        f"Rows generated: {len(result.state_alignment)}",
        "",
        "Alignment Coverage Review",
        "-------------------------",
        *_coverage_lines(result),
        "",
        "Unmatched Alignment Review",
        "--------------------------",
        *_row_lines(result.unmatched_review, "unmatched_id", "required_source_action", "unmatched_diagnostic"),
        "",
        "Readiness Assessment",
        "--------------------",
        *readiness_lines(result.summary),
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
        "- This phase builds same-time alignment tables only.",
        "- This phase aligns H4 timestamps to contemporaneous D1 state/regime context.",
        "- This phase does not interpret the meaning of aligned H4/D1 contexts.",
        "- This phase does not generate trading signals.",
        "- This phase does not produce operational decisions.",
        "- Later phases may review historical outcomes by aligned context, but this phase does not.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows if row is not None]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _write_frame(path: Path, frame: pd.DataFrame, columns: list[str]) -> None:
    if frame.empty:
        pd.DataFrame(columns=columns).to_csv(path, index=False)
        return
    frame.reindex(columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _row_lines(rows: list[object], id_field: str, status_field: str, diagnostic_field: str) -> list[str]:
    if not rows:
        return ["No rows were produced."]
    return [f"- {getattr(row, id_field)}: {getattr(row, status_field)}; {getattr(row, diagnostic_field)}" for row in rows[:10]]


def _coverage_lines(result: H4D1SameTimeAlignmentResult) -> list[str]:
    if result.coverage_review is None:
        return ["No alignment coverage review was produced."]
    row = result.coverage_review
    return [
        f"H4 transition rows: {row.h4_transition_row_count}",
        f"Aligned H4 transition rows: {row.aligned_h4_transition_row_count}",
        f"Unaligned H4 transition rows: {row.unaligned_h4_transition_row_count}",
        f"H4 state rows: {row.h4_state_row_count}",
        f"Aligned H4 state rows: {row.aligned_h4_state_row_count}",
        f"Unaligned H4 state rows: {row.unaligned_h4_state_row_count}",
        f"D1 state rows: {row.d1_state_row_count}",
        f"Transition alignment ratio: {row.transition_alignment_ratio}",
        f"State alignment ratio: {row.state_alignment_ratio}",
        f"Overall alignment coverage class: {row.overall_alignment_coverage_class}",
        f"Diagnostic: {row.coverage_diagnostic}",
    ]


def _input_directories(result: H4D1SameTimeAlignmentResult) -> list[str]:
    if not result.source_inventory:
        return ["No input directories were reviewed."]
    parents = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents]


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains forbidden wording: {blocked}")
