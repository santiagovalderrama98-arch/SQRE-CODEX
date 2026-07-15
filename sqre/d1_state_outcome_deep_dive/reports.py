"""CSV and text report writers for D1 state outcome deep dive."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.d1_state_outcome_deep_dive.findings import state_summary_diagnostic, state_summary_follow_up
from sqre.d1_state_outcome_deep_dive.loader import optional_input_file_status
from sqre.d1_state_outcome_deep_dive.models import (
    D1StateOutcomeDeepDiveResult,
    OutcomeStatisticsRow,
    StateDeepDiveSummaryRow,
)
from sqre.d1_state_outcome_deep_dive.outcome_statistics import mean


PROFILE_INVENTORY_COLUMNS = [
    "Condition_Label",
    "Forward_Window",
    "Profile_Type",
    "Regime_Count",
    "Regimes_Present",
    "Scenario_Count",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Regime",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Direction_Alignment_CV",
    "Sample_Adequacy_Class",
    "Regime_Coverage_Class",
    "Dispersion_Class",
    "Sensitivity_Class",
    "Condition_Research_Class",
    "Profile_Diagnostic",
    "Recommended_Follow_Up",
]

REGIME_BREAKDOWN_COLUMNS = [
    "Condition_Label",
    "Forward_Window",
    "Profile_Type",
    "Regime_ID",
    "Regime_Label",
    "Scenario_ID",
    "Sample_Size",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Favorable_Displacement_Pips",
    "Average_Adverse_Displacement_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Sample_Adequacy_Flag",
    "Regime_Observation_Diagnostic",
]

OUTCOME_STATISTICS_COLUMNS = [
    "Condition_Label",
    "Forward_Window",
    "Profile_Type",
    "Regime_Count",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Regime",
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
    "Regime_ID",
    "Regime_Label",
    "Scenario_ID",
    "Sample_Size",
    "Forward_Close_Return_vs_Profile_Avg",
    "Forward_Range_vs_Profile_Avg",
    "Outcome_Magnitude_vs_Profile_Avg",
    "Direction_Alignment_vs_Profile_Avg",
    "Regime_Deviation_Class",
    "Regime_Comparison_Diagnostic",
]

SUMMARY_COLUMNS = [
    "Condition_Label",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Regime_Sensitive_Observation_Count",
    "Total_Sample_Size",
    "Average_Regime_Count",
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


def build_state_deep_dive_summary(statistics_rows: list[OutcomeStatisticsRow]) -> list[StateDeepDiveSummaryRow]:
    grouped: dict[str, list[OutcomeStatisticsRow]] = defaultdict(list)
    for row in statistics_rows:
        grouped[row.condition_label].append(row)
    summaries: list[StateDeepDiveSummaryRow] = []
    for label, rows in sorted(grouped.items()):
        ready = sum(1 for row in rows if row.profile_type == "RESEARCH_READY")
        sensitive = sum(1 for row in rows if row.profile_type == "REGIME_SENSITIVE_OBSERVATION")
        high = sum(1 for row in rows if row.outcome_profile_stability_class == "HIGH_DISPERSION")
        summaries.append(
            StateDeepDiveSummaryRow(
                condition_label=label,
                profile_count=len(rows),
                research_ready_profile_count=ready,
                regime_sensitive_observation_count=sensitive,
                total_sample_size=sum(row.total_sample_size for row in rows),
                average_regime_count=mean([row.regime_count for row in rows]),
                average_forward_range_pips=mean([row.average_forward_range_pips for row in rows]),
                average_outcome_magnitude_pips=mean([row.average_outcome_magnitude_pips for row in rows]),
                average_direction_alignment_rate=mean([row.average_direction_alignment_rate for row in rows]),
                average_forward_range_cv=mean([row.forward_range_cv for row in rows]),
                average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in rows]),
                stable_profile_count=sum(1 for row in rows if row.outcome_profile_stability_class == "STABLE_DESCRIPTIVE"),
                moderate_profile_count=sum(1 for row in rows if row.outcome_profile_stability_class == "MODERATE_DISPERSION"),
                high_dispersion_profile_count=high,
                state_deep_dive_diagnostic=state_summary_diagnostic(ready, sensitive, high),
                recommended_follow_up=state_summary_follow_up(sensitive, high),
            )
        )
    return summaries


def write_deep_dive_outputs(result: D1StateOutcomeDeepDiveResult) -> D1StateOutcomeDeepDiveResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "d1_state_deep_dive_profile_inventory.csv", result.selected_profiles, PROFILE_INVENTORY_COLUMNS)
    _write_rows(result.output_dir / "d1_state_regime_breakdown.csv", result.regime_breakdown_rows, REGIME_BREAKDOWN_COLUMNS)
    _write_rows(result.output_dir / "d1_state_outcome_statistics.csv", result.outcome_statistics_rows, OUTCOME_STATISTICS_COLUMNS)
    _write_rows(result.output_dir / "d1_state_regime_comparison_matrix.csv", result.comparison_rows, COMPARISON_COLUMNS)
    _write_rows(result.output_dir / "d1_state_deep_dive_summary.csv", result.summary_rows, SUMMARY_COLUMNS)
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: D1StateOutcomeDeepDiveResult) -> str:
    optional_status = optional_input_file_status(result.outcome_review_dir, result.regime_research_dir)
    lines = [
        "SQRE D1 Research-Ready State Outcome Deep Dive",
        "=============================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        f"Outcome Review Directory: {result.outcome_review_dir}",
        f"Regime Research Directory: {result.regime_research_dir}",
        f"Optional Input Availability: {_optional_status_text(optional_status)}",
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Profiles Loaded",
        "---------------",
        f"Research-Ready Profiles Loaded: {result.research_ready_profiles_loaded}",
        f"Regime-Sensitive Profiles Loaded: {result.regime_sensitive_profiles_loaded}",
        f"Regime Outcomes Loaded: {result.regime_outcomes_loaded}",
        f"Selected State Profiles: {len(result.selected_profiles)}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        _executive_summary(result),
        "",
        "Selected State Profiles",
        "-----------------------",
        _selected_profiles_text(result),
        "",
        "DIRECTIONAL_EXPANSION Deep Dive",
        "-------------------------------",
        _condition_deep_dive_text(result, "DIRECTIONAL_EXPANSION"),
        "",
        "DIRECTIONAL_DISPLACEMENT Deep Dive",
        "----------------------------------",
        _condition_deep_dive_text(result, "DIRECTIONAL_DISPLACEMENT"),
        "",
        "Regime Breakdown Review",
        "-----------------------",
        "Regime-period observations are scenario-period labels and do not make macro causal claims.",
        f"Regime breakdown rows: {len(result.regime_breakdown_rows)}",
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
        "- D1 transition outcome deep dive",
        "- H4 state outcome deep dive",
        "- H4 transition outcome deep dive",
        "- H4/D1 condition-family aggregation",
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
        "- Regimes are scenario-period labels, not macroeconomic causal classifications.",
        "- Findings depend on available D1 historical samples.",
        "- Findings are descriptive.",
        "- No comparative ordering is produced.",
        "- No production calibration decision is made.",
        "- No operational decision is produced.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    records = [_row_record(row, columns) for row in rows]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _row_record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(_field_name(column), "") for column in columns}


def _field_name(column: str) -> str:
    return column.replace("_vs_", "_vs_").lower()


def _optional_status_text(status: dict[str, bool]) -> str:
    return ", ".join(f"{name}={'present' if present else 'missing'}" for name, present in sorted(status.items()))


def _executive_summary(result: D1StateOutcomeDeepDiveResult) -> str:
    ready = sum(1 for profile in result.selected_profiles if profile.profile_type == "RESEARCH_READY")
    sensitive = sum(1 for profile in result.selected_profiles if profile.profile_type == "REGIME_SENSITIVE_OBSERVATION")
    return "\n".join(
        [
            f"Research-ready state profiles selected: {ready}",
            f"Regime-sensitive observation profiles selected: {sensitive}",
            f"Outcome statistics rows: {len(result.outcome_statistics_rows)}",
            f"Comparison matrix rows: {len(result.comparison_rows)}",
            f"Summary rows: {len(result.summary_rows)}",
        ]
    )


def _selected_profiles_text(result: D1StateOutcomeDeepDiveResult) -> str:
    if not result.selected_profiles:
        return "No selected state profiles were available."
    return "\n".join(
        "- "
        f"{profile.profile_type}: {profile.condition_label} FW={profile.forward_window} "
        f"sample={profile.total_sample_size} regimes={profile.regime_count}"
        for profile in result.selected_profiles
    )


def _condition_deep_dive_text(result: D1StateOutcomeDeepDiveResult, condition_label: str) -> str:
    rows = [row for row in result.outcome_statistics_rows if row.condition_label == condition_label]
    if not rows:
        return f"No selected profiles for {condition_label}."
    lines = []
    for row in sorted(rows, key=lambda item: (item.profile_type, item.forward_window)):
        lines.append(
            "- "
            f"FW {row.forward_window} ({row.profile_type}): sample={row.total_sample_size}, "
            f"regimes={row.regime_count}, forward_range={_fmt(row.average_forward_range_pips)}, "
            f"outcome_magnitude={_fmt(row.average_outcome_magnitude_pips)}, "
            f"direction_alignment={_fmt(row.average_direction_alignment_rate)}, "
            f"dispersion={row.outcome_profile_stability_class}, diagnostic={row.outcome_profile_diagnostic}"
        )
    return "\n".join(lines)


def _dispersion_text(rows: list[OutcomeStatisticsRow]) -> str:
    if not rows:
        return "No outcome statistics rows were available."
    stable = sum(1 for row in rows if row.outcome_profile_stability_class == "STABLE_DESCRIPTIVE")
    moderate = sum(1 for row in rows if row.outcome_profile_stability_class == "MODERATE_DISPERSION")
    high = sum(1 for row in rows if row.outcome_profile_stability_class == "HIGH_DISPERSION")
    return f"Stable profiles: {stable}\nModerate dispersion profiles: {moderate}\nHigh dispersion profiles: {high}"


def _readiness_text(rows: list[StateDeepDiveSummaryRow]) -> str:
    if not rows:
        return "No state deep dive summaries were available."
    return "\n".join(
        "- "
        f"{row.condition_label}: profiles={row.profile_count}, ready={row.research_ready_profile_count}, "
        f"regime_sensitive_observations={row.regime_sensitive_observation_count}, diagnostic={row.state_deep_dive_diagnostic}"
        for row in rows
    )


def _fmt(value: float) -> str:
    return f"{value:.4f}"
