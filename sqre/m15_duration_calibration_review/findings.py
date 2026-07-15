"""Findings for M15 duration calibration review."""

from __future__ import annotations

from sqre.m15_duration_calibration_review.models import M15DurationReviewFinding, M15DurationReviewRow


def build_m15_duration_review_findings(rows: list[M15DurationReviewRow]) -> list[M15DurationReviewFinding]:
    findings: list[M15DurationReviewFinding] = []
    for row in rows:
        findings.append(
            M15DurationReviewFinding(
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
            M15DurationReviewFinding(
                timeframe=row.timeframe,
                experiment_profile=row.experiment_profile,
                finding_type="STRUCTURAL_FRAGMENTATION",
                flag=row.fragmentation_flag,
                message=f"Structure change versus baseline is {_format_relative(row.relative_structure_change_vs_baseline)}.",
            )
        )
        findings.append(
            M15DurationReviewFinding(
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
        findings.append(
            M15DurationReviewFinding(
                timeframe=row.timeframe,
                experiment_profile=row.experiment_profile,
                finding_type="STATE_DIVERSITY",
                flag=row.state_diversity_flag,
                message=f"Average unique states is {row.average_unique_states:.4f}.",
            )
        )
    return findings


def _format_relative(value: float | None) -> str:
    if value is None:
        return "changed from zero or unavailable"
    return f"{value:.4f}"
