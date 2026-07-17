"""CSV and text report writers for H4 transition scenario dispersion review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.h4_transition_scenario_dispersion_review.loader import optional_file_status
from sqre.h4_transition_scenario_dispersion_review.models import (
    H4TransitionScenarioDispersionReviewResult,
    ProfileDispersionDiagnostic,
    TransitionGroupDispersionSummaryRow,
)


PROFILE_COLUMNS = [
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Family",
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
    "Transition_Profile_Readiness_Class",
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

GROUP_COLUMNS = [
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Scenario_Sensitive_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "Aggregation_Candidate_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Moderate_Dispersion_Profile_Count",
    "Stable_Profile_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Dispersion",
    "Average_High_Deviation_Scenario_Count",
    "Dominant_Dispersion_Class",
]

FAMILY_COLUMNS = [
    "Transition_Family",
    *GROUP_COLUMNS,
    "Transition_Family_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]
SOURCE_STATE_COLUMNS = [
    "Source_State",
    *GROUP_COLUMNS[:-2],
    "Source_State_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]
TARGET_STATE_COLUMNS = [
    "Target_State",
    *GROUP_COLUMNS[:-2],
    "Target_State_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]

WINDOW_COLUMNS = [
    "Forward_Window",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Scenario_Sensitive_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "Aggregation_Candidate_Profile_Count",
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
    "Scenario_Sensitive_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "Aggregation_Candidate_Profile_Count",
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
    "H4_Transition_Dispersion_Profile",
    "H4_Transition_Aggregation_Readiness_Flag",
    "H4_Transition_Scenario_Dispersion_Diagnostic",
    "Recommended_Follow_Up",
]

KEY_TRANSITIONS = [
    "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT",
    "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION",
    "DIRECTIONAL_EXPANSION -> DIRECTIONAL_DISPLACEMENT",
    "VOLATILE_ROTATION -> DIRECTIONAL_DISPLACEMENT",
]


def write_review_outputs(result: H4TransitionScenarioDispersionReviewResult) -> H4TransitionScenarioDispersionReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(
        result.output_dir / "h4_transition_profile_dispersion_diagnostics.csv",
        result.profile_diagnostics,
        PROFILE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_transition_scenario_dispersion_contribution.csv",
        result.scenario_contributions,
        SCENARIO_CONTRIBUTION_COLUMNS,
    )
    _write_group_rows(
        result.output_dir / "h4_transition_family_dispersion_summary.csv",
        result.family_summaries,
        FAMILY_COLUMNS,
        "Transition_Family",
        "Transition_Family_Dispersion_Diagnostic",
    )
    _write_group_rows(
        result.output_dir / "h4_transition_source_state_dispersion_summary.csv",
        result.source_state_summaries,
        SOURCE_STATE_COLUMNS,
        "Source_State",
        "Source_State_Dispersion_Diagnostic",
    )
    _write_group_rows(
        result.output_dir / "h4_transition_target_state_dispersion_summary.csv",
        result.target_state_summaries,
        TARGET_STATE_COLUMNS,
        "Target_State",
        "Target_State_Dispersion_Diagnostic",
    )
    _write_rows(
        result.output_dir / "h4_transition_forward_window_dispersion_summary.csv",
        result.window_summaries,
        WINDOW_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_transition_aggregation_candidate_profiles.csv",
        result.aggregation_candidates,
        AGGREGATION_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_transition_scenario_sensitive_profiles.csv",
        result.scenario_sensitive_profiles,
        SCENARIO_SENSITIVE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_transition_sample_constrained_profiles.csv",
        result.sample_constrained_profiles,
        SAMPLE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_transition_scenario_dispersion_review_summary.csv",
        [result.review_summary] if result.review_summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4TransitionScenarioDispersionReviewResult) -> str:
    status = optional_file_status(result.input_dir)
    lines = [
        "SQRE H4 Transition Scenario Dispersion Review",
        "============================================",
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
        "Transition Profile Dispersion Overview",
        "--------------------------------------",
        _profile_overview_text(result),
        "",
        "Key Transition Review",
        "---------------------",
        _key_transition_text(result.profile_diagnostics),
        "",
        "Transition Family Dispersion Review",
        "-----------------------------------",
        _group_review_text(result.family_summaries, "No transition family summaries were available."),
        "",
        "Source State Dispersion Review",
        "------------------------------",
        _group_review_text(result.source_state_summaries, "No source state summaries were available."),
        "",
        "Target State Dispersion Review",
        "------------------------------",
        _group_review_text(result.target_state_summaries, "No target state summaries were available."),
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
        "Scenario-Sensitive Transition Review",
        "------------------------------------",
        _profile_list_text(result.scenario_sensitive_profiles, "No scenario-sensitive transition profiles were identified."),
        "",
        "Sample-Constrained Transition Review",
        "------------------------------------",
        _profile_list_text(result.sample_constrained_profiles, "No sample-constrained transition profiles were identified."),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        _readiness_text(result),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        "- H4 selective transition aggregation review",
        "- H4 transition/state combined context review",
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


def _write_group_rows(
    path: Path,
    rows: Iterable[TransitionGroupDispersionSummaryRow],
    columns: list[str],
    group_column: str,
    diagnostic_column: str,
) -> None:
    records = []
    for row in rows:
        record = _row_record(row, columns)
        record[group_column] = row.group_value
        record[diagnostic_column] = row.dispersion_diagnostic
        records.append(record)
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _row_record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _optional_status_text(status: dict[str, bool]) -> str:
    return ", ".join(f"{name}={'present' if present else 'missing'}" for name, present in sorted(status.items()))


def _summary_text(result: H4TransitionScenarioDispersionReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No H4 transition scenario dispersion summary was available."
    return "\n".join(
        [
            f"Aggregation candidate profiles: {summary.aggregation_candidate_profile_count}",
            f"Scenario-sensitive profiles: {summary.scenario_sensitive_profile_count}",
            f"Sample-constrained profiles: {summary.sample_constrained_profile_count}",
            f"H4 transition aggregation readiness: {summary.h4_transition_aggregation_readiness_flag}",
            summary.h4_transition_scenario_dispersion_diagnostic,
        ]
    )


def _profile_overview_text(result: H4TransitionScenarioDispersionReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No transition profile dispersion diagnostics were available."
    return "\n".join(
        [
            f"Input profiles: {summary.input_profile_count}",
            f"Research-ready profiles: {summary.research_ready_profile_count}",
            f"Aggregation candidate profiles: {summary.aggregation_candidate_profile_count}",
            f"Scenario-sensitive profiles: {summary.scenario_sensitive_profile_count}",
            f"Sample-constrained profiles: {summary.sample_constrained_profile_count}",
            f"High dispersion profiles: {summary.high_dispersion_profile_count}",
            f"Moderate dispersion profiles: {summary.moderate_dispersion_profile_count}",
            f"Stable profiles: {summary.stable_profile_count}",
        ]
    )


def _key_transition_text(rows: list[ProfileDispersionDiagnostic]) -> str:
    if not rows:
        return "No transition profile diagnostics were available."
    lines = []
    for label in KEY_TRANSITIONS:
        selected = [row for row in rows if row.condition_label == label]
        if not selected:
            lines.append(f"- {label}: no matching H4 transition diagnostics were available.")
            continue
        for row in selected:
            lines.append(
                "- "
                f"{row.condition_label} FW={row.forward_window}: "
                f"source={row.source_state}, target={row.target_state}, "
                f"class={row.transition_profile_readiness_class}, "
                f"dispersion={row.profile_dispersion_class}, "
                f"high_deviation_scenarios={row.high_deviation_scenario_count}, "
                f"diagnostic={row.profile_dispersion_diagnostic}"
            )
    return "\n".join(lines)


def _group_review_text(rows: list[TransitionGroupDispersionSummaryRow], empty_text: str) -> str:
    if not rows:
        return empty_text
    return "\n".join(
        "- "
        f"{row.group_value}: profiles={row.profile_count}, candidates={row.aggregation_candidate_profile_count}, "
        f"scenario_sensitive={row.scenario_sensitive_profile_count}, sample={row.sample_constrained_profile_count}, "
        f"diagnostic={row.dispersion_diagnostic}"
        for row in rows
    )


def _window_review_text(result: H4TransitionScenarioDispersionReviewResult) -> str:
    if not result.window_summaries:
        return "No forward window summaries were available."
    return "\n".join(
        "- "
        f"FW {row.forward_window}: profiles={row.profile_count}, candidates={row.aggregation_candidate_profile_count}, "
        f"high={row.high_dispersion_profile_count}, moderate={row.moderate_dispersion_profile_count}, "
        f"stable={row.stable_profile_count}, diagnostic={row.window_dispersion_diagnostic}"
        for row in result.window_summaries
    )


def _scenario_review_text(result: H4TransitionScenarioDispersionReviewResult) -> str:
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
        f"{row.condition_label} FW={row.forward_window}: class={row.transition_profile_readiness_class}, "
        f"dispersion={row.profile_dispersion_class}, high_deviation_scenarios={row.high_deviation_scenario_count}"
        for row in rows
    )


def _readiness_text(result: H4TransitionScenarioDispersionReviewResult) -> str:
    summary = result.review_summary
    if summary is None:
        return "No research readiness summary was available."
    return "\n".join(
        [
            summary.h4_transition_scenario_dispersion_diagnostic,
            f"Recommended follow-up: {summary.recommended_follow_up}",
        ]
    )
