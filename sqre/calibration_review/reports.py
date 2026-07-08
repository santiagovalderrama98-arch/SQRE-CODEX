"""CSV and text reports for SQRE calibration review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.calibration_review.models import CalibrationFinding, CalibrationMetricsRow, CalibrationReviewSummary


SUMMARY_COLUMNS = [
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Status",
    "Period_Start",
    "Period_End",
    "OHLC_Rows",
    "Duration_Utilization_Ratio",
    "Most_Common_State_Ratio",
    "Directional_State_Ratio",
    "Compression_Consolidation_Ratio",
    "Volatile_Rotation_Ratio",
    "Unclassified_Rate",
    "Low_Quality_Rate",
    "State_Diversity",
    "Transition_Diversity",
    "State_Change_Rate",
    "Direction_Change_Rate",
    "Transition_Stability",
    "Research_Low_Sample_Rate",
    "Price_Outcome_Low_Sample_Rate",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Direction_Alignment_Rate",
    "Average_Forward_Close_Return_Pips",
    "Duration_Near_Max_Flag",
    "High_State_Dominance_Flag",
    "Low_State_Diversity_Flag",
    "High_Directional_Ratio_Flag",
    "High_Research_Low_Sample_Flag",
    "High_Price_Outcome_Low_Sample_Flag",
    "Calibration_Status",
    "Calibration_Notes",
]


def write_calibration_review_summary_csv(path: Path | str, rows: list[CalibrationMetricsRow]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_summary_row(row) for row in rows], columns=SUMMARY_COLUMNS).to_csv(output_path, index=False)


def write_calibration_review_report(
    path: Path | str,
    review_summary: CalibrationReviewSummary,
    rows: list[CalibrationMetricsRow],
    findings: list[CalibrationFinding],
) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(review_summary, rows, findings), encoding="utf-8")


def _summary_row(row: CalibrationMetricsRow) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw[_snake(column)] for column in SUMMARY_COLUMNS}


def _build_report(
    review_summary: CalibrationReviewSummary,
    rows: list[CalibrationMetricsRow],
    findings: list[CalibrationFinding],
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    watch_review = [finding for finding in findings if finding.severity in {"WATCH", "REVIEW"}]
    lines = [
        "SQRE Calibration Review Report",
        "==============================",
        "",
        f"Generated At: {generated_at}",
        f"Input Files: {', '.join(review_summary.input_files) if review_summary.input_files else 'NONE'}",
        f"Scenarios Loaded: {review_summary.scenarios_loaded}",
        f"Completed Scenarios: {review_summary.completed_scenarios}",
        f"Missing or Failed Scenarios: {review_summary.missing_or_failed_scenarios}",
        f"Summary Rows: {review_summary.summary_rows}",
        f"Findings Generated: {review_summary.finding_count}",
        f"Review Status: {review_summary.review_status}",
        "",
        "Calibration Overview",
        "--------------------",
    ]
    lines.extend(_overview_lines(rows))
    lines.extend(["", "Market Structure Calibration Review", "-----------------------------------"])
    lines.extend(_structure_lines(rows))
    lines.extend(["", "Market States Calibration Review", "--------------------------------"])
    lines.extend(_state_lines(rows))
    lines.extend(["", "Transition Calibration Review", "-----------------------------"])
    lines.extend(_transition_lines(rows))
    lines.extend(["", "Price Outcome Calibration Review", "--------------------------------"])
    lines.extend(_price_outcome_lines(rows))
    lines.extend(["", "Temporal Consistency Review", "---------------------------"])
    lines.extend(_finding_lines(findings, {"TEMPORAL_CONSISTENCY"}))
    lines.extend(["", "Potential Calibration Issues", "----------------------------"])
    lines.extend(_finding_lines(watch_review, {finding.finding_type for finding in watch_review}))
    lines.extend(
        [
            "",
            "Candidate Adjustments for Phase 7.4.1",
            "-------------------------------------",
            "- Review timeframe-specific state thresholds.",
            "- Review whether duration limits are acting as structural termination constraints.",
            "- Review DIRECTIONAL_DISPLACEMENT concentration in H4/D1.",
            "- Review COMPLEX_CONSOLIDATION absence in H4/D1.",
            "- Review minimum sample requirements for low timeframe scenarios.",
            "",
            "Do Not Change Yet",
            "-----------------",
            "- No thresholds were modified.",
            "- No runtime parameters were changed.",
            "- No strategy logic was added.",
            "- No decision logic was added.",
            "",
            "Limitations",
            "-----------",
            "- This review is diagnostic.",
            "- Results depend on processed datasets.",
            "- Cross-timeframe comparisons are descriptive, not rankings.",
            "- Forward close return can be regime-sensitive.",
            "- Low sample conditions require caution.",
            "",
        ]
    )
    return "\n".join(lines)


def _overview_lines(rows: list[CalibrationMetricsRow]) -> list[str]:
    if not rows:
        return ["- No scenario rows available."]
    return [
        f"- {row.scenario_id}: timeframe={row.timeframe}, status={row.calibration_status}, "
        f"duration_ratio={row.duration_utilization_ratio:.4f}, state_ratio={row.most_common_state_ratio:.4f}"
        for row in rows
    ]


def _structure_lines(rows: list[CalibrationMetricsRow]) -> list[str]:
    if not rows:
        return ["- No structure diagnostics available."]
    lines = [
        f"- {row.scenario_id}: duration_utilization={row.duration_utilization_ratio:.4f}, near_max={row.duration_near_max_flag}"
        for row in rows
    ]
    near_max = [row.scenario_id for row in rows if row.duration_near_max_flag]
    lines.append(f"- Scenarios near max duration: {', '.join(near_max) if near_max else 'NONE'}")
    lines.append("- Preliminary interpretation: duration ratios are descriptive and require review before calibration changes.")
    return lines


def _state_lines(rows: list[CalibrationMetricsRow]) -> list[str]:
    if not rows:
        return ["- No state diagnostics available."]
    return [
        f"- {row.scenario_id}: most_common_state_ratio={row.most_common_state_ratio:.4f}, "
        f"directional_state_ratio={row.directional_state_ratio:.4f}, state_diversity={row.state_diversity}"
        for row in rows
    ]


def _transition_lines(rows: list[CalibrationMetricsRow]) -> list[str]:
    if not rows:
        return ["- No transition diagnostics available."]
    return [
        f"- {row.scenario_id}: state_change_rate={row.state_change_rate:.4f}, "
        f"direction_change_rate={row.direction_change_rate:.4f}, "
        f"transition_stability={row.transition_stability:.4f}, transition_diversity={row.transition_diversity}"
        for row in rows
    ]


def _price_outcome_lines(rows: list[CalibrationMetricsRow]) -> list[str]:
    if not rows:
        return ["- No price outcome diagnostics available."]
    lines = [
        f"- {row.scenario_id}: avg_forward_range_pips={row.average_forward_range_pips:.4f}, "
        f"avg_outcome_magnitude_pips={row.average_outcome_magnitude_pips:.4f}, "
        f"direction_alignment_rate={row.direction_alignment_rate:.4f}"
        for row in rows
    ]
    lines.append("- Forward close return is noted as regime-sensitive.")
    return lines


def _finding_lines(findings: list[CalibrationFinding], finding_types: set[str]) -> list[str]:
    selected = [finding for finding in findings if finding.finding_type in finding_types]
    if not selected:
        return ["- No findings in this section."]
    return [
        f"- {finding.finding_id}: severity={finding.severity}, type={finding.finding_type}, "
        f"scope={finding.scope}, scenario={finding.scenario_id}, metric={finding.metric_name}, "
        f"value={finding.metric_value:.4f}, threshold={finding.threshold:.4f}. {finding.message}"
        for finding in selected
    ]


def _snake(column: str) -> str:
    return column.lower()
