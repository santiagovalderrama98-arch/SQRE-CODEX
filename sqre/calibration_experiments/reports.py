"""Reports for SQRE calibration experiments."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.calibration_experiments.models import CalibrationExperimentSummary, ExperimentMetricsRow


SUMMARY_COLUMNS = [
    "Experiment_Run_ID",
    "Experiment_Type",
    "Experiment_ID",
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Status",
    "Message",
    "Period_Start",
    "Period_End",
    "OHLC_Rows",
    "Max_Structure_Duration_Seconds",
    "Minimum_Sample_Size",
    "Forward_Windows",
    "Structures_Detected",
    "Average_Structure_Duration",
    "Duration_Utilization_Ratio",
    "Average_Price_Displacement",
    "Most_Common_Direction",
    "Average_Persistence_Index",
    "Average_Structural_Complexity",
    "Average_Structural_Stability",
    "Average_Structural_Confidence",
    "States_Generated",
    "Unique_States",
    "Most_Common_State",
    "Most_Common_State_Ratio",
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
    "Average_Transition_Magnitude",
    "Average_Transition_Stability",
    "Conditions_Evaluated",
    "Condition_Summary_Rows",
    "Low_Sample_Conditions_Research",
    "Research_Low_Sample_Rate",
    "Price_Outcomes_Generated",
    "Price_Outcome_Summary_Rows",
    "Price_Outcome_Distribution_Rows",
    "Low_Sample_Conditions_Price_Outcome",
    "Price_Outcome_Low_Sample_Rate",
    "Average_Forward_Close_Return_Pips",
    "Median_Forward_Close_Return_Pips",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Relative_Structure_Count_Change_vs_Baseline",
    "Relative_Duration_Change_vs_Baseline",
    "Relative_State_Diversity_Change_vs_Baseline",
    "Relative_Forward_Range_Change_vs_Baseline",
    "Experiment_Notes",
]


def write_calibration_experiment_summary_csv(path: Path | str, rows: list[ExperimentMetricsRow]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_summary_row(row) for row in rows], columns=SUMMARY_COLUMNS).to_csv(output_path, index=False)
    return output_path


def write_calibration_experiment_report(
    path: Path | str,
    summary: CalibrationExperimentSummary,
    rows: list[ExperimentMetricsRow],
) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(summary, rows), encoding="utf-8")
    return report_path


def _summary_row(row: ExperimentMetricsRow) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw[_snake(column)] for column in SUMMARY_COLUMNS}


def _build_report(summary: CalibrationExperimentSummary, rows: list[ExperimentMetricsRow]) -> str:
    lines = [
        "SQRE Calibration Experiment Report",
        "==================================",
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
        "- Duration sensitivity experiments",
        "- Sample size sensitivity experiments",
        _timeframe_scope_line(rows),
        "- No Market State threshold changes",
        "",
        "Duration Sensitivity Summary",
        "----------------------------",
    ]
    lines.extend(_duration_lines(rows))
    lines.extend(["", "Sample Size Sensitivity Summary", "-------------------------------"])
    lines.extend(_sample_size_lines(rows))
    lines.extend(["", "Key Observations", "----------------"])
    lines.extend(_observation_lines(rows))
    lines.extend(
        [
            "",
            "Potential Follow-Up Areas",
            "-------------------------",
            "- Review duration limit behavior if duration utilization remains near max under expanded settings.",
            "- Review whether conservative settings fragment structures excessively.",
            "- Review whether expanded settings reduce state diversity excessively.",
            "- Review minimum sample size before later downstream eligibility work.",
            "- Consider a later state-threshold experiment phase.",
            "",
            "Do Not Change Yet",
            "-----------------",
            "- No production thresholds were modified.",
            "- No runtime defaults were modified.",
            "- No Market State thresholds were changed.",
            "- No operational logic was added.",
            "",
            "Limitations",
            "-----------",
            "- Experiments are diagnostic.",
            "- Results depend on processed datasets.",
            "- Relative changes are descriptive.",
            "- No comparative ordering is produced.",
            "- No execution guidance is produced.",
            "",
        ]
    )
    return "\n".join(lines)


def _timeframe_scope_line(rows: list[ExperimentMetricsRow]) -> str:
    timeframes = list(dict.fromkeys(row.timeframe for row in rows if row.timeframe))
    if not timeframes:
        return "- Configured timeframe scenarios"
    if len(timeframes) == 1:
        return f"- {timeframes[0]} scenarios"
    if len(timeframes) == 2:
        return f"- {timeframes[0]} and {timeframes[1]} scenarios"
    return f"- {', '.join(timeframes[:-1])}, and {timeframes[-1]} scenarios"


def _duration_lines(rows: list[ExperimentMetricsRow]) -> list[str]:
    duration_rows = [row for row in rows if row.experiment_type == "DURATION"]
    if not duration_rows:
        return ["- No duration experiment rows available."]
    return [
        "- "
        f"{row.timeframe} {row.scenario_id} {row.experiment_id}: "
        f"structures={row.structures_detected}, "
        f"avg_duration={row.average_structure_duration:.2f}, "
        f"duration_ratio={row.duration_utilization_ratio:.4f}, "
        f"states={row.states_generated}, diversity={row.unique_states}, "
        f"directional_ratio={row.directional_state_ratio:.4f}, "
        f"avg_forward_range_pips={row.average_forward_range_pips:.4f}, "
        f"research_low_sample_rate={row.research_low_sample_rate:.4f}, "
        f"price_outcome_low_sample_rate={row.price_outcome_low_sample_rate:.4f}, "
        f"status={row.status}"
        for row in duration_rows
    ]


def _sample_size_lines(rows: list[ExperimentMetricsRow]) -> list[str]:
    sample_rows = [row for row in rows if row.experiment_type == "SAMPLE_SIZE"]
    if not sample_rows:
        return ["- No sample size experiment rows available."]
    return [
        "- "
        f"{row.timeframe} {row.scenario_id} {row.experiment_id}: "
        f"minimum_sample_size={row.minimum_sample_size}, "
        f"research_low_sample_rate={row.research_low_sample_rate:.4f}, "
        f"price_outcome_low_sample_rate={row.price_outcome_low_sample_rate:.4f}, "
        f"condition_rows={row.condition_summary_rows}, "
        f"price_outcome_rows={row.price_outcome_summary_rows}, "
        f"status={row.status}"
        for row in sample_rows
    ]


def _observation_lines(rows: list[ExperimentMetricsRow]) -> list[str]:
    if not rows:
        return ["- No experiment metrics available."]
    completed = [row for row in rows if row.status in {"COMPLETED", "SKIPPED"}]
    if not completed:
        return ["- No completed experiment metrics available for comparison."]
    high_duration = [row for row in completed if row.duration_utilization_ratio >= 0.85]
    high_low_sample = [
        row for row in completed if row.research_low_sample_rate >= 0.5 or row.price_outcome_low_sample_rate >= 0.5
    ]
    lines = [
        f"- Completed or reused rows available for diagnostic comparison: {len(completed)}.",
        f"- Rows with duration utilization at or above 0.85: {len(high_duration)}.",
        f"- Rows with low-sample rate at or above 0.50: {len(high_low_sample)}.",
    ]
    lines.extend(_relative_change_lines(completed))
    return lines


def _relative_change_lines(rows: list[ExperimentMetricsRow]) -> list[str]:
    changed = [row for row in rows if row.relative_structure_count_change_vs_baseline != 0]
    if not changed:
        return ["- Structure count changes versus baseline are stable or unavailable."]
    return [
        "- "
        f"{row.experiment_run_id}: structure_count_change={row.relative_structure_count_change_vs_baseline:.4f}, "
        f"duration_change={row.relative_duration_change_vs_baseline:.4f}, "
        f"state_diversity_change={row.relative_state_diversity_change_vs_baseline:.4f}, "
        f"forward_range_change={row.relative_forward_range_change_vs_baseline:.4f}."
        for row in changed
    ]


def _snake(column: str) -> str:
    return column.lower()
