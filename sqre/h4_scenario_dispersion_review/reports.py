"""CSV and text report writers for H4 scenario dispersion review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.h4_scenario_dispersion_review.loader import optional_file_status
from sqre.h4_scenario_dispersion_review.models import (
    H4ScenarioDispersionReviewResult,
    ProfileDispersionDiagnostic,
)


PROFILE_COLUMNS = [
    "Condition_Label",
    "Forward_Window",
    "Profile_Type",
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
    "Profile_Dispersion_Class",
    "Profile_Research_Readiness_Class",
    "Profile_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]

AGGREGATION_COLUMNS = PROFILE_COLUMNS + ["Aggregation_Candidate_Rationale"]
SCENARIO_SENSITIVE_COLUMNS = PROFILE_COLUMNS + ["Scenario_Sensitivity_Rationale"]
SAMPLE_COLUMNS = PROFILE_COLUMNS + ["Sample_Review_Rationale"]

SCENARIO_CONTRIBUTION_COLUMNS = [
    "Scenario_ID",
    "Profile_Count",
    "Total_Observations",
    "Average_Sample_Size",
    "Average_Forward_Range_Deviation",
    "Average_Outcome_Magnitude_Deviation",
    "Average_Direction_Alignment_Deviation",
    "High_Deviation_Profile_Count",
    "Moderate_Deviation_Profile_Count",
    "Low_Deviation_Profile_Count",
    "High_Deviation_Profile_Ratio",
    "Dominant_Deviation_Class",
    "Scenario_Contribution_Class",
    "Scenario_Dispersion_Diagnostic",
]

STATE_COLUMNS = [
    "Condition_Label",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Moderate_Dispersion_Profile_Count",
    "Stable_Profile_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "Average_High_Deviation_Scenario_Count",
    "Dominant_Dispersion_Class",
    "State_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]

WINDOW_COLUMNS = [
    "Forward_Window",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Moderate_Dispersion_Profile_Count",
    "Stable_Profile_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "Average_High_Deviation_Scenario_Count",
    "Window_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]

SUMMARY_COLUMNS = [
    "Timeframe",
    "Input_Profile_Count",
    "Research_Ready_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "Aggregation_Candidate_Profile_Count",
    "Scenario_Sensitive_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Moderate_Dispersion_Profile_Count",
    "Stable_Profile_Count",
    "Scenario_Count",
    "High_Contribution_Scenario_Count",
    "Moderate_Contribution_Scenario_Count",
    "Low_Contribution_Scenario_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "H4_Dispersion_Profile",
    "H4_Aggregation_Readiness_Flag",
    "H4_Scenario_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]


def write_review_outputs(result: H4ScenarioDispersionReviewResult) -> H4ScenarioDispersionReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_profile_dispersion_diagnostics.csv", result.profile_diagnostics, PROFILE_COLUMNS)
    _write_rows(
        result.output_dir / "h4_scenario_dispersion_contribution.csv",
        result.scenario_contributions,
        SCENARIO_CONTRIBUTION_COLUMNS,
    )
    _write_rows(result.output_dir / "h4_state_dispersion_summary.csv", result.state_summaries, STATE_COLUMNS)
    _write_rows(result.output_dir / "h4_forward_window_dispersion_summary.csv", result.window_summaries, WINDOW_COLUMNS)
    _write_rows(result.output_dir / "h4_aggregation_candidate_profiles.csv", result.aggregation_candidates, AGGREGATION_COLUMNS)
    _write_rows(result.output_dir / "h4_scenario_sensitive_profiles.csv", result.scenario_sensitive_profiles, SCENARIO_SENSITIVE_COLUMNS)
    _write_rows(result.output_dir / "h4_sample_constrained_profiles.csv", result.sample_constrained_profiles, SAMPLE_COLUMNS)
    _write_rows(
        result.output_dir / "h4_scenario_dispersion_review_summary.csv",
        [result.review_summary] if result.review_summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4ScenarioDispersionReviewResult) -> str:
    status = optional_file_status(result.input_dir)
    lines = [
        "SQRE H4 Scenario Dispersion Review",
        "==================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directory",
        "---------------",
        str(result.input_dir),
        f"Optional Input Availability: {_optional_status_text(status)}",
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Profiles Loaded",
        "---------------",
        f"Input profiles loaded: {result.profiles_loaded}",
        f"Outcome statistics rows loaded: {result.statistics_loaded}",
        f"Scenario comparison rows loaded: {result.comparison_rows_loaded}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        _summary_text(result),
        "",
        "Profile Dispersion Overview",
        "---------------------------",
        _profile_overview_text(result),
        "",
        "State Dispersion Review",
        "-----------------------",
        _state_review_text(result),
        "",
        "Forward Window Dispersion Review",
        "--------------------------------",
        _window_review_text(result),
        "",
        "Scenario Contribution Review",
        "----------------------------",
        "Scenario-period contribution is descriptive and does not make causal claims.",
        _scenario_review_text(result),
        "",
        "Aggregation Candidate Review",
        "----------------------------",
        _profile_list_text(result.aggregation_candidates, "No aggregation candidate profiles were identified."),
        "",
        "Scenario-Sensitive Profile Review",
        "---------------------------------",
        _profile_list_text(result.scenario_sensitive_profiles, "No scenario-sensitive profiles were identified."),
        "",
        "Sample-Constrained Profile Review",
        "---------------------------------",
        _profile_list_text(result.sample_constrained_profiles, "No sample-constrained profiles were identified."),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        _readiness_text(result),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        "- H4 transition outcome deep dive",
        "- H4 selective aggregation review",
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


def _summary_text(result: H4ScenarioDispersionReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No H4 scenario dispersion summary was available."
    return "\n".join(
        [
            f"Aggregation candidate profiles: {summary.aggregation_candidate_profile_count}",
            f"Scenario-sensitive profiles: {summary.scenario_sensitive_profile_count}",
            f"Sample-constrained profiles: {summary.sample_constrained_profile_count}",
            f"H4 aggregation readiness: {summary.h4_aggregation_readiness_flag}",
            summary.h4_scenario_dispersion_diagnostic,
        ]
    )


def _profile_overview_text(result: H4ScenarioDispersionReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No profile dispersion diagnostics were available."
    return "\n".join(
        [
            f"Input profiles: {summary.input_profile_count}",
            f"Aggregation candidate profiles: {summary.aggregation_candidate_profile_count}",
            f"Scenario-sensitive profiles: {summary.scenario_sensitive_profile_count}",
            f"Sample-constrained profiles: {summary.sample_constrained_profile_count}",
            f"High dispersion profiles: {summary.high_dispersion_profile_count}",
            f"Moderate dispersion profiles: {summary.moderate_dispersion_profile_count}",
            f"Stable profiles: {summary.stable_profile_count}",
        ]
    )


def _state_review_text(result: H4ScenarioDispersionReviewResult) -> str:
    if not result.state_summaries:
        return "No state dispersion summaries were available."
    return "\n".join(
        "- "
        f"{row.condition_label}: profiles={row.profile_count}, high={row.high_dispersion_profile_count}, "
        f"moderate={row.moderate_dispersion_profile_count}, stable={row.stable_profile_count}, "
        f"diagnostic={row.state_dispersion_diagnostic}"
        for row in result.state_summaries
    )


def _window_review_text(result: H4ScenarioDispersionReviewResult) -> str:
    if not result.window_summaries:
        return "No forward window summaries were available."
    return "\n".join(
        "- "
        f"FW {row.forward_window}: profiles={row.profile_count}, high={row.high_dispersion_profile_count}, "
        f"moderate={row.moderate_dispersion_profile_count}, stable={row.stable_profile_count}, "
        f"diagnostic={row.window_dispersion_diagnostic}"
        for row in result.window_summaries
    )


def _scenario_review_text(result: H4ScenarioDispersionReviewResult) -> str:
    if not result.scenario_contributions:
        return "No scenario contribution rows were available."
    return "\n".join(
        "- "
        f"{row.scenario_id}: contribution={row.scenario_contribution_class}, "
        f"high_deviation_ratio={row.high_deviation_profile_ratio:.4f}, "
        f"diagnostic={row.scenario_dispersion_diagnostic}"
        for row in result.scenario_contributions
    )


def _profile_list_text(rows: list[ProfileDispersionDiagnostic], empty_text: str) -> str:
    if not rows:
        return empty_text
    return "\n".join(
        "- "
        f"{row.condition_label} FW={row.forward_window}: class={row.profile_research_readiness_class}, "
        f"dispersion={row.profile_dispersion_class}, high_deviation_scenarios={row.high_deviation_scenario_count}"
        for row in rows
    )


def _readiness_text(result: H4ScenarioDispersionReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No research readiness summary was available."
    return "\n".join(
        [
            summary.h4_scenario_dispersion_diagnostic,
            f"Recommended follow-up: {summary.recommended_follow_up}",
        ]
    )
