"""Findings for M15 introduction review."""

from __future__ import annotations

from sqre.m15_introduction_review.models import M15ReviewFinding, M15ReviewRow


def build_m15_review_findings(rows: list[M15ReviewRow]) -> list[M15ReviewFinding]:
    findings: list[M15ReviewFinding] = []
    for row in rows:
        findings.extend(
            [
                M15ReviewFinding(
                    finding_type="STRUCTURE_STABILITY",
                    flag=row.structure_stability_flag,
                    message=f"M15 structure count CV is {row.structure_count_cv:.4f}.",
                ),
                M15ReviewFinding(
                    finding_type="DURATION_UTILIZATION",
                    flag=row.duration_utilization_flag,
                    message=f"M15 average duration utilization is {row.average_duration_utilization_ratio:.4f}.",
                ),
                M15ReviewFinding(
                    finding_type="STATE_DIVERSITY",
                    flag=row.state_diversity_flag,
                    message=f"M15 average unique states is {row.average_unique_states:.4f}.",
                ),
                M15ReviewFinding(
                    finding_type="LOW_SAMPLE_PRESSURE",
                    flag=row.low_sample_pressure_flag,
                    message=(
                        f"M15 average low sample counts are research={row.average_low_sample_conditions_research:.4f}, "
                        f"price_outcome={row.average_low_sample_conditions_price_outcome:.4f}."
                    ),
                ),
                M15ReviewFinding(
                    finding_type="FORWARD_RANGE_STABILITY",
                    flag=row.forward_range_stability_flag,
                    message=f"M15 forward range CV is {row.forward_range_cv:.4f}.",
                ),
                M15ReviewFinding(
                    finding_type="DIAGNOSTIC_PROFILE",
                    flag=row.m15_diagnostic_profile,
                    message=row.recommended_follow_up,
                ),
            ]
        )
    return findings
