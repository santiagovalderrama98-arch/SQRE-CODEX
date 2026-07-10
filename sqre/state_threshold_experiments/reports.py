"""Reports for SQRE state threshold experiments."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.state_threshold_experiments.models import (
    StateThresholdExperimentMetricsRow,
    StateThresholdExperimentSummary,
)


SUMMARY_COLUMNS = [
    "Experiment_Run_ID",
    "Profile_ID",
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Status",
    "Message",
    "Period_Start",
    "Period_End",
    "OHLC_Rows",
    "Structures_Detected",
    "Average_Structure_Duration",
    "Average_Structural_Confidence",
    "States_Generated",
    "Unique_States",
    "Most_Common_State",
    "Most_Common_State_Ratio",
    "Directional_Displacement_Count",
    "Directional_Expansion_Count",
    "Directional_Drift_Count",
    "Volatile_Rotation_Count",
    "Complex_Consolidation_Count",
    "Neutral_Compression_Count",
    "Low_Quality_Structure_Count",
    "Unclassified_Count",
    "Directional_State_Ratio",
    "Compression_Consolidation_Ratio",
    "Volatile_Rotation_Ratio",
    "Unclassified_Rate",
    "Low_Quality_Rate",
    "Average_State_Confidence",
    "Transitions_Generated",
    "Unique_Transitions",
    "Most_Common_Transition",
    "State_Change_Rate",
    "Direction_Change_Rate",
    "Average_Transition_Stability",
    "Conditions_Evaluated",
    "Condition_Summary_Rows",
    "Low_Sample_Conditions_Research",
    "Research_Low_Sample_Rate",
    "Price_Outcomes_Generated",
    "Price_Outcome_Summary_Rows",
    "Low_Sample_Conditions_Price_Outcome",
    "Price_Outcome_Low_Sample_Rate",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Average_Forward_Close_Return_Pips",
    "Relative_Most_Common_State_Ratio_vs_Baseline",
    "Relative_Directional_State_Ratio_vs_Baseline",
    "Relative_State_Diversity_Change_vs_Baseline",
    "Relative_Volatile_Rotation_Ratio_vs_Baseline",
    "Relative_Compression_Consolidation_Ratio_vs_Baseline",
    "Relative_Unclassified_Rate_vs_Baseline",
    "Relative_Low_Quality_Rate_vs_Baseline",
    "Relative_Forward_Range_Change_vs_Baseline",
    "Experiment_Notes",
]


def write_state_threshold_experiment_summary_csv(
    path: Path | str,
    rows: list[StateThresholdExperimentMetricsRow],
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_summary_row(row) for row in rows], columns=SUMMARY_COLUMNS).to_csv(output_path, index=False)
    return output_path


def write_state_threshold_experiment_report(
    path: Path | str,
    summary: StateThresholdExperimentSummary,
    rows: list[StateThresholdExperimentMetricsRow],
) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(summary, rows), encoding="utf-8")
    return report_path


def _summary_row(row: StateThresholdExperimentMetricsRow) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw[_snake(column)] for column in SUMMARY_COLUMNS}


def _build_report(summary: StateThresholdExperimentSummary, rows: list[StateThresholdExperimentMetricsRow]) -> str:
    lines = [
        "SQRE State Threshold Experiment Report",
        "======================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        f"Experiment Name: {summary.experiment_name}",
        f"Runs Configured: {summary.runs_configured}",
        f"Runs Completed: {summary.runs_completed}",
        f"Runs Missing Input: {summary.runs_missing_input}",
        f"Runs Failed: {summary.runs_failed}",
        f"Summary Rows: {summary.summary_rows}",
        "",
        "Experiment Scope",
        "----------------",
        "- Optional Market State threshold profiles",
        "- H4 and D1 scenarios",
        "- Baseline profile comparisons",
        "- Descriptive sensitivity analysis only",
        "",
        "Profile Overview",
        "----------------",
    ]
    lines.extend(_profile_lines(rows))
    lines.extend(["", "State Distribution Comparison", "-----------------------------"])
    lines.extend(_state_distribution_lines(rows))
    lines.extend(["", "Transition Sensitivity", "----------------------"])
    lines.extend(_transition_lines(rows))
    lines.extend(["", "Research and Price Outcome Sensitivity", "--------------------------------------"])
    lines.extend(_research_lines(rows))
    lines.extend(["", "Key Observations", "----------------"])
    lines.extend(_observation_lines(rows))
    lines.extend(
        [
            "",
            "Potential Follow-Up Areas",
            "-------------------------",
            "- Review whether directional_stricter reduces directional concentration.",
            "- Review whether consolidation_sensitive increases non-directional classification without excessive unclassified or low-quality states.",
            "- Review whether balanced_high_tf improves state diversity while preserving classification confidence.",
            "- Consider a later production candidate config only after repeated validation.",
            "",
            "Do Not Change Yet",
            "-----------------",
            "- No production thresholds were modified.",
            "- No runtime defaults were modified.",
            "- No Decision Engine was added.",
            "- No operational market action logic was added.",
            "",
            "Limitations",
            "-----------",
            "- Experiments are diagnostic.",
            "- Results depend on the selected processed datasets.",
            "- Relative changes are descriptive.",
            "- No profile ranking is produced.",
            "- No execution guidance is produced.",
            "",
        ]
    )
    return "\n".join(lines)


def _profile_lines(rows: list[StateThresholdExperimentMetricsRow]) -> list[str]:
    if not rows:
        return ["- No experiment rows available."]
    profile_ids = sorted({row.profile_id for row in rows})
    return [f"- {profile_id}: rows={sum(1 for row in rows if row.profile_id == profile_id)}" for profile_id in profile_ids]


def _state_distribution_lines(rows: list[StateThresholdExperimentMetricsRow]) -> list[str]:
    completed = _completed(rows)
    if not completed:
        return ["- No completed state distribution metrics available."]
    return [
        "- "
        f"{row.profile_id} {row.scenario_id}: "
        f"states={row.states_generated}, diversity={row.unique_states}, "
        f"most_common={row.most_common_state}, most_common_ratio={row.most_common_state_ratio:.4f}, "
        f"directional_ratio={row.directional_state_ratio:.4f}, "
        f"compression_consolidation_ratio={row.compression_consolidation_ratio:.4f}, "
        f"volatile_rotation_ratio={row.volatile_rotation_ratio:.4f}, "
        f"unclassified_rate={row.unclassified_rate:.4f}, "
        f"low_quality_rate={row.low_quality_rate:.4f}"
        for row in completed
    ]


def _transition_lines(rows: list[StateThresholdExperimentMetricsRow]) -> list[str]:
    completed = _completed(rows)
    if not completed:
        return ["- No completed transition metrics available."]
    return [
        "- "
        f"{row.profile_id} {row.scenario_id}: "
        f"transitions={row.transitions_generated}, unique_transitions={row.unique_transitions}, "
        f"most_common_transition={row.most_common_transition}, "
        f"state_change_rate={row.state_change_rate:.4f}, "
        f"direction_change_rate={row.direction_change_rate:.4f}, "
        f"transition_stability={row.average_transition_stability:.4f}"
        for row in completed
    ]


def _research_lines(rows: list[StateThresholdExperimentMetricsRow]) -> list[str]:
    completed = _completed(rows)
    if not completed:
        return ["- No completed research metrics available."]
    return [
        "- "
        f"{row.profile_id} {row.scenario_id}: "
        f"conditions={row.conditions_evaluated}, "
        f"research_low_sample_rate={row.research_low_sample_rate:.4f}, "
        f"price_outcome_rows={row.price_outcome_summary_rows}, "
        f"price_outcome_low_sample_rate={row.price_outcome_low_sample_rate:.4f}, "
        f"avg_forward_range_pips={row.average_forward_range_pips:.4f}, "
        f"direction_alignment_rate={row.direction_alignment_rate:.4f}"
        for row in completed
    ]


def _observation_lines(rows: list[StateThresholdExperimentMetricsRow]) -> list[str]:
    if not rows:
        return ["- No experiment metrics available."]
    completed = _completed(rows)
    if not completed:
        return ["- No completed experiment metrics available for comparison."]
    compared = [row for row in completed if row.profile_id != "state_baseline"]
    lines = [
        f"- Completed or reused rows available for diagnostic comparison: {len(completed)}.",
        f"- Non-baseline comparison rows available: {len(compared)}.",
    ]
    lines.extend(_relative_change_lines(compared))
    return lines


def _relative_change_lines(rows: list[StateThresholdExperimentMetricsRow]) -> list[str]:
    if not rows:
        return ["- Baseline comparison rows are unavailable."]
    return [
        "- "
        f"{row.experiment_run_id}: directional_change={row.relative_directional_state_ratio_vs_baseline:.4f}, "
        f"diversity_change={row.relative_state_diversity_change_vs_baseline:.4f}, "
        f"unclassified_change={row.relative_unclassified_rate_vs_baseline:.4f}, "
        f"forward_range_change={row.relative_forward_range_change_vs_baseline:.4f}."
        for row in rows
    ]


def _completed(rows: list[StateThresholdExperimentMetricsRow]) -> list[StateThresholdExperimentMetricsRow]:
    return [row for row in rows if row.status in {"COMPLETED", "SKIPPED"}]


def _snake(column: str) -> str:
    return column.lower()
