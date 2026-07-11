"""CSV and text reports for expanded historical calibration review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.expanded_calibration_review.models import (
    ExpandedCalibrationFinding,
    ExpandedCalibrationReviewSummary,
    TimeframeCalibrationReviewRow,
)


SUMMARY_COLUMNS = [
    "Timeframe",
    "Scenario_Count",
    "Scenario_IDs",
    "Average_OHLC_Rows",
    "Total_OHLC_Rows",
    "Average_Structures_Detected",
    "Min_Structures_Detected",
    "Max_Structures_Detected",
    "Structure_Count_Range",
    "Structure_Count_CV",
    "Average_Structure_Duration",
    "Min_Average_Structure_Duration",
    "Max_Average_Structure_Duration",
    "Structure_Duration_CV",
    "Average_Unique_States",
    "Min_Unique_States",
    "Max_Unique_States",
    "State_Diversity_Range",
    "Most_Common_State_Mode",
    "Directional_Displacement_Total",
    "Directional_Expansion_Total",
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
    "Min_Forward_Range_Pips",
    "Max_Forward_Range_Pips",
    "Forward_Range_CV",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Min_Direction_Alignment_Rate",
    "Max_Direction_Alignment_Rate",
    "Average_Low_Sample_Conditions_Research",
    "Average_Low_Sample_Conditions_Price_Outcome",
    "Max_Low_Sample_Conditions_Research",
    "Max_Low_Sample_Conditions_Price_Outcome",
    "Structural_Stability_Flag",
    "State_Diversity_Flag",
    "Low_Sample_Pressure_Flag",
    "Forward_Range_Regime_Sensitivity_Flag",
    "Unclassified_Pressure_Flag",
    "Low_Quality_Pressure_Flag",
    "Diagnostic_Profile",
    "Recommended_Follow_Up",
]


def write_expanded_calibration_review_summary_csv(
    path: Path | str,
    rows: list[TimeframeCalibrationReviewRow],
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_summary_row(row) for row in rows], columns=SUMMARY_COLUMNS).to_csv(output_path, index=False)


def write_expanded_calibration_review_report(
    path: Path | str,
    review_summary: ExpandedCalibrationReviewSummary,
    rows: list[TimeframeCalibrationReviewRow],
    findings: list[ExpandedCalibrationFinding],
) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(review_summary, rows, findings), encoding="utf-8")


def _summary_row(row: TimeframeCalibrationReviewRow) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw[_snake(column)] for column in SUMMARY_COLUMNS}


def _build_report(
    review_summary: ExpandedCalibrationReviewSummary,
    rows: list[TimeframeCalibrationReviewRow],
    findings: list[ExpandedCalibrationFinding],
) -> str:
    lines = [
        "SQRE Expanded Historical Calibration Review",
        "==========================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        f"Input Summaries: {', '.join(review_summary.input_files) if review_summary.input_files else 'NONE'}",
        f"Rows Loaded: {review_summary.rows_loaded}",
        f"Timeframes Reviewed: {review_summary.timeframes_reviewed}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
    ]
    lines.extend(_executive_lines(rows))
    lines.extend(["", "Timeframe Overview", "------------------"])
    lines.extend(_overview_lines(rows))
    lines.extend(["", "Structural Stability Review", "---------------------------"])
    lines.extend(_flag_lines(rows, "structural_stability_flag", "structure_count_cv"))
    lines.extend(["", "State Diversity Review", "----------------------"])
    lines.extend(_state_diversity_lines(rows))
    lines.extend(["", "Low Sample Pressure Review", "--------------------------"])
    lines.extend(_low_sample_lines(rows))
    lines.extend(["", "Price Outcome Regime Sensitivity Review", "---------------------------------------"])
    lines.extend(_forward_range_lines(rows))
    lines.extend(["", "Diagnostic Findings", "-------------------"])
    lines.extend(_finding_lines(findings))
    lines.extend(
        [
            "",
            "Potential Follow-Up Areas",
            "-------------------------",
            "- Regime-normalized price outcome analysis",
            "- H1-specific calibration experiments",
            "- M5-specific microstructure calibration",
            "- Continued H4/D1 monitoring",
            "",
            "Do Not Change Yet",
            "-----------------",
            "- No production defaults were modified.",
            "- No thresholds were modified.",
            "- No Decision Engine was added.",
            "- No operational logic was added.",
            "",
            "Limitations",
            "-----------",
            "- Review depends on available processed datasets.",
            "- Partial/missing samples are excluded from the summary input.",
            "- Findings are descriptive.",
            "- No timeframe ranking is produced.",
            "",
        ]
    )
    return "\n".join(lines)


def _executive_lines(rows: list[TimeframeCalibrationReviewRow]) -> list[str]:
    if not rows:
        return ["- No timeframe rows available."]
    return [f"- {row.timeframe}: {row.diagnostic_profile}" for row in rows]


def _overview_lines(rows: list[TimeframeCalibrationReviewRow]) -> list[str]:
    if not rows:
        return ["- No timeframe rows available."]
    return [
        f"- {row.timeframe}: scenarios={row.scenario_count}, "
        f"avg_structures={row.average_structures_detected:.4f}, "
        f"structure_count_cv={row.structure_count_cv:.4f}, "
        f"avg_unique_states={row.average_unique_states:.4f}, "
        f"state_mode={row.most_common_state_mode or 'NONE'}, "
        f"avg_forward_range={row.average_forward_range_pips:.4f}, "
        f"direction_alignment_rate={row.average_direction_alignment_rate:.4f}, "
        f"low_sample_avg=({row.average_low_sample_conditions_research:.4f}, "
        f"{row.average_low_sample_conditions_price_outcome:.4f}), "
        f"profile={row.diagnostic_profile}, follow_up={row.recommended_follow_up}"
        for row in rows
    ]


def _flag_lines(rows: list[TimeframeCalibrationReviewRow], flag_attr: str, metric_attr: str) -> list[str]:
    if not rows:
        return ["- No structural stability diagnostics available."]
    return [
        f"- {row.timeframe}: {getattr(row, flag_attr)}, {metric_attr}={getattr(row, metric_attr):.4f}"
        for row in rows
    ]


def _state_diversity_lines(rows: list[TimeframeCalibrationReviewRow]) -> list[str]:
    if not rows:
        return ["- No state diversity diagnostics available."]
    return [
        f"- {row.timeframe}: {row.state_diversity_flag}, average_unique_states={row.average_unique_states:.4f}, "
        f"dominant_state={row.most_common_state_mode or 'NONE'}"
        for row in rows
    ]


def _low_sample_lines(rows: list[TimeframeCalibrationReviewRow]) -> list[str]:
    if not rows:
        return ["- No low sample diagnostics available."]
    return [
        f"- {row.timeframe}: {row.low_sample_pressure_flag}, "
        f"research_avg={row.average_low_sample_conditions_research:.4f}, "
        f"price_outcome_avg={row.average_low_sample_conditions_price_outcome:.4f}"
        for row in rows
    ]


def _forward_range_lines(rows: list[TimeframeCalibrationReviewRow]) -> list[str]:
    if not rows:
        return ["- No forward range diagnostics available."]
    return [
        f"- {row.timeframe}: {row.forward_range_regime_sensitivity_flag}, "
        f"forward_range_cv={row.forward_range_cv:.4f}, "
        f"range_min={row.min_forward_range_pips:.4f}, range_max={row.max_forward_range_pips:.4f}"
        for row in rows
    ]


def _finding_lines(findings: list[ExpandedCalibrationFinding]) -> list[str]:
    if not findings:
        return ["- No findings generated."]
    return [
        f"- {finding.timeframe}: type={finding.finding_type}, flag={finding.flag}. {finding.message}"
        for finding in findings
    ]


def _snake(column: str) -> str:
    return column.lower()
