"""CSV and text report writers for H4 transition outcome deep dive."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.h4_transition_outcome_deep_dive.findings import transition_summary_diagnostic, transition_summary_follow_up
from sqre.h4_transition_outcome_deep_dive.loader import optional_input_file_status
from sqre.h4_transition_outcome_deep_dive.models import (
    H4TransitionOutcomeDeepDiveResult,
    OutcomeStatisticsRow,
    TransitionFamilySummaryRow,
    TransitionSummaryRow,
)
from sqre.h4_transition_outcome_deep_dive.outcome_statistics import mean


PROFILE_INVENTORY_COLUMNS = [
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Family",
    "Forward_Window",
    "Profile_Type",
    "Scenario_Count",
    "Scenarios_Present",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Scenario",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Scenario_Sensitivity_Flag",
    "Sample_Adequacy_Flag",
    "Dispersion_Class",
    "Transition_Research_Class",
    "Profile_Diagnostic",
    "Recommended_Follow_Up",
]

SCENARIO_BREAKDOWN_COLUMNS = [
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Family",
    "Forward_Window",
    "Profile_Type",
    "Scenario_ID",
    "Timeframe",
    "Sample_Size",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Favorable_Displacement_Pips",
    "Average_Adverse_Displacement_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Sample_Adequacy_Flag",
    "Scenario_Observation_Diagnostic",
]

OUTCOME_STATISTICS_COLUMNS = [
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Family",
    "Forward_Window",
    "Profile_Type",
    "Scenario_Count",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Scenario",
    "Average_Forward_Close_Return_Pips",
    "Min_Forward_Close_Return_Pips",
    "Max_Forward_Close_Return_Pips",
    "Forward_Close_Return_Dispersion_Pips",
    "Average_Forward_Range_Pips",
    "Min_Forward_Range_Pips",
    "Max_Forward_Range_Pips",
    "Forward_Range_Dispersion_Pips",
    "Forward_Range_CV",
    "Average_Outcome_Magnitude_Pips",
    "Min_Outcome_Magnitude_Pips",
    "Max_Outcome_Magnitude_Pips",
    "Outcome_Magnitude_Dispersion_Pips",
    "Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Rate",
    "Min_Direction_Alignment_Rate",
    "Max_Direction_Alignment_Rate",
    "Direction_Alignment_Dispersion",
    "Outcome_Profile_Stability_Class",
    "Outcome_Profile_Diagnostic",
    "Recommended_Follow_Up",
]

COMPARISON_COLUMNS = [
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Family",
    "Forward_Window",
    "Scenario_ID",
    "Sample_Size",
    "Forward_Close_Return_vs_Profile_Avg",
    "Forward_Range_vs_Profile_Avg",
    "Outcome_Magnitude_vs_Profile_Avg",
    "Direction_Alignment_vs_Profile_Avg",
    "Scenario_Deviation_Class",
    "Scenario_Comparison_Diagnostic",
]

FAMILY_SUMMARY_COLUMNS = [
    "Transition_Family",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Scenario_Sensitive_Observation_Count",
    "Sample_Constrained_Observation_Count",
    "Total_Sample_Size",
    "Average_Scenario_Count",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Stable_Profile_Count",
    "Moderate_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Transition_Family_Diagnostic",
    "Recommended_Follow_Up",
]

SUMMARY_COLUMNS = [
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Family",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Scenario_Sensitive_Observation_Count",
    "Sample_Constrained_Observation_Count",
    "Total_Sample_Size",
    "Average_Scenario_Count",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Stable_Profile_Count",
    "Moderate_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Transition_Deep_Dive_Diagnostic",
    "Recommended_Follow_Up",
]


def build_transition_deep_dive_summary(statistics_rows: list[OutcomeStatisticsRow]) -> list[TransitionSummaryRow]:
    grouped: dict[str, list[OutcomeStatisticsRow]] = defaultdict(list)
    for row in statistics_rows:
        grouped[row.condition_label].append(row)
    return [_summary_row(label, rows) for label, rows in sorted(grouped.items())]


def build_transition_family_summary(statistics_rows: list[OutcomeStatisticsRow]) -> list[TransitionFamilySummaryRow]:
    grouped: dict[str, list[OutcomeStatisticsRow]] = defaultdict(list)
    for row in statistics_rows:
        grouped[row.transition_family].append(row)
    return [_family_row(family, rows) for family, rows in sorted(grouped.items())]


def write_deep_dive_outputs(result: H4TransitionOutcomeDeepDiveResult) -> H4TransitionOutcomeDeepDiveResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(
        result.output_dir / "h4_transition_deep_dive_profile_inventory.csv",
        result.selected_profiles,
        PROFILE_INVENTORY_COLUMNS,
    )
    _write_rows(result.output_dir / "h4_transition_scenario_breakdown.csv", result.scenario_breakdown_rows, SCENARIO_BREAKDOWN_COLUMNS)
    _write_rows(result.output_dir / "h4_transition_outcome_statistics.csv", result.outcome_statistics_rows, OUTCOME_STATISTICS_COLUMNS)
    _write_rows(result.output_dir / "h4_transition_scenario_comparison_matrix.csv", result.comparison_rows, COMPARISON_COLUMNS)
    _write_rows(result.output_dir / "h4_transition_family_summary.csv", result.family_summary_rows, FAMILY_SUMMARY_COLUMNS)
    _write_rows(result.output_dir / "h4_transition_deep_dive_summary.csv", result.summary_rows, SUMMARY_COLUMNS)
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4TransitionOutcomeDeepDiveResult) -> str:
    optional_status = optional_input_file_status(result.h4_d1_research_dir, result.validation_output_dir)
    lines = [
        "SQRE H4 Transition Outcome Deep Dive",
        "===================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        f"H4/D1 Research Directory: {result.h4_d1_research_dir}",
        f"Validation Output Directory: {result.validation_output_dir}",
        f"Optional Input Availability: {_optional_status_text(optional_status)}",
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Profiles Loaded",
        "---------------",
        f"Price Profiles Loaded: {result.price_profiles_loaded}",
        f"Scenario Outcomes Loaded: {result.scenario_outcomes_loaded}",
        f"Selected H4 Transition Profiles: {len(result.selected_profiles)}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        _executive_summary(result),
        "",
        "Selected H4 Transition Profiles",
        "--------------------------------",
        _selected_profiles_text(result),
        "",
        "Key Transition Deep Dive",
        "------------------------",
        _key_transition_text(result),
        "",
        "Transition Family Review",
        "------------------------",
        _family_text(result.family_summary_rows),
        "",
        "Sample-Constrained Transition Review",
        "------------------------------------",
        _sample_constrained_text(result),
        "",
        "Scenario Breakdown Review",
        "-------------------------",
        "Scenario-period observations are descriptive historical partitions.",
        f"Scenario breakdown rows: {len(result.scenario_breakdown_rows)}",
        "",
        "Outcome Dispersion Review",
        "-------------------------",
        _dispersion_text(result.outcome_statistics_rows),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        _readiness_text(result.summary_rows),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        "- H4 transition scenario dispersion review",
        "- H4/D1 condition-family aggregation",
        "- H4 transition/state combined context review",
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


def _summary_row(label: str, rows: list[OutcomeStatisticsRow]) -> TransitionSummaryRow:
    ready, scenario, sample, high = _counts(rows)
    first = rows[0]
    return TransitionSummaryRow(
        condition_label=label,
        source_state=first.source_state,
        target_state=first.target_state,
        transition_family=first.transition_family,
        profile_count=len(rows),
        research_ready_profile_count=ready,
        scenario_sensitive_observation_count=scenario,
        sample_constrained_observation_count=sample,
        total_sample_size=sum(row.total_sample_size for row in rows),
        average_scenario_count=mean([row.scenario_count for row in rows]),
        average_forward_range_pips=mean([row.average_forward_range_pips for row in rows]),
        average_outcome_magnitude_pips=mean([row.average_outcome_magnitude_pips for row in rows]),
        average_direction_alignment_rate=mean([row.average_direction_alignment_rate for row in rows]),
        average_forward_range_cv=mean([row.forward_range_cv for row in rows]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in rows]),
        stable_profile_count=sum(1 for row in rows if row.outcome_profile_stability_class == "STABLE_DESCRIPTIVE"),
        moderate_profile_count=sum(1 for row in rows if row.outcome_profile_stability_class == "MODERATE_DISPERSION"),
        high_dispersion_profile_count=high,
        transition_deep_dive_diagnostic=transition_summary_diagnostic(ready, sample, scenario, high),
        recommended_follow_up=transition_summary_follow_up(sample, scenario, high),
    )


def _family_row(family: str, rows: list[OutcomeStatisticsRow]) -> TransitionFamilySummaryRow:
    ready, scenario, sample, high = _counts(rows)
    return TransitionFamilySummaryRow(
        transition_family=family,
        profile_count=len(rows),
        research_ready_profile_count=ready,
        scenario_sensitive_observation_count=scenario,
        sample_constrained_observation_count=sample,
        total_sample_size=sum(row.total_sample_size for row in rows),
        average_scenario_count=mean([row.scenario_count for row in rows]),
        average_forward_range_pips=mean([row.average_forward_range_pips for row in rows]),
        average_outcome_magnitude_pips=mean([row.average_outcome_magnitude_pips for row in rows]),
        average_direction_alignment_rate=mean([row.average_direction_alignment_rate for row in rows]),
        average_forward_range_cv=mean([row.forward_range_cv for row in rows]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in rows]),
        stable_profile_count=sum(1 for row in rows if row.outcome_profile_stability_class == "STABLE_DESCRIPTIVE"),
        moderate_profile_count=sum(1 for row in rows if row.outcome_profile_stability_class == "MODERATE_DISPERSION"),
        high_dispersion_profile_count=high,
        transition_family_diagnostic=transition_summary_diagnostic(ready, sample, scenario, high),
        recommended_follow_up=transition_summary_follow_up(sample, scenario, high),
    )


def _counts(rows: list[OutcomeStatisticsRow]) -> tuple[int, int, int, int]:
    ready = sum(1 for row in rows if row.profile_type == "RESEARCH_READY")
    scenario = sum(1 for row in rows if row.profile_type == "SCENARIO_SENSITIVE_OBSERVATION")
    sample = sum(1 for row in rows if row.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION")
    high = sum(1 for row in rows if row.outcome_profile_stability_class == "HIGH_DISPERSION")
    return ready, scenario, sample, high


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    records = [_row_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _row_record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _optional_status_text(status: dict[str, bool]) -> str:
    return ", ".join(f"{name}={'present' if present else 'missing'}" for name, present in sorted(status.items()))


def _executive_summary(result: H4TransitionOutcomeDeepDiveResult) -> str:
    ready = sum(1 for profile in result.selected_profiles if profile.profile_type == "RESEARCH_READY")
    sample = sum(1 for profile in result.selected_profiles if profile.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION")
    scenario = sum(1 for profile in result.selected_profiles if profile.profile_type == "SCENARIO_SENSITIVE_OBSERVATION")
    return "\n".join(
        [
            f"Research-ready H4 transition profiles selected: {ready}",
            f"Sample-constrained H4 transition observations selected: {sample}",
            f"Scenario-sensitive H4 transition observations selected: {scenario}",
            f"Outcome statistics rows: {len(result.outcome_statistics_rows)}",
            f"Comparison matrix rows: {len(result.comparison_rows)}",
            f"Transition family summary rows: {len(result.family_summary_rows)}",
            f"Summary rows: {len(result.summary_rows)}",
        ]
    )


def _selected_profiles_text(result: H4TransitionOutcomeDeepDiveResult) -> str:
    if not result.selected_profiles:
        return "No selected H4 transition profiles were available."
    return "\n".join(
        "- "
        f"{profile.profile_type}: {profile.condition_label} "
        f"({profile.source_state} -> {profile.target_state}) FW={profile.forward_window} "
        f"sample={profile.total_sample_size} scenarios={profile.scenario_count}"
        for profile in result.selected_profiles
    )


def _key_transition_text(result: H4TransitionOutcomeDeepDiveResult) -> str:
    if not result.outcome_statistics_rows:
        return "No transition outcome statistics rows were available."
    lines = []
    for row in sorted(result.outcome_statistics_rows, key=lambda item: (-item.total_sample_size, item.condition_label, item.forward_window))[:8]:
        lines.append(
            "- "
            f"{row.condition_label} ({row.source_state} -> {row.target_state}) FW={row.forward_window}: "
            f"sample={row.total_sample_size}, scenarios={row.scenario_count}, "
            f"forward_range={_fmt(row.average_forward_range_pips)}, "
            f"outcome_magnitude={_fmt(row.average_outcome_magnitude_pips)}, "
            f"direction_alignment={_fmt(row.average_direction_alignment_rate)}, "
            f"dispersion={row.outcome_profile_stability_class}, diagnostic={row.outcome_profile_diagnostic}"
        )
    return "\n".join(lines)


def _family_text(rows: list[TransitionFamilySummaryRow]) -> str:
    if not rows:
        return "No transition family summary rows were available."
    return "\n".join(
        "- "
        f"{row.transition_family}: profiles={row.profile_count}, sample={row.total_sample_size}, "
        f"ready={row.research_ready_profile_count}, scenario_sensitive={row.scenario_sensitive_observation_count}, "
        f"sample_review={row.sample_constrained_observation_count}, diagnostic={row.transition_family_diagnostic}"
        for row in rows
    )


def _sample_constrained_text(result: H4TransitionOutcomeDeepDiveResult) -> str:
    rows = [row for row in result.selected_profiles if row.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION"]
    if not rows:
        return "No sample-constrained H4 transition observations were selected."
    return "\n".join(
        "- "
        f"{row.condition_label} FW={row.forward_window}: sample={row.total_sample_size}, "
        f"scenarios={row.scenario_count}, follow_up={row.recommended_follow_up}"
        for row in rows
    )


def _dispersion_text(rows: list[OutcomeStatisticsRow]) -> str:
    if not rows:
        return "No outcome statistics rows were available."
    stable = sum(1 for row in rows if row.outcome_profile_stability_class == "STABLE_DESCRIPTIVE")
    moderate = sum(1 for row in rows if row.outcome_profile_stability_class == "MODERATE_DISPERSION")
    high = sum(1 for row in rows if row.outcome_profile_stability_class == "HIGH_DISPERSION")
    return f"Stable profiles: {stable}\nModerate dispersion profiles: {moderate}\nHigh dispersion profiles: {high}"


def _readiness_text(rows: list[TransitionSummaryRow]) -> str:
    if not rows:
        return "No H4 transition deep dive summaries were available."
    return "\n".join(
        "- "
        f"{row.condition_label}: profiles={row.profile_count}, ready={row.research_ready_profile_count}, "
        f"sample_review={row.sample_constrained_observation_count}, "
        f"scenario_sensitive={row.scenario_sensitive_observation_count}, "
        f"diagnostic={row.transition_deep_dive_diagnostic}"
        for row in rows
    )


def _fmt(value: float) -> str:
    return f"{value:.4f}"
