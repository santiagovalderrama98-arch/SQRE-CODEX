"""CSV and text report writers for H4 scenario-sensitive state review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.h4_scenario_sensitive_state_review.loader import optional_file_status
from sqre.h4_scenario_sensitive_state_review.models import H4ScenarioSensitiveStateReviewResult, ProfileReviewRow


PROFILE_REVIEW_COLUMNS = [
    "Condition_Label",
    "Forward_Window",
    "Scenario_Count",
    "Total_Sample_Size",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Direction_Alignment_Dispersion",
    "High_Deviation_Scenario_Count",
    "Moderate_Deviation_Scenario_Count",
    "Low_Deviation_Scenario_Count",
    "Dominant_Deviation_Class",
    "Dispersion_Driver_Class",
    "Primary_Deviating_Metric",
    "Scenario_Sensitivity_Class",
    "Near_Aggregation_Candidate_Flag",
    "Profile_Review_Diagnostic",
    "Recommended_Follow_Up",
]

DETAIL_COLUMNS = [
    "Condition_Label",
    "Forward_Window",
    "Scenario_ID",
    "Sample_Size",
    "Forward_Range_vs_Profile_Avg",
    "Outcome_Magnitude_vs_Profile_Avg",
    "Direction_Alignment_vs_Profile_Avg",
    "Scenario_Deviation_Class",
    "Primary_Scenario_Deviation_Metric",
    "Scenario_Deviation_Intensity_Class",
    "Scenario_Deviation_Diagnostic",
]

SCENARIO_COLUMNS = [
    "Scenario_ID",
    "Scenario_Profile_Count",
    "High_Deviation_Profile_Count",
    "Moderate_Deviation_Profile_Count",
    "Low_Deviation_Profile_Count",
    "Average_Forward_Range_Deviation",
    "Average_Outcome_Magnitude_Deviation",
    "Average_Direction_Alignment_Deviation",
    "Most_Common_Primary_Deviation_Metric",
    "Scenario_Recurrent_Deviation_Class",
    "Scenario_Review_Diagnostic",
]

STATE_COLUMNS = [
    "Condition_Label",
    "Profile_Count",
    "High_Sensitivity_Profile_Count",
    "Moderate_Sensitivity_Profile_Count",
    "Low_Sensitivity_Profile_Count",
    "Near_Aggregation_Candidate_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "Most_Common_Dispersion_Driver",
    "State_Sensitivity_Diagnostic",
    "Recommended_Follow_Up",
]

WINDOW_COLUMNS = [
    "Forward_Window",
    "Profile_Count",
    "High_Sensitivity_Profile_Count",
    "Moderate_Sensitivity_Profile_Count",
    "Low_Sensitivity_Profile_Count",
    "Near_Aggregation_Candidate_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "Most_Common_Dispersion_Driver",
    "Window_Sensitivity_Diagnostic",
    "Recommended_Follow_Up",
]

NEAR_COLUMNS = PROFILE_REVIEW_COLUMNS + ["Near_Candidate_Rationale"]

SUMMARY_COLUMNS = [
    "Timeframe",
    "Scenario_Sensitive_Profile_Count",
    "Reviewed_Profile_Count",
    "High_Sensitivity_Profile_Count",
    "Moderate_Sensitivity_Profile_Count",
    "Low_Sensitivity_Profile_Count",
    "Near_Aggregation_Candidate_Count",
    "Scenario_Count",
    "High_Recurrent_Deviation_Scenario_Count",
    "Moderate_Recurrent_Deviation_Scenario_Count",
    "Low_Recurrent_Deviation_Scenario_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "Dominant_Dispersion_Driver",
    "H4_Scenario_Sensitive_Profile",
    "H4_Review_Readiness_Flag",
    "H4_Scenario_Sensitive_Review_Diagnostic",
    "Recommended_Follow_Up",
]


def write_review_outputs(result: H4ScenarioSensitiveStateReviewResult) -> H4ScenarioSensitiveStateReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_scenario_sensitive_profile_review.csv", result.reviewed_profiles, PROFILE_REVIEW_COLUMNS)
    _write_rows(result.output_dir / "h4_profile_scenario_deviation_detail.csv", result.scenario_details, DETAIL_COLUMNS)
    _write_rows(result.output_dir / "h4_scenario_recurrent_deviation_summary.csv", result.scenario_summaries, SCENARIO_COLUMNS)
    _write_rows(result.output_dir / "h4_state_sensitivity_summary.csv", result.state_summaries, STATE_COLUMNS)
    _write_rows(result.output_dir / "h4_forward_window_sensitivity_summary.csv", result.window_summaries, WINDOW_COLUMNS)
    _write_rows(result.output_dir / "h4_near_aggregation_candidate_review.csv", result.near_candidates, NEAR_COLUMNS)
    _write_rows(
        result.output_dir / "h4_scenario_sensitive_state_review_summary.csv",
        [result.review_summary] if result.review_summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    status = optional_file_status(result.dispersion_review_dir, result.state_deep_dive_dir)
    lines = [
        "SQRE H4 Scenario-Sensitive State Profile Review",
        "==============================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        f"Dispersion Review: {result.dispersion_review_dir}",
        f"State Deep Dive: {result.state_deep_dive_dir}",
        f"Optional Input Availability: {_optional_status_text(status)}",
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Profiles Loaded",
        "---------------",
        f"Scenario-sensitive profiles loaded: {result.scenario_sensitive_profiles_loaded}",
        f"Scenario comparison rows loaded: {result.comparison_rows_loaded}",
        f"Scenario breakdown rows loaded: {result.breakdown_rows_loaded}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        _summary_text(result),
        "",
        "Scenario-Sensitive Profile Overview",
        "-----------------------------------",
        _profile_overview_text(result),
        "",
        "State Sensitivity Review",
        "------------------------",
        _state_review_text(result),
        "",
        "Forward Window Sensitivity Review",
        "---------------------------------",
        _window_review_text(result),
        "",
        "Scenario Recurrent Deviation Review",
        "-----------------------------------",
        "Scenario-period recurrent deviation is descriptive and does not make causal claims.",
        _scenario_review_text(result),
        "",
        "Deviation Driver Review",
        "-----------------------",
        _driver_review_text(result),
        "",
        "Near Aggregation Candidate Review",
        "---------------------------------",
        _near_candidate_text(result.near_candidates),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        _readiness_text(result),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        "- H4 transition outcome deep dive",
        "- H4 scenario-sensitive state family review",
        "- H4/D1 condition-family aggregation",
        "- Research reference-store design",
        "- H1 secondary context monitoring",
        "",
        "Do Not Change Yet",
        "-----------------",
        "- No production defaults were modified.",
        "- No thresholds were modified.",
        "- No production taxonomy was modified.",
        "- No Decision Engine was added.",
        "- No operational logic was added.",
        "",
        "Limitations",
        "-----------",
        "- Scenario periods are descriptive partitions, not causal classifications.",
        "- Findings depend on available H4 historical samples.",
        "- Findings are descriptive.",
        "- No comparative ordering is produced.",
        "- No production calibration decision is made.",
        "- No operational decision is produced.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    records = [_row_record(row, columns) for row in rows if row is not None]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _row_record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _optional_status_text(status: dict[str, bool]) -> str:
    return ", ".join(f"{name}={'present' if present else 'missing'}" for name, present in sorted(status.items()))


def _summary_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No H4 scenario-sensitive summary was available."
    return "\n".join(
        [
            f"Reviewed profiles: {summary.reviewed_profile_count}",
            f"High sensitivity profiles: {summary.high_sensitivity_profile_count}",
            f"Moderate sensitivity profiles: {summary.moderate_sensitivity_profile_count}",
            f"Low sensitivity profiles: {summary.low_sensitivity_profile_count}",
            f"Near aggregation candidates: {summary.near_aggregation_candidate_count}",
            f"Dominant dispersion driver: {summary.dominant_dispersion_driver}",
            f"H4 review readiness: {summary.h4_review_readiness_flag}",
            summary.h4_scenario_sensitive_review_diagnostic,
        ]
    )


def _profile_overview_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No scenario-sensitive profile rows were available."
    return "\n".join(
        [
            f"Scenario-sensitive profiles loaded: {summary.scenario_sensitive_profile_count}",
            f"Reviewed profiles: {summary.reviewed_profile_count}",
            f"High sensitivity profiles: {summary.high_sensitivity_profile_count}",
            f"Moderate sensitivity profiles: {summary.moderate_sensitivity_profile_count}",
            f"Low sensitivity profiles: {summary.low_sensitivity_profile_count}",
            f"Near aggregation candidates: {summary.near_aggregation_candidate_count}",
            f"Dominant dispersion driver: {summary.dominant_dispersion_driver}",
        ]
    )


def _state_review_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    if not result.state_summaries:
        return "No state sensitivity summaries were available."
    return "\n".join(
        "- "
        f"{row.condition_label}: profiles={row.profile_count}, high={row.high_sensitivity_profile_count}, "
        f"moderate={row.moderate_sensitivity_profile_count}, near={row.near_aggregation_candidate_count}, "
        f"driver={row.most_common_dispersion_driver}, diagnostic={row.state_sensitivity_diagnostic}"
        for row in result.state_summaries
    )


def _window_review_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    if not result.window_summaries:
        return "No forward window sensitivity summaries were available."
    return "\n".join(
        "- "
        f"FW {row.forward_window}: profiles={row.profile_count}, high={row.high_sensitivity_profile_count}, "
        f"moderate={row.moderate_sensitivity_profile_count}, near={row.near_aggregation_candidate_count}, "
        f"driver={row.most_common_dispersion_driver}, diagnostic={row.window_sensitivity_diagnostic}"
        for row in result.window_summaries
    )


def _scenario_review_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    if not result.scenario_summaries:
        return "No scenario recurrent deviation rows were available."
    return "\n".join(
        "- "
        f"{row.scenario_id}: class={row.scenario_recurrent_deviation_class}, "
        f"high={row.high_deviation_profile_count}, moderate={row.moderate_deviation_profile_count}, "
        f"driver={row.most_common_primary_deviation_metric}, diagnostic={row.scenario_review_diagnostic}"
        for row in result.scenario_summaries
    )


def _driver_review_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    if not result.reviewed_profiles:
        return "No deviation driver rows were available."
    counts: dict[str, int] = {}
    for row in result.reviewed_profiles:
        counts[row.primary_deviating_metric] = counts.get(row.primary_deviating_metric, 0) + 1
    return "\n".join(f"- {driver}: {count} profiles" for driver, count in sorted(counts.items()))


def _near_candidate_text(rows: list[ProfileReviewRow]) -> str:
    if not rows:
        return "No near aggregation candidate profiles were identified."
    return "\n".join(
        "- "
        f"{row.condition_label} FW={row.forward_window}: sensitivity={row.scenario_sensitivity_class}, "
        f"driver={row.primary_deviating_metric}"
        for row in rows
    )


def _readiness_text(result: H4ScenarioSensitiveStateReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No research readiness summary was available."
    return "\n".join(
        [
            summary.h4_scenario_sensitive_review_diagnostic,
            f"Recommended follow-up: {summary.recommended_follow_up}",
        ]
    )
