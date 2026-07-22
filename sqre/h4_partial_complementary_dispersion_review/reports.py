"""CSV and text report writers for H4 partial complementary review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_partial_complementary_dispersion_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    research_readiness_assessment,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    H4PartialComplementaryDispersionReviewResult,
)


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SAMPLE_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Coverage_Ratio",
    "Run_Status",
    "Sample_Adequacy_Class",
    "Partial_Comparison_Class",
    "Condition_Profile_Count",
    "Partial_Sample_Status",
    "Partial_Sample_Diagnostic",
]
STATE_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Partial_State_Profile",
    "Partial_Unique_State_Count",
    "Partial_Most_Common_State",
    "Baseline_State_Dispersion_Profile",
    "Baseline_State_Readiness_Flag",
    "Partial_State_Consistency_Class",
    "Partial_State_Diagnostic",
]
TRANSITION_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Partial_Most_Common_Transition",
    "Partial_Unique_Transition_Count",
    "Baseline_Transition_Dispersion_Profile",
    "Baseline_Transition_Readiness_Flag",
    "Partial_Transition_Consistency_Class",
    "Partial_Transition_Diagnostic",
]
SENSITIVITY_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Baseline_Scenario_Sensitive_Profile",
    "Baseline_High_Sensitivity_Profile_Count",
    "Baseline_Near_Aggregation_Candidate_Count",
    "Partial_Comparison_Class",
    "Partial_Condition_Profile_Count",
    "Partial_Sensitivity_Interpretation",
    "Partial_Sensitivity_Diagnostic",
]
INTERPRETATION_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Baseline_Scenario_Count",
    "Coverage_Ratio",
    "Condition_Profile_Count",
    "Sample_Adequacy_Class",
    "Partial_Comparison_Class",
    "State_Consistency_Class",
    "Transition_Consistency_Class",
    "Sensitivity_Interpretation",
    "Partial_Baseline_Interpretation_Class",
    "Partial_Baseline_Interpretation_Diagnostic",
    "Recommended_Follow_Up",
]
CAVEAT_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Coverage_Ratio",
    "Baseline_Scenario_Count",
    "Partial_Sample_Caveat_Class",
    "Partial_Sample_Caveat_Diagnostic",
]
SUMMARY_COLUMNS = [
    "Timeframe",
    "Candidate_Count",
    "Reviewed_Partial_Sample_Count",
    "Complementary_Support_Count",
    "Consistent_But_Limited_Count",
    "Divergent_Count",
    "Inconclusive_Count",
    "Unavailable_Count",
    "Baseline_Scenario_Count",
    "Average_Coverage_Ratio",
    "Average_Condition_Profile_Count",
    "Dominant_Partial_Baseline_Interpretation",
    "H4_Partial_Complementary_Profile",
    "H4_Partial_Complementary_Readiness_Flag",
    "H4_Partial_Complementary_Diagnostic",
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
    result: H4PartialComplementaryDispersionReviewResult,
) -> H4PartialComplementaryDispersionReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_partial_complement_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_rows(result.output_dir / "h4_partial_sample_review_inventory.csv", result.partial_samples, SAMPLE_COLUMNS)
    _write_rows(result.output_dir / "h4_partial_state_complement_review.csv", result.state_reviews, STATE_COLUMNS)
    _write_rows(
        result.output_dir / "h4_partial_transition_complement_review.csv",
        result.transition_reviews,
        TRANSITION_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_partial_sensitivity_complement_review.csv",
        result.sensitivity_reviews,
        SENSITIVITY_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_partial_baseline_interpretation_matrix.csv",
        result.interpretation_rows,
        INTERPRETATION_COLUMNS,
    )
    _write_rows(result.output_dir / "h4_partial_sample_caveat_review.csv", result.caveat_rows, CAVEAT_COLUMNS)
    _write_rows(
        result.output_dir / "h4_partial_complementary_dispersion_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4PartialComplementaryDispersionReviewResult) -> str:
    lines = [
        "SQRE H4 Partial Sample Complementary Dispersion Review",
        "=====================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        f"Partial validation directory: {result.partial_validation_dir}",
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        f"Source rows: {len(result.source_inventory)}",
        *_row_lines(result.source_inventory, "source_name", "load_status", "diagnostic"),
        "",
        "Partial Sample Review Inventory",
        "-------------------------------",
        *_row_lines(result.partial_samples, "candidate_id", "partial_sample_status", "partial_sample_diagnostic"),
        "",
        "State Complement Review",
        "-----------------------",
        *_row_lines(result.state_reviews, "candidate_id", "partial_state_consistency_class", "partial_state_diagnostic"),
        "",
        "Transition Complement Review",
        "----------------------------",
        *_row_lines(
            result.transition_reviews,
            "candidate_id",
            "partial_transition_consistency_class",
            "partial_transition_diagnostic",
        ),
        "",
        "Sensitivity Complement Review",
        "-----------------------------",
        *_row_lines(
            result.sensitivity_reviews,
            "candidate_id",
            "partial_sensitivity_interpretation",
            "partial_sensitivity_diagnostic",
        ),
        "",
        "Partial Baseline Interpretation Matrix",
        "--------------------------------------",
        *_row_lines(
            result.interpretation_rows,
            "candidate_id",
            "partial_baseline_interpretation_class",
            "partial_baseline_interpretation_diagnostic",
        ),
        "",
        "Partial Sample Caveat Review",
        "----------------------------",
        *_row_lines(result.caveat_rows, "candidate_id", "partial_sample_caveat_class", "partial_sample_caveat_diagnostic"),
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


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _row_lines(rows: list[object], id_attr: str, status_attr: str, diagnostic_attr: str) -> list[str]:
    if not rows:
        return ["No rows available."]
    output = []
    for row in rows[:5]:
        output.append(f"- {getattr(row, id_attr)}: {getattr(row, status_attr)}; {getattr(row, diagnostic_attr)}")
    return output


def _validate_report_text(report_text: str) -> None:
    lowered = report_text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains blocked wording: {', '.join(blocked)}")
