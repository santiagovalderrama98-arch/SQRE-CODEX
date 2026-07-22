"""CSV and text report writers for H4/D1 contextual transition review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_contextual_transition_review.findings import (
    descriptive_findings,
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.h4_d1_contextual_transition_review.models import H4D1ContextualTransitionReviewResult


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
MAP_COLUMNS = [
    "Scenario_Context_ID",
    "Symbol",
    "H4_Scenario_ID",
    "D1_Scenario_ID",
    "D1_Regime_Label",
    "D1_Context_Label",
    "Mapping_Method",
    "Mapping_Confidence_Class",
    "Mapping_Diagnostic",
]
CONTEXT_COLUMNS = [
    "Context_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Source_State",
    "H4_Target_State",
    "H4_Transition_Label",
    "H4_Forward_Window",
    "H4_Context_Interpretation_Class",
    "H4_Context_Readiness_Flag",
    "D1_Regime_Label",
    "D1_Context_Status",
    "D1_Sample_Adequacy_Class",
    "D1_Dispersion_Class",
    "Partial_Context_Status",
    "Context_Inventory_Diagnostic",
]
REGIME_COLUMNS = [
    "Context_ID",
    "D1_Regime_Label",
    "D1_Context_Status",
    "D1_Regime_Count",
    "D1_Sample_Adequacy_Class",
    "D1_Dispersion_Class",
    "D1_Regime_Sensitivity_Class",
    "D1_Context_Interpretation_Class",
    "D1_Context_Diagnostic",
]
ALIGNMENT_COLUMNS = [
    "Context_ID",
    "H4_Source_State",
    "H4_Target_State",
    "H4_Transition_Label",
    "H4_Forward_Window",
    "H4_Context_Interpretation_Class",
    "H4_Context_Readiness_Flag",
    "D1_Context_Interpretation_Class",
    "D1_Regime_Label",
    "H4_D1_Alignment_Class",
    "H4_D1_Alignment_Diagnostic",
]
DISPERSION_COLUMNS = [
    "Context_ID",
    "H4_Transition_Label",
    "H4_Forward_Window",
    "H4_Combined_Dispersion_Class",
    "D1_Dispersion_Class",
    "D1_Regime_Label",
    "Contextual_Dispersion_Class",
    "Contextual_Dispersion_Driver",
    "Contextual_Dispersion_Diagnostic",
]
SENSITIVITY_COLUMNS = [
    "Context_ID",
    "H4_Combined_Sensitivity_Class",
    "D1_Regime_Sensitivity_Class",
    "D1_Regime_Label",
    "Contextual_Sensitivity_Class",
    "Contextual_Sensitivity_Diagnostic",
]
PARTIAL_COLUMNS = [
    "Context_ID",
    "Partial_Sample_ID",
    "Partial_Sample_Label",
    "Partial_Interpretation_Class",
    "Partial_Readiness_Flag",
    "Partial_Context_Use_Class",
    "H4_D1_Partial_Use_Class",
    "Partial_Context_Diagnostic",
]
INTERPRETATION_COLUMNS = [
    "Context_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Source_State",
    "H4_Target_State",
    "H4_Transition_Label",
    "H4_Forward_Window",
    "D1_Regime_Label",
    "H4_D1_Alignment_Class",
    "Contextual_Dispersion_Class",
    "Contextual_Sensitivity_Class",
    "H4_D1_Partial_Use_Class",
    "H4_D1_Contextual_Interpretation_Class",
    "H4_D1_Contextual_Readiness_Flag",
    "H4_D1_Contextual_Diagnostic",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Context_Count",
    "Mapped_Context_Count",
    "Unmapped_Context_Count",
    "D1_Regime_Count",
    "D1_Context_Reinforces_H4_Dispersion_Count",
    "D1_Context_Segments_H4_Dispersion_Count",
    "D1_Context_Does_Not_Reduce_H4_Dispersion_Count",
    "D1_Reinforces_H4_Scenario_Sensitivity_Count",
    "D1_Contextualizes_H4_Scenario_Sensitivity_Count",
    "Input_Limited_Count",
    "Sample_Constrained_Count",
    "Ready_For_Contextual_Reference_Count",
    "Requires_Scenario_And_Regime_Interpretation_Count",
    "Requires_Sample_Adequacy_Review_Count",
    "Requires_Input_Completeness_Review_Count",
    "Dominant_H4_D1_Contextual_Interpretation",
    "H4_D1_Contextual_Profile",
    "H4_D1_Contextual_Readiness_Flag",
    "H4_D1_Contextual_Diagnostic",
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
    "edge",
    "best timeframe",
    "ranking",
    "should trade",
    "predicts",
    "optimal",
]


def write_review_outputs(result: H4D1ContextualTransitionReviewResult) -> H4D1ContextualTransitionReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_d1_context_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_scenario_context_map.csv", result.scenario_context_map, MAP_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_context_inventory.csv", result.context_inventory, CONTEXT_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_regime_context_review.csv", result.regime_reviews, REGIME_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_alignment_review.csv", result.alignment_reviews, ALIGNMENT_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_contextual_dispersion_review.csv", result.dispersion_reviews, DISPERSION_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_contextual_sensitivity_review.csv", result.sensitivity_reviews, SENSITIVITY_COLUMNS)
    _write_rows(result.output_dir / "h4_d1_partial_context_integration.csv", result.partial_integrations, PARTIAL_COLUMNS)
    _write_rows(
        result.output_dir / "h4_d1_contextual_interpretation_matrix.csv",
        result.interpretation_rows,
        INTERPRETATION_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_contextual_transition_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4D1ContextualTransitionReviewResult) -> str:
    lines = [
        "SQRE H4/D1 Contextual Transition Review",
        "=======================================",
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
        "H4/D1 Scenario Context Map",
        "--------------------------",
        *_row_lines(result.scenario_context_map, "scenario_context_id", "mapping_confidence_class", "mapping_diagnostic"),
        "",
        "H4/D1 Context Inventory",
        "-----------------------",
        *_row_lines(result.context_inventory, "context_id", "d1_context_status", "context_inventory_diagnostic"),
        "",
        "D1 Regime Context Review",
        "------------------------",
        *_row_lines(result.regime_reviews, "context_id", "d1_context_interpretation_class", "d1_context_diagnostic"),
        "",
        "H4/D1 Alignment Review",
        "----------------------",
        *_row_lines(result.alignment_reviews, "context_id", "h4_d1_alignment_class", "h4_d1_alignment_diagnostic"),
        "",
        "Contextual Dispersion Review",
        "----------------------------",
        *_row_lines(result.dispersion_reviews, "context_id", "contextual_dispersion_class", "contextual_dispersion_diagnostic"),
        "",
        "Contextual Sensitivity Review",
        "-----------------------------",
        *_row_lines(result.sensitivity_reviews, "context_id", "contextual_sensitivity_class", "contextual_sensitivity_diagnostic"),
        "",
        "Partial Context Integration",
        "---------------------------",
        *_row_lines(result.partial_integrations, "context_id", "h4_d1_partial_use_class", "partial_context_diagnostic"),
        "",
        "H4/D1 Contextual Interpretation Matrix",
        "--------------------------------------",
        *_row_lines(result.interpretation_rows, "context_id", "h4_d1_contextual_interpretation_class", "h4_d1_contextual_diagnostic"),
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


def _input_directory_lines(result: H4D1ContextualTransitionReviewResult) -> list[str]:
    roots = sorted({str(Path(row.path).parent) for row in result.source_inventory})
    return [f"- {root}" for root in roots]


def _row_lines(rows: list[object], id_attr: str, status_attr: str, diagnostic_attr: str) -> list[str]:
    if not rows:
        return ["No rows available."]
    return [
        f"- {getattr(row, id_attr)}: {getattr(row, status_attr)}; {getattr(row, diagnostic_attr)}"
        for row in rows[:5]
    ]


def _validate_report_text(report_text: str) -> None:
    lowered = report_text.lower()
    for term in FORBIDDEN_REPORT_TERMS:
        if term in lowered:
            raise ValueError(f"Forbidden report term found: {term}")
