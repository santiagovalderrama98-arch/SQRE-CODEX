"""Output writers for timestamped H4/D1 state and regime generation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.timestamped_h4_d1_state_regime_generation.d1_state_regime_table_builder import D1_STATE_COLUMNS
from sqre.timestamped_h4_d1_state_regime_generation.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_lines,
)
from sqre.timestamped_h4_d1_state_regime_generation.h4_state_table_builder import H4_STATE_COLUMNS
from sqre.timestamped_h4_d1_state_regime_generation.h4_transition_table_builder import H4_TRANSITION_COLUMNS
from sqre.timestamped_h4_d1_state_regime_generation.models import TimestampedH4D1StateRegimeGenerationResult


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
COVERAGE_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Input_Row_Count",
    "D1_Input_Row_Count",
    "H4_State_Row_Count",
    "H4_Transition_Row_Count",
    "D1_State_Row_Count",
    "H4_State_Coverage_Class",
    "H4_Transition_Coverage_Class",
    "D1_State_Coverage_Class",
    "Coverage_Diagnostic",
]
MISSING_COLUMNS = [
    "Missing_Output_ID",
    "Missing_Output_Type",
    "Current_Status",
    "Required_Source_Action",
    "Missing_Output_Diagnostic",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Input_Row_Count",
    "D1_Input_Row_Count",
    "H4_State_Row_Count",
    "H4_Transition_Row_Count",
    "D1_State_Row_Count",
    "Dominant_Generation_Coverage_Class",
    "Timestamped_H4_D1_State_Regime_Readiness_Flag",
    "Timestamped_H4_D1_State_Regime_Diagnostic",
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


def write_outputs(result: TimestampedH4D1StateRegimeGenerationResult) -> TimestampedH4D1StateRegimeGenerationResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "timestamped_h4_d1_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "timestamped_h4_market_states.csv", result.h4_states, H4_STATE_COLUMNS)
    _write_frame(result.output_dir / "timestamped_h4_state_transitions.csv", result.h4_transitions, H4_TRANSITION_COLUMNS)
    _write_frame(result.output_dir / "timestamped_d1_market_states.csv", result.d1_states, D1_STATE_COLUMNS)
    _write_rows(
        result.output_dir / "timestamped_h4_d1_generation_coverage_review.csv",
        [result.coverage_review] if result.coverage_review else [],
        COVERAGE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "timestamped_h4_d1_missing_output_review.csv",
        result.missing_output_review,
        MISSING_COLUMNS,
    )
    _write_rows(
        result.output_dir / "timestamped_h4_d1_state_regime_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: TimestampedH4D1StateRegimeGenerationResult) -> str:
    lines = [
        "SQRE Timestamped H4/D1 State & Regime Table Generation",
        "=======================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directory",
        "---------------",
        _input_directory(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        *_row_lines(result.source_inventory, "source_name", "load_status", "diagnostic"),
        "",
        "H4 Timestamped Market States",
        "----------------------------",
        f"Rows generated: {len(result.h4_states)}",
        "",
        "H4 Timestamped State Transitions",
        "-------------------------------",
        f"Rows generated: {len(result.h4_transitions)}",
        "",
        "D1 Timestamped Market States / Regimes",
        "--------------------------------------",
        f"Rows generated: {len(result.d1_states)}",
        "",
        "Coverage Review",
        "---------------",
        *_coverage_lines(result),
        "",
        "Missing Output Review",
        "---------------------",
        *_row_lines(result.missing_output_review, "missing_output_id", "required_source_action", "missing_output_diagnostic"),
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
        "- This phase generates timestamped H4/D1 state/regime tables only.",
        "- This phase does not perform H4/D1 same-time alignment.",
        "- This phase does not perform H4/D1 contextual interpretation.",
        "- This phase does not generate trading signals.",
        "- Generated timestamps are future alignment keys only.",
        "- Same-time H4/D1 review must occur in a later phase.",
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
    lines: list[str] = []
    for row in rows[:10]:
        lines.append(
            f"- {getattr(row, id_field)}: {getattr(row, status_field)}; {getattr(row, diagnostic_field)}"
        )
    return lines


def _coverage_lines(result: TimestampedH4D1StateRegimeGenerationResult) -> list[str]:
    if result.coverage_review is None:
        return ["No coverage review was produced."]
    row = result.coverage_review
    return [
        f"H4 input rows: {row.h4_input_row_count}",
        f"D1 input rows: {row.d1_input_row_count}",
        f"H4 state rows: {row.h4_state_row_count}",
        f"H4 transition rows: {row.h4_transition_row_count}",
        f"D1 state rows: {row.d1_state_row_count}",
        f"H4 state coverage class: {row.h4_state_coverage_class}",
        f"H4 transition coverage class: {row.h4_transition_coverage_class}",
        f"D1 state coverage class: {row.d1_state_coverage_class}",
        f"Diagnostic: {row.coverage_diagnostic}",
    ]


def _input_directory(result: TimestampedH4D1StateRegimeGenerationResult) -> str:
    if not result.source_inventory:
        return "No synchronized input directory was reviewed."
    first_path = Path(result.source_inventory[0].path)
    return str(first_path.parent)


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains forbidden wording: {blocked}")
