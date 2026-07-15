"""CSV and text report writers for H4 state outcome deep dive."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.h4_state_outcome_deep_dive.findings import state_summary_diagnostic, state_summary_follow_up
from sqre.h4_state_outcome_deep_dive.loader import optional_input_file_status
from sqre.h4_state_outcome_deep_dive.models import (
    H4StateDeepDiveSummaryRow,
    H4StateOutcomeDeepDiveResult,
    OutcomeStatisticsRow,
)
from sqre.h4_state_outcome_deep_dive.outcome_statistics import mean


PROFILE_INVENTORY_COLUMNS = [
    "Condition_Label",
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
    "Condition_Research_Class",
    "Profile_Diagnostic",
    "Recommended_Follow_Up",
]

SCENARIO_BREAKDOWN_COLUMNS = [
    "Condition_Label",
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

SUMMARY_COLUMNS = [
    "Condition_Label",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Sample_Constrained_Observation_Count",
    "Scenario_Sensitive_Observation_Count",
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
    "State_Deep_Dive_Diagnostic",
    "Recommended_Follow_Up",
]


def build_state_deep_dive_summary(
    statistics_rows: list[OutcomeStatisticsRow],
) -> list[H4StateDeepDiveSummaryRow]:
    grouped: dict[str, list[OutcomeStatisticsRow]] = defaultdict(list)
    for row in statistics_rows:
        grouped[row.condition_label].append(row)
    summaries: list[H4StateDeepDiveSummaryRow] = []
    for label, rows in sorted(grouped.items()):
        ready = sum(1 for row in rows if row.profile_type == "RESEARCH_READY")
        sample = sum(1 for row in rows if row.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION")
        scenario = sum(1 for row in rows if row.profile_type == "SCENARIO_SENSITIVE_OBSERVATION")
        high = sum(1 for row in rows if row.outcome_profile_stability_class == "HIGH_DISPERSION")
        summaries.append(
            H4StateDeepDiveSummaryRow(
                condition_label=label,
                profile_count=len(rows),
                research_ready_profile_count=ready,
                sample_constrained_observation_count=sample,
                scenario_sensitive_observation_count=scenario,
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
                state_deep_dive_diagnostic=state_summary_diagnostic(ready, sample, scenario, high),
                recommended_follow_up=state_summary_follow_up(sample, scenario, high),
            )
        )
    return summaries


def write_deep_dive_outputs(result: H4StateOutcomeDeepDiveResult) -> H4StateOutcomeDeepDiveResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_state_deep_dive_profile_inventory.csv", result.selected_profiles, PROFILE_INVENTORY_COLUMNS)
    _write_rows(result.output_dir / "h4_state_scenario_breakdown.csv", result.scenario_breakdown_rows, SCENARIO_BREAKDOWN_COLUMNS)
    _write_rows(result.output_dir / "h4_state_outcome_statistics.csv", result.outcome_statistics_rows, OUTCOME_STATISTICS_COLUMNS)
    _write_rows(result.output_dir / "h4_state_scenario_comparison_matrix.csv", result.comparison_rows, COMPARISON_COLUMNS)
    _write_rows(result.output_dir / "h4_state_deep_dive_summary.csv", result.summary_rows, SUMMARY_COLUMNS)
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4StateOutcomeDeepDiveResult) -> str:
    optional_status = optional_input_file_status(result.h4_d1_research_dir, result.validation_output_dir)
    lines = [
        "SQRE H4 Research-Ready State Outcome Deep Dive",
        "================================================",
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
        f"Selected H4 State Profiles: {len(result.selected_profiles)}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        _executive_summary(result),
        "",
        "Selected H4 State Profiles",
        "--------------------------",
        _selected_profiles_text(result),
        "",
        "DIRECTIONAL_DISPLACEMENT Deep Dive",
        "----------------------------------",
        _condition_deep_dive_text(result, "DIRECTIONAL_DISPLACEMENT"),
        "",
        "DIRECTIONAL_EXPANSION Deep Dive",
        "-------------------------------",
        _condition_deep_dive_text(result, "DIRECTIONAL_EXPANSION"),
        "",
        "VOLATILE_ROTATION Review",
        "------------------------",
        _condition_deep_dive_text(result, "VOLATILE_ROTATION"),
        "",
        "Sample-Constrained State Review",
        "-------------------------------",
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
        "- H4 transition outcome deep dive",
        "- H4/D1 condition-family aggregation",
        "- Scenario-level sample adequacy review",
        "- Research reference-store design",
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
        "- Findings depend on available H4 historical samples.",
        "- Findings are descriptive.",
        "- No comparative ordering is produced.",
        "- No production calibration decision is made.",
        "- No operational decision is produced.",
        "- H4 state labels do not make macro causal claims.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    records = [_row_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _row_record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(_field_name(column), "") for column in columns}


def _field_name(column: str) -> str:
    return column.lower()


def _optional_status_text(status: dict[str, bool]) -> str:
    return ", ".join(f"{name}={'present' if present else 'missing'}" for name, present in sorted(status.items()))


def _executive_summary(result: H4StateOutcomeDeepDiveResult) -> str:
    ready = sum(1 for profile in result.selected_profiles if profile.profile_type == "RESEARCH_READY")
    sample = sum(1 for profile in result.selected_profiles if profile.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION")
    scenario = sum(1 for profile in result.selected_profiles if profile.profile_type == "SCENARIO_SENSITIVE_OBSERVATION")
    return "\n".join(
        [
            f"Research-ready H4 state profiles selected: {ready}",
            f"Sample-constrained H4 observations selected: {sample}",
            f"Scenario-sensitive H4 observations selected: {scenario}",
            f"Outcome statistics rows: {len(result.outcome_statistics_rows)}",
            f"Comparison matrix rows: {len(result.comparison_rows)}",
            f"Summary rows: {len(result.summary_rows)}",
        ]
    )


def _selected_profiles_text(result: H4StateOutcomeDeepDiveResult) -> str:
    if not result.selected_profiles:
        return "No selected H4 state profiles were available."
    return "\n".join(
        "- "
        f"{profile.profile_type}: {profile.condition_label} FW={profile.forward_window} "
        f"sample={profile.total_sample_size} scenarios={profile.scenario_count}"
        for profile in result.selected_profiles
    )


def _condition_deep_dive_text(result: H4StateOutcomeDeepDiveResult, condition_label: str) -> str:
    rows = [row for row in result.outcome_statistics_rows if row.condition_label == condition_label]
    if not rows:
        return f"No selected profiles for {condition_label}."
    lines = []
    for row in sorted(rows, key=lambda item: (item.profile_type, item.forward_window)):
        lines.append(
            "- "
            f"FW {row.forward_window} ({row.profile_type}): sample={row.total_sample_size}, "
            f"scenarios={row.scenario_count}, forward_range={_fmt(row.average_forward_range_pips)}, "
            f"outcome_magnitude={_fmt(row.average_outcome_magnitude_pips)}, "
            f"direction_alignment={_fmt(row.average_direction_alignment_rate)}, "
            f"dispersion={row.outcome_profile_stability_class}, diagnostic={row.outcome_profile_diagnostic}"
        )
    return "\n".join(lines)


def _sample_constrained_text(result: H4StateOutcomeDeepDiveResult) -> str:
    rows = [row for row in result.selected_profiles if row.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION"]
    if not rows:
        return "No sample-constrained H4 state observations were selected."
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


def _readiness_text(rows: list[H4StateDeepDiveSummaryRow]) -> str:
    if not rows:
        return "No H4 state deep dive summaries were available."
    return "\n".join(
        "- "
        f"{row.condition_label}: profiles={row.profile_count}, ready={row.research_ready_profile_count}, "
        f"sample_review={row.sample_constrained_observation_count}, "
        f"scenario_sensitive={row.scenario_sensitive_observation_count}, "
        f"diagnostic={row.state_deep_dive_diagnostic}"
        for row in rows
    )


def _fmt(value: float) -> str:
    return f"{value:.4f}"
