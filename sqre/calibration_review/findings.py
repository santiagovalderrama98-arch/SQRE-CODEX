"""Generate diagnostic calibration findings."""

from __future__ import annotations

from itertools import combinations

from sqre.calibration_review.config import CalibrationReviewConfig
from sqre.calibration_review.models import CalibrationFinding, CalibrationMetricsRow


TIMEFRAME_ORDER = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]


def generate_calibration_findings(
    rows: list[CalibrationMetricsRow],
    config: CalibrationReviewConfig,
) -> list[CalibrationFinding]:
    findings: list[CalibrationFinding] = []
    for row in rows:
        findings.extend(_scenario_findings(row, config, start_index=len(findings) + 1))
    findings.extend(_temporal_findings(rows, start_index=len(findings) + 1))
    findings.extend(_timeframe_findings(rows, start_index=len(findings) + 1))
    return findings


def _scenario_findings(
    row: CalibrationMetricsRow,
    config: CalibrationReviewConfig,
    *,
    start_index: int,
) -> list[CalibrationFinding]:
    findings: list[CalibrationFinding] = []
    if row.status != "COMPLETED":
        return findings
    checks = [
        (
            row.duration_near_max_flag,
            "STRUCTURE_DURATION",
            "WATCH",
            "duration_utilization_ratio",
            row.duration_utilization_ratio,
            config.duration_near_max_threshold,
            "Average structure duration is near the configured maximum. Review whether structures are terminating by structural logic or by duration limit.",
        ),
        (
            row.high_state_dominance_flag,
            "STATE_DISTRIBUTION",
            "REVIEW" if row.low_state_diversity_flag else "WATCH",
            "most_common_state_ratio",
            row.most_common_state_ratio,
            config.state_dominance_threshold,
            "Most common state dominates the scenario distribution. Review whether state thresholds are too concentrated for this timeframe.",
        ),
        (
            row.low_state_diversity_flag,
            "STATE_DIVERSITY",
            "WATCH",
            "state_diversity",
            float(row.state_diversity),
            float(config.low_state_diversity_threshold),
            "State diversity is low. Review whether the taxonomy is too coarse for this timeframe.",
        ),
        (
            row.high_directional_ratio_flag,
            "STATE_DISTRIBUTION",
            "WATCH",
            "directional_state_ratio",
            row.directional_state_ratio,
            config.high_directional_ratio_threshold,
            "Directional states represent a high share of all states. Review whether directional thresholds are appropriate for this timeframe.",
        ),
        (
            row.high_research_low_sample_flag,
            "LOW_SAMPLE_SIZE",
            "REVIEW",
            "research_low_sample_rate",
            row.research_low_sample_rate,
            config.low_sample_rate_threshold,
            "Research Engine has a high low-sample condition rate. More historical data may be required before interpretation.",
        ),
        (
            row.high_price_outcome_low_sample_flag,
            "LOW_SAMPLE_SIZE",
            "REVIEW",
            "price_outcome_low_sample_rate",
            row.price_outcome_low_sample_rate,
            config.low_sample_rate_threshold,
            "Price Outcome Research has a high low-sample condition rate. More historical data may be required before interpretation.",
        ),
    ]
    for enabled, finding_type, severity, metric, value, threshold, message in checks:
        if enabled:
            findings.append(
                _finding(
                    len(findings) + start_index,
                    finding_type,
                    severity,
                    "SCENARIO",
                    row.timeframe,
                    row.scenario_id,
                    metric,
                    value,
                    threshold,
                    message,
                )
            )
    return findings


def _temporal_findings(rows: list[CalibrationMetricsRow], *, start_index: int) -> list[CalibrationFinding]:
    findings: list[CalibrationFinding] = []
    grouped: dict[str, list[CalibrationMetricsRow]] = {}
    for row in rows:
        if row.status == "COMPLETED":
            grouped.setdefault(row.timeframe, []).append(row)
    for timeframe, items in grouped.items():
        if len(items) < 2:
            continue
        for first, second in combinations(items, 2):
            consistent = (
                _relative_diff(first.ohlc_rows, second.ohlc_rows) <= 0.15
                and _relative_diff(first.duration_utilization_ratio, second.duration_utilization_ratio) <= 0.10
                and _relative_diff(first.average_forward_range_pips, second.average_forward_range_pips) <= 0.20
            )
            severity = "INFO" if consistent else "WATCH"
            message = (
                "Temporal metrics are broadly consistent across periods for this timeframe."
                if consistent
                else "Temporal consistency differs across periods for this timeframe. Review whether differences reflect regime variation or calibration sensitivity."
            )
            findings.append(
                _finding(
                    len(findings) + start_index,
                    "TEMPORAL_CONSISTENCY",
                    severity,
                    "TIMEFRAME",
                    timeframe,
                    f"{first.scenario_id}|{second.scenario_id}",
                    "temporal_consistency",
                    1.0 if consistent else 0.0,
                    1.0,
                    message,
                )
            )
    return findings


def _timeframe_findings(rows: list[CalibrationMetricsRow], *, start_index: int) -> list[CalibrationFinding]:
    completed = [row for row in rows if row.status == "COMPLETED"]
    grouped: dict[str, list[CalibrationMetricsRow]] = {}
    for row in completed:
        grouped.setdefault(row.timeframe, []).append(row)
    available = [timeframe for timeframe in TIMEFRAME_ORDER if timeframe in grouped]
    if len(available) < 3:
        return []
    averages = [
        (timeframe, _average(row.average_forward_range_pips for row in grouped[timeframe]))
        for timeframe in available
    ]
    increasing = all(current <= following for (_, current), (_, following) in zip(averages, averages[1:]))
    return [
        _finding(
            start_index,
            "TIMEFRAME_SENSITIVITY",
            "INFO" if increasing else "WATCH",
            "VALIDATION",
            "MULTI",
            "MULTI_TIMEFRAME",
            "average_forward_range_pips",
            averages[-1][1] if averages else 0.0,
            0.0,
            (
                "Average forward range increases across available timeframes."
                if increasing
                else "Average forward range does not increase consistently across available timeframes. Review timeframe sensitivity."
            ),
        )
    ]


def _finding(
    index: int,
    finding_type: str,
    severity: str,
    scope: str,
    timeframe: str,
    scenario_id: str,
    metric_name: str,
    metric_value: float,
    threshold: float,
    message: str,
) -> CalibrationFinding:
    return CalibrationFinding(
        finding_id=f"CAL_{index:06d}",
        finding_type=finding_type,
        severity=severity,
        scope=scope,
        timeframe=timeframe,
        scenario_id=scenario_id,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold=threshold,
        message=message,
    )


def _relative_diff(first: float, second: float) -> float:
    denominator = max(abs(first), abs(second), 1.0)
    return abs(first - second) / denominator


def _average(values) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0
