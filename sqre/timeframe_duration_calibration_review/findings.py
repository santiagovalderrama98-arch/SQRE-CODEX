"""Findings for H1/M5 duration calibration review."""

from __future__ import annotations

from sqre.timeframe_duration_calibration_review.models import DurationReviewFinding, DurationReviewRow


def build_duration_review_findings(rows: list[DurationReviewRow]) -> list[DurationReviewFinding]:
    findings: list[DurationReviewFinding] = []
    for row in rows:
        findings.append(
            DurationReviewFinding(
                timeframe=row.timeframe,
                experiment_profile=row.experiment_profile,
                finding_type="DURATION_PROFILE",
                flag=row.duration_utilization_flag,
                message=(
                    f"{row.profile_diagnostic}. Duration utilization is "
                    f"{row.average_duration_utilization_ratio:.4f}."
                ),
            )
        )
        findings.append(
            DurationReviewFinding(
                timeframe=row.timeframe,
                experiment_profile=row.experiment_profile,
                finding_type="LOW_SAMPLE_PRESSURE",
                flag=row.low_sample_pressure_flag,
                message=(
                    f"Average low sample counts are research={row.average_low_sample_conditions_research:.4f}, "
                    f"price_outcome={row.average_low_sample_conditions_price_outcome:.4f}."
                ),
            )
        )
    return findings
