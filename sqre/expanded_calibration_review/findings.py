"""Generate diagnostic findings for expanded calibration review."""

from __future__ import annotations

from sqre.expanded_calibration_review.config import ExpandedCalibrationReviewConfig
from sqre.expanded_calibration_review.models import ExpandedCalibrationFinding, TimeframeCalibrationReviewRow


def generate_expanded_calibration_findings(
    rows: list[TimeframeCalibrationReviewRow],
    config: ExpandedCalibrationReviewConfig,
) -> list[ExpandedCalibrationFinding]:
    findings: list[ExpandedCalibrationFinding] = []
    for row in rows:
        if row.scenario_count < config.min_scenarios_per_timeframe:
            findings.append(
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="SCENARIO_COVERAGE",
                    flag="LOW",
                    message="Timeframe has fewer scenarios than the diagnostic minimum.",
                )
            )
        findings.extend(
            [
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="STRUCTURAL_STABILITY",
                    flag=row.structural_stability_flag,
                    message=f"Structure count CV is {row.structure_count_cv:.4f}.",
                ),
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="STATE_DIVERSITY",
                    flag=row.state_diversity_flag,
                    message=f"Average unique states is {row.average_unique_states:.4f}.",
                ),
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="LOW_SAMPLE_PRESSURE",
                    flag=row.low_sample_pressure_flag,
                    message=(
                        "Average low sample conditions are "
                        f"research={row.average_low_sample_conditions_research:.4f}, "
                        f"price_outcome={row.average_low_sample_conditions_price_outcome:.4f}."
                    ),
                ),
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="FORWARD_RANGE_REGIME_SENSITIVITY",
                    flag=row.forward_range_regime_sensitivity_flag,
                    message=f"Forward range CV is {row.forward_range_cv:.4f}.",
                ),
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="UNCLASSIFIED_PRESSURE",
                    flag=row.unclassified_pressure_flag,
                    message=f"Average unclassified rate is {row.average_unclassified_rate:.4f}.",
                ),
                ExpandedCalibrationFinding(
                    timeframe=row.timeframe,
                    finding_type="LOW_QUALITY_PRESSURE",
                    flag=row.low_quality_pressure_flag,
                    message=f"Average low quality rate is {row.average_low_quality_rate:.4f}.",
                ),
            ]
        )
    return findings
