"""Reports for M15 duration calibration review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from sqre.m15_duration_calibration_review.models import (
    M15DurationReviewFinding,
    M15DurationReviewResult,
    M15DurationReviewRow,
)


SUMMARY_COLUMNS = [
    "Timeframe",
    "Experiment_Profile",
    "Scenario_Count",
    "Completed_Run_Count",
    "Failed_Run_Count",
    "Missing_Input_Count",
    "Scenario_IDs",
    "Max_Structure_Duration_Seconds",
    "Average_Structures_Detected",
    "Min_Structures_Detected",
    "Max_Structures_Detected",
    "Structure_Count_Range",
    "Structure_Count_CV",
    "Average_Structure_Duration",
    "Average_Duration_Utilization_Ratio",
    "Min_Duration_Utilization_Ratio",
    "Max_Duration_Utilization_Ratio",
    "Average_Unique_States",
    "Min_Unique_States",
    "Max_Unique_States",
    "State_Diversity_Range",
    "Most_Common_State_Mode",
    "Directional_Displacement_Total",
    "Directional_Expansion_Total",
    "Directional_Drift_Total",
    "Volatile_Rotation_Total",
    "Complex_Consolidation_Total",
    "Low_Quality_Structure_Total",
    "Unclassified_Total",
    "Average_Directional_State_Ratio",
    "Average_Complex_Consolidation_Ratio",
    "Average_Volatile_Rotation_Ratio",
    "Average_Low_Quality_Rate",
    "Average_Unclassified_Rate",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Average_Low_Sample_Conditions_Research",
    "Average_Low_Sample_Conditions_Price_Outcome",
    "Max_Low_Sample_Conditions_Research",
    "Max_Low_Sample_Conditions_Price_Outcome",
    "Baseline_Profile",
    "Baseline_Structures_Detected",
    "Relative_Structure_Change_vs_Baseline",
    "Relative_Duration_Utilization_Change_vs_Baseline",
    "Relative_Unique_States_Change_vs_Baseline",
    "Relative_Low_Sample_Research_Change_vs_Baseline",
    "Relative_Low_Sample_Price_Outcome_Change_vs_Baseline",
    "Relative_Forward_Range_Change_vs_Baseline",
    "Relative_Direction_Alignment_Change_vs_Baseline",
    "Structure_Stability_Flag",
    "Duration_Utilization_Flag",
    "State_Diversity_Flag",
    "Low_Sample_Pressure_Flag",
    "Fragmentation_Flag",
    "Compression_Flag",
    "Profile_Diagnostic",
    "Recommended_Follow_Up",
]


def write_m15_duration_review_summary_csv(path: Path | str, rows: list[M15DurationReviewRow]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_summary_row(row) for row in rows], columns=SUMMARY_COLUMNS).to_csv(output_path, index=False)


def write_m15_duration_review_report(
    path: Path | str,
    result: M15DurationReviewResult,
    findings: list[M15DurationReviewFinding],
) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(result, findings), encoding="utf-8")


def _summary_row(row: M15DurationReviewRow) -> dict[str, Any]:
    raw = asdict(row)
    return {_column: _blank_none(raw[_snake(_column)]) for _column in SUMMARY_COLUMNS}


def _build_report(result: M15DurationReviewResult, findings: list[M15DurationReviewFinding]) -> str:
    rows = result.rows
    lines = [
        "SQRE M15 Duration Calibration Review",
        "===================================",
        "",
        "Generated At",
        "------------",
        datetime.now(timezone.utc).isoformat(),
        "",
        "Input Experiment Summary",
        "------------------------",
        result.input_experiment_summary,
        "",
        "Rows Loaded",
        "-----------",
        str(result.rows_loaded),
        "",
        "Profiles Reviewed",
        "-----------------",
        str(result.profiles_reviewed),
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
    ]
    lines.extend(_executive_lines(rows))
    lines.extend(["", "Experiment Coverage", "-------------------"])
    lines.extend(_coverage_lines(rows, result.rows_loaded))
    lines.extend(["", "M15 Duration Profile Overview", "-----------------------------"])
    lines.extend(_overview_lines(rows))
    lines.extend(["", "Baseline Comparison Review", "--------------------------"])
    lines.extend(_baseline_lines(rows))
    lines.extend(["", "M15 Diagnostic Review", "---------------------"])
    lines.extend(_diagnostic_lines(rows))
    lines.extend(["", "Diagnostic Findings", "-------------------"])
    lines.extend(_finding_lines(findings))
    lines.extend(
        [
            "",
            "Potential Follow-Up Areas",
            "-------------------------",
            "- M15 duration candidate validation",
            "- M15 price outcome aggregation",
            "- M15 vs H1/M5 comparative diagnostic review",
            "- Continued H4/D1 monitoring as higher-timeframe context",
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
            "- Review depends on available processed M15 datasets.",
            "- Findings are descriptive.",
            "- No comparative ordering is produced.",
            "- No production calibration decision is made.",
            "",
        ]
    )
    return "\n".join(lines)


def _executive_lines(rows: list[M15DurationReviewRow]) -> list[str]:
    if not rows:
        return ["- No M15 duration profile rows available."]
    return [f"- {row.experiment_profile}: {row.profile_diagnostic}" for row in rows]


def _coverage_lines(rows: list[M15DurationReviewRow], rows_loaded: int) -> list[str]:
    completed = sum(row.completed_run_count for row in rows)
    failed = sum(row.failed_run_count for row in rows)
    missing = sum(row.missing_input_count for row in rows)
    scenario_ids = set()
    for row in rows:
        scenario_ids.update(item for item in row.scenario_ids.split(";") if item)
    return [
        f"- Total rows: {rows_loaded}",
        f"- Completed rows: {completed}",
        f"- Failed rows: {failed}",
        f"- Missing rows: {missing}",
        f"- Scenario count: {len(scenario_ids)}",
        f"- Profile count: {len(rows)}",
    ]


def _overview_lines(rows: list[M15DurationReviewRow]) -> list[str]:
    if not rows:
        return ["- No profile overview rows available."]
    return [
        f"- {row.experiment_profile}: scenarios={row.scenario_count}, completed={row.completed_run_count}, "
        f"max_duration={row.max_structure_duration_seconds}, avg_structures={row.average_structures_detected:.4f}, "
        f"structure_cv={row.structure_count_cv:.4f}, "
        f"avg_duration_utilization={row.average_duration_utilization_ratio:.4f}, "
        f"avg_unique_states={row.average_unique_states:.4f}, state_mode={row.most_common_state_mode or 'NONE'}, "
        f"low_sample_avg=({row.average_low_sample_conditions_research:.4f}, "
        f"{row.average_low_sample_conditions_price_outcome:.4f}), "
        f"avg_forward_range={row.average_forward_range_pips:.4f}, "
        f"direction_alignment={row.average_direction_alignment_rate:.4f}, "
        f"diagnostic={row.profile_diagnostic}, follow_up={row.recommended_follow_up}"
        for row in rows
    ]


def _baseline_lines(rows: list[M15DurationReviewRow]) -> list[str]:
    comparison_rows = [row for row in rows if row.experiment_profile != row.baseline_profile]
    if not comparison_rows:
        return ["- No non-baseline duration profiles available."]
    return [
        f"- {row.experiment_profile}: baseline={row.baseline_profile}, "
        f"structure_change={_format_relative(row.relative_structure_change_vs_baseline)}, "
        f"duration_utilization_change={_format_relative(row.relative_duration_utilization_change_vs_baseline)}, "
        f"unique_states_change={_format_relative(row.relative_unique_states_change_vs_baseline)}, "
        f"low_sample_research_change={_format_relative(row.relative_low_sample_research_change_vs_baseline)}, "
        f"forward_range_change={_format_relative(row.relative_forward_range_change_vs_baseline)}"
        for row in comparison_rows
    ]


def _diagnostic_lines(rows: list[M15DurationReviewRow]) -> list[str]:
    if not rows:
        return ["- No M15 diagnostic rows available."]
    return [
        f"- {row.experiment_profile}: {row.profile_diagnostic}; "
        f"fragmentation={row.fragmentation_flag}; compression={row.compression_flag}; "
        f"duration={row.duration_utilization_flag}; low_sample={row.low_sample_pressure_flag}; "
        f"state_diversity={row.state_diversity_flag}"
        for row in rows
    ]


def _finding_lines(findings: list[M15DurationReviewFinding]) -> list[str]:
    if not findings:
        return ["- No findings generated."]
    return [
        f"- {finding.timeframe} {finding.experiment_profile}: "
        f"type={finding.finding_type}, flag={finding.flag}. {finding.message}"
        for finding in findings
    ]


def _format_relative(value: float | None) -> str:
    if value is None:
        return "changed from zero or unavailable"
    return f"{value:.4f}"


def _snake(column: str) -> str:
    return column.lower()


def _blank_none(value: Any) -> Any:
    if value is None:
        return ""
    return value
