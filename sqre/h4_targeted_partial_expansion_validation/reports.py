"""Output writers for H4 targeted partial expansion validation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    research_readiness_assessment,
)
from sqre.h4_targeted_partial_expansion_validation.models import H4TargetedPartialExpansionResult


CANDIDATE_COLUMNS = [
    "Candidate_ID",
    "Symbol",
    "Timeframe",
    "Sample_Label",
    "Feasibility_Class",
    "Coverage_Ratio",
    "Raw_File_Path",
    "Raw_File_Status",
    "Defined_Start_Date",
    "Defined_End_Date",
    "Actual_Start_Date",
    "Actual_End_Date",
    "Candidate_Selection_Status",
    "Candidate_Diagnostic",
]

RUN_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Run_Status",
    "Event_Detection_Status",
    "Market_Structure_Status",
    "Market_States_Status",
    "Transition_Engine_Status",
    "Research_Engine_Status",
    "Price_Outcome_Status",
    "OHLC_Rows",
    "Event_Count",
    "Structure_Count",
    "State_Count",
    "Transition_Count",
    "Condition_Profile_Count",
    "Run_Diagnostic",
]

STRUCTURE_STATE_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "OHLC_Rows",
    "Structure_Count",
    "Average_Structure_Duration",
    "Average_Structure_Range_Pips",
    "Unique_State_Count",
    "Most_Common_State",
    "State_Diversity_Profile",
    "Structure_State_Diagnostic",
]

TRANSITION_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Transition_Count",
    "Unique_Transition_Count",
    "Most_Common_Transition",
    "Directional_To_Directional_Count",
    "Directional_To_Rotation_Count",
    "Rotation_To_Directional_Count",
    "Sample_Transition_Diagnostic",
]

PRICE_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Condition_Profile_Count",
    "Research_Ready_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "Scenario_Sensitive_Profile_Count",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Price_Outcome_Diagnostic",
]

COMPARISON_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Baseline_Scenario_Count",
    "Partial_OHLC_Rows",
    "Baseline_Average_OHLC_Rows",
    "Partial_Structure_Count",
    "Baseline_Average_Structure_Count",
    "Structure_Count_vs_Baseline_Ratio",
    "Partial_State_Count",
    "Baseline_Average_State_Count",
    "Partial_Transition_Count",
    "Baseline_Average_Transition_Count",
    "Partial_Average_Forward_Range_Pips",
    "Baseline_Average_Forward_Range_Pips",
    "Forward_Range_vs_Baseline_Ratio",
    "Partial_Average_Outcome_Magnitude_Pips",
    "Baseline_Average_Outcome_Magnitude_Pips",
    "Outcome_Magnitude_vs_Baseline_Ratio",
    "Partial_Comparison_Class",
    "Partial_Comparison_Diagnostic",
]

ADEQUACY_COLUMNS = [
    "Candidate_ID",
    "Sample_Label",
    "Coverage_Ratio",
    "OHLC_Rows",
    "Structure_Count",
    "State_Count",
    "Transition_Count",
    "Condition_Profile_Count",
    "Sample_Adequacy_Class",
    "Sample_Adequacy_Diagnostic",
    "Recommended_Follow_Up",
]

SUMMARY_COLUMNS = [
    "Timeframe",
    "Candidate_Count",
    "Validated_Partial_Candidate_Count",
    "Failed_Candidate_Count",
    "Partial_Sample_Count",
    "Baseline_Scenario_Count",
    "Average_Coverage_Ratio",
    "Partial_Research_Usable_Count",
    "Partial_Limited_Count",
    "Partial_Insufficient_Count",
    "Partial_Unavailable_Count",
    "H4_Partial_Expansion_Profile",
    "H4_Partial_Expansion_Readiness_Flag",
    "H4_Partial_Expansion_Diagnostic",
    "Recommended_Follow_Up",
]


def write_review_outputs(result: H4TargetedPartialExpansionResult) -> H4TargetedPartialExpansionResult:
    result.research_output_dir.mkdir(parents=True, exist_ok=True)
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)

    _write_rows(result.research_output_dir / "h4_partial_candidate_inventory.csv", result.candidates, CANDIDATE_COLUMNS)
    _write_rows(result.research_output_dir / "h4_partial_validation_run_summary.csv", result.run_summaries, RUN_COLUMNS)
    _write_rows(
        result.research_output_dir / "h4_partial_structure_state_summary.csv",
        result.structure_state_summaries,
        STRUCTURE_STATE_COLUMNS,
    )
    _write_rows(result.research_output_dir / "h4_partial_transition_summary.csv", result.transition_summaries, TRANSITION_COLUMNS)
    _write_rows(
        result.research_output_dir / "h4_partial_price_outcome_summary.csv",
        result.price_outcome_summaries,
        PRICE_COLUMNS,
    )
    _write_rows(
        result.research_output_dir / "h4_partial_vs_baseline_comparison.csv",
        result.baseline_comparisons,
        COMPARISON_COLUMNS,
    )
    _write_rows(
        result.research_output_dir / "h4_partial_sample_adequacy_review.csv",
        result.sample_adequacy_rows,
        ADEQUACY_COLUMNS,
    )
    _write_rows(
        result.research_output_dir / "h4_targeted_partial_expansion_validation_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4TargetedPartialExpansionResult) -> str:
    summary = result.summary
    lines = [
        "SQRE H4 Targeted Partial Expansion Validation",
        "============================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        f"Feasibility directory: {result.feasibility_dir}",
        f"Baseline validation directory: {result.baseline_validation_dir}",
        f"Baseline research directory: {result.baseline_research_dir}",
        "",
        "Output Directories",
        "------------------",
        f"Validation output directory: {result.output_dir}",
        f"Research output directory: {result.research_output_dir}",
        "",
        "Candidate Inventory",
        "-------------------",
        f"Candidate rows: {len(result.candidates)}",
        *_row_lines(result.candidates, "candidate_id", "raw_file_status", "candidate_diagnostic"),
        "",
        "Validation Run Summary",
        "----------------------",
        f"Run rows: {len(result.run_summaries)}",
        *_row_lines(result.run_summaries, "candidate_id", "run_status", "run_diagnostic"),
        "",
        "Partial Structure/State Summary",
        "-------------------------------",
        *_row_lines(result.structure_state_summaries, "candidate_id", "state_diversity_profile", "structure_state_diagnostic"),
        "",
        "Partial Transition Summary",
        "--------------------------",
        *_row_lines(result.transition_summaries, "candidate_id", "most_common_transition", "sample_transition_diagnostic"),
        "",
        "Partial Price Outcome Summary",
        "-----------------------------",
        *_row_lines(result.price_outcome_summaries, "candidate_id", "condition_profile_count", "price_outcome_diagnostic"),
        "",
        "Partial vs Baseline Comparison",
        "------------------------------",
        *_row_lines(result.baseline_comparisons, "candidate_id", "partial_comparison_class", "partial_comparison_diagnostic"),
        "",
        "Sample Adequacy Review",
        "----------------------",
        *_row_lines(result.sample_adequacy_rows, "candidate_id", "sample_adequacy_class", "sample_adequacy_diagnostic"),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        *research_readiness_assessment(summary),
        _summary_line(summary, "Readiness flag", "h4_partial_expansion_readiness_flag"),
        _summary_line(summary, "Profile", "h4_partial_expansion_profile"),
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
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(_attr_name(column), "") for column in columns}


def _attr_name(column: str) -> str:
    return column.lower()


def _row_lines(rows: list[object], id_attr: str, status_attr: str, diagnostic_attr: str) -> list[str]:
    if not rows:
        return ["No rows available."]
    output = []
    for row in rows[:5]:
        output.append(
            f"- {getattr(row, id_attr)}: {getattr(row, status_attr)}; {getattr(row, diagnostic_attr)}"
        )
    return output


def _summary_line(summary: object | None, label: str, attr: str) -> str:
    if summary is None:
        return f"{label}: unavailable"
    return f"{label}: {getattr(summary, attr)}"
