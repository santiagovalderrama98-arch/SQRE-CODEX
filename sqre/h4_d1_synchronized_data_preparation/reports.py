"""Output writers for H4/D1 synchronized historical data preparation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_assessment,
)
from sqre.h4_d1_synchronized_data_preparation.models import H4D1SynchronizedDataPreparationResult


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
H4_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol", "Timeframe", "Source_File", "Normalization_Diagnostic"]
CONTINUITY_COLUMNS = [
    "Symbol",
    "Timeframe",
    "Input_Row_Count",
    "Normalized_Row_Count",
    "Period_Start",
    "Period_End",
    "Parsed_Timestamp_Count",
    "Duplicate_Timestamp_Count",
    "Conflicting_Duplicate_Timestamp_Count",
    "Gap_Count",
    "Large_Gap_Count",
    "Weekend_Gap_Count",
    "Estimated_Missing_H4_Candle_Count",
    "Continuity_Ratio",
    "H4_Continuity_Class",
    "Continuity_Diagnostic",
]
D1_COLUMNS = [
    "Date",
    "D1_Period_Start",
    "D1_Period_End",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Symbol",
    "Timeframe",
    "H4_Candle_Count",
    "Expected_H4_Candle_Count",
    "D1_Candle_Quality_Class",
    "D1_Aggregation_Diagnostic",
]
ALIGNMENT_COLUMNS = [
    "H4_Candle_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Timestamp",
    "H4_Date",
    "H4_Open",
    "H4_High",
    "H4_Low",
    "H4_Close",
    "H4_Volume",
    "D1_Date",
    "D1_Period_Start",
    "D1_Period_End",
    "D1_Open",
    "D1_High",
    "D1_Low",
    "D1_Close",
    "D1_Volume",
    "D1_H4_Candle_Count",
    "H4_D1_Candle_Alignment_Class",
    "Alignment_Diagnostic",
]
SYNC_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Row_Count",
    "D1_Row_Count",
    "Aligned_H4_Row_Count",
    "Unaligned_H4_Row_Count",
    "Full_D1_Candle_Count",
    "Partial_D1_Candle_Count",
    "Low_Coverage_D1_Candle_Count",
    "Continuity_Ratio",
    "Synchronization_Coverage_Ratio",
    "Synchronization_Quality_Class",
    "Synchronization_Diagnostic",
]
MISSING_COLUMNS = [
    "Missing_Data_ID",
    "Missing_Data_Type",
    "Current_Status",
    "Required_Source_Action",
    "Missing_Data_Diagnostic",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Row_Count",
    "D1_Row_Count",
    "Aligned_H4_Row_Count",
    "Unaligned_H4_Row_Count",
    "Full_D1_Candle_Count",
    "Partial_D1_Candle_Count",
    "Low_Coverage_D1_Candle_Count",
    "Continuity_Ratio",
    "Synchronization_Coverage_Ratio",
    "Dominant_Synchronization_Quality_Class",
    "H4_D1_Synchronized_Data_Readiness_Flag",
    "H4_D1_Synchronized_Data_Diagnostic",
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


def write_outputs(result: H4D1SynchronizedDataPreparationResult) -> H4D1SynchronizedDataPreparationResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_d1_synchronized_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "h4_normalized_ohlc.csv", result.h4_frame, H4_COLUMNS)
    _write_rows(result.output_dir / "h4_continuity_review.csv", [result.continuity_review] if result.continuity_review else [], CONTINUITY_COLUMNS)
    _write_frame(result.output_dir / "d1_from_h4_ohlc.csv", result.d1_frame, D1_COLUMNS)
    _write_frame(result.output_dir / "h4_d1_candle_alignment_map.csv", result.alignment_frame, ALIGNMENT_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_synchronization_review.csv", [result.synchronization_review] if result.synchronization_review else [], SYNC_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_missing_data_review.csv", result.missing_data_review, MISSING_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_synchronized_data_summary.csv", [result.summary] if result.summary else [], SUMMARY_COLUMNS)
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4D1SynchronizedDataPreparationResult) -> str:
    lines = [
        "SQRE H4/D1 Synchronized Historical Data Preparation",
        "===================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories / Input Files",
        "-------------------------------",
        *_input_lines(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        *_row_lines(result.source_inventory, "source_name", "load_status", "diagnostic"),
        "",
        "H4 Normalization Summary",
        "------------------------",
        f"H4 rows: {len(result.h4_frame)}",
        "",
        "H4 Continuity Review",
        "--------------------",
        *_continuity_lines(result),
        "",
        "D1 From H4 Aggregation Review",
        "-----------------------------",
        f"D1 rows: {len(result.d1_frame)}",
        "",
        "H4/D1 Candle Alignment Map Review",
        "---------------------------------",
        f"Alignment rows: {len(result.alignment_frame)}",
        "",
        "Synchronization Review",
        "----------------------",
        *_sync_lines(result),
        "",
        "Missing Data Review",
        "-------------------",
        *_row_lines(result.missing_data_review, "missing_data_id", "required_source_action", "missing_data_diagnostic"),
        "",
        "Readiness Assessment",
        "--------------------",
        *readiness_assessment(result.summary),
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
        "- This phase prepares synchronized H4/D1 OHLC data only.",
        "- D1 is derived from H4 by default to preserve temporal consistency.",
        "- H4/D1 candle alignment is data-level alignment only.",
        "- This phase does not generate market states.",
        "- This phase does not generate state transitions.",
        "- This phase does not generate D1 regimes.",
        "- This phase does not perform same-time H4/D1 interpretation.",
        "- Future phases must generate H4 states/transitions and D1 regimes/states from this synchronized base.",
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


def _input_lines(result: H4D1SynchronizedDataPreparationResult) -> list[str]:
    if not result.source_inventory:
        return ["No input sources were reviewed."]
    return [f"- {row.path}" for row in result.source_inventory[:8]]


def _continuity_lines(result: H4D1SynchronizedDataPreparationResult) -> list[str]:
    if result.continuity_review is None:
        return ["No continuity review was produced."]
    row = result.continuity_review
    return [
        f"Continuity ratio: {row.continuity_ratio}",
        f"H4 continuity class: {row.h4_continuity_class}",
        f"Gap count: {row.gap_count}",
        f"Weekend gap count: {row.weekend_gap_count}",
    ]


def _sync_lines(result: H4D1SynchronizedDataPreparationResult) -> list[str]:
    if result.synchronization_review is None:
        return ["No synchronization review was produced."]
    row = result.synchronization_review
    return [
        f"Synchronization coverage ratio: {row.synchronization_coverage_ratio}",
        f"Synchronization quality class: {row.synchronization_quality_class}",
        f"Aligned H4 rows: {row.aligned_h4_row_count}",
        f"Unaligned H4 rows: {row.unaligned_h4_row_count}",
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
