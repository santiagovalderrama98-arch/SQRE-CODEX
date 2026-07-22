"""CSV and text report writers for H4 transition/state combined context review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_transition_state_combined_context_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    research_readiness_assessment,
)
from sqre.h4_transition_state_combined_context_review.models import (
    H4TransitionStateCombinedContextReviewResult,
)


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
CONTEXT_COLUMNS = [
    "Context_ID",
    "Symbol",
    "Timeframe",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Forward_Window",
    "State_Profile_Status",
    "Transition_Profile_Status",
    "State_Dispersion_Status",
    "Transition_Dispersion_Status",
    "State_Sensitivity_Status",
    "Transition_Sensitivity_Status",
    "Partial_Context_Status",
    "Context_Inventory_Diagnostic",
]
ALIGNMENT_COLUMNS = [
    "Context_ID",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Forward_Window",
    "State_Readiness_Flag",
    "Transition_Readiness_Flag",
    "State_Dispersion_Class",
    "Transition_Dispersion_Class",
    "State_Transition_Alignment_Class",
    "State_Transition_Alignment_Diagnostic",
]
DISPERSION_COLUMNS = [
    "Context_ID",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Forward_Window",
    "State_Dispersion_Class",
    "Transition_Dispersion_Class",
    "Combined_Dispersion_Class",
    "Combined_Dispersion_Driver",
    "Combined_Dispersion_Diagnostic",
]
SENSITIVITY_COLUMNS = [
    "Context_ID",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Forward_Window",
    "State_Sensitivity_Class",
    "Transition_Sensitivity_Class",
    "Near_Aggregation_Candidate_Flag",
    "Combined_Sensitivity_Class",
    "Combined_Sensitivity_Diagnostic",
]
PARTIAL_COLUMNS = [
    "Context_ID",
    "Partial_Sample_ID",
    "Partial_Sample_Label",
    "Partial_Interpretation_Class",
    "Partial_Readiness_Flag",
    "Partial_Caveat_Class",
    "Partial_Context_Use_Class",
    "Partial_Context_Diagnostic",
]
INTERPRETATION_COLUMNS = [
    "Context_ID",
    "Symbol",
    "Timeframe",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Forward_Window",
    "State_Transition_Alignment_Class",
    "Combined_Dispersion_Class",
    "Combined_Sensitivity_Class",
    "Partial_Context_Use_Class",
    "Combined_Context_Interpretation_Class",
    "Combined_Context_Readiness_Flag",
    "Combined_Context_Diagnostic",
    "Recommended_Follow_Up",
]
SUMMARY_COLUMNS = [
    "Timeframe",
    "Context_Count",
    "Aligned_Scenario_Sensitive_Count",
    "Mixed_Diagnostics_Count",
    "Combined_High_Dispersion_Count",
    "Combined_Sample_Constrained_Count",
    "Combined_Baseline_Unavailable_Count",
    "Combined_Scenario_Sensitive_Count",
    "Descriptively_Stable_Count",
    "Input_Limited_Count",
    "Partial_Context_Limited_Support_Count",
    "Ready_For_Context_Reference_Count",
    "Requires_Scenario_Level_Interpretation_Count",
    "Requires_Sample_Adequacy_Review_Count",
    "Requires_Input_Completeness_Review_Count",
    "Dominant_Combined_Context_Interpretation",
    "H4_Transition_State_Context_Profile",
    "H4_Transition_State_Context_Readiness_Flag",
    "H4_Transition_State_Context_Diagnostic",
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


def write_review_outputs(
    result: H4TransitionStateCombinedContextReviewResult,
) -> H4TransitionStateCombinedContextReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_transition_state_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_rows(result.output_dir / "h4_transition_state_context_inventory.csv", result.context_inventory, CONTEXT_COLUMNS)
    _write_rows(result.output_dir / "h4_state_transition_alignment_review.csv", result.alignment_reviews, ALIGNMENT_COLUMNS)
    _write_rows(result.output_dir / "h4_combined_context_dispersion_review.csv", result.dispersion_reviews, DISPERSION_COLUMNS)
    _write_rows(result.output_dir / "h4_combined_context_sensitivity_review.csv", result.sensitivity_reviews, SENSITIVITY_COLUMNS)
    _write_rows(result.output_dir / "h4_partial_context_caveat_integration.csv", result.partial_caveats, PARTIAL_COLUMNS)
    _write_rows(
        result.output_dir / "h4_transition_state_context_interpretation_matrix.csv",
        result.interpretation_rows,
        INTERPRETATION_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_transition_state_combined_context_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    text = build_report_text(result)
    _validate_report_text(text)
    result.report_path.write_text(text, encoding="utf-8")
    return result


def build_report_text(result: H4TransitionStateCombinedContextReviewResult) -> str:
    lines = [
        "SQRE H4 Transition/State Combined Context Review",
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
        "Combined Context Inventory",
        "--------------------------",
        *_row_lines(result.context_inventory, "context_id", "partial_context_status", "context_inventory_diagnostic"),
        "",
        "State/Transition Alignment Review",
        "---------------------------------",
        *_row_lines(result.alignment_reviews, "context_id", "state_transition_alignment_class", "state_transition_alignment_diagnostic"),
        "",
        "Combined Dispersion Review",
        "--------------------------",
        *_row_lines(result.dispersion_reviews, "context_id", "combined_dispersion_class", "combined_dispersion_diagnostic"),
        "",
        "Combined Sensitivity Review",
        "---------------------------",
        *_row_lines(result.sensitivity_reviews, "context_id", "combined_sensitivity_class", "combined_sensitivity_diagnostic"),
        "",
        "Partial Context Caveat Integration",
        "----------------------------------",
        *_row_lines(result.partial_caveats, "context_id", "partial_context_use_class", "partial_context_diagnostic"),
        "",
        "Combined Context Interpretation Matrix",
        "--------------------------------------",
        *_row_lines(result.interpretation_rows, "context_id", "combined_context_interpretation_class", "combined_context_diagnostic"),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        *research_readiness_assessment(result.summary),
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


def _input_directory_lines(result: H4TransitionStateCombinedContextReviewResult) -> list[str]:
    roots = sorted({str(Path(row.path).parent) for row in result.source_inventory})
    return [f"- {root}" for root in roots]


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _row_lines(rows: list[object], id_attr: str, status_attr: str, diagnostic_attr: str) -> list[str]:
    if not rows:
        return ["No rows available."]
    return [
        f"- {getattr(row, id_attr)}: {getattr(row, status_attr)}; {getattr(row, diagnostic_attr)}"
        for row in rows[:5]
    ]


def _validate_report_text(report_text: str) -> None:
    lowered = report_text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains blocked wording: {', '.join(blocked)}")
