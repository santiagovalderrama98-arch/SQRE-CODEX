from sqre.m15_duration_calibration_review.config import M15DurationCalibrationReviewConfig
from sqre.m15_duration_calibration_review.findings import build_m15_duration_review_findings
from sqre.m15_duration_calibration_review.metrics import build_m15_duration_review_rows
from sqre.m15_duration_calibration_review.models import M15DurationExperimentRunRow


def test_findings_are_descriptive_and_non_operational():
    rows = build_m15_duration_review_rows(
        [
            M15DurationExperimentRunRow(
                scenario_id="eurusd_m15_period_1",
                timeframe="M15",
                experiment_profile="m15_duration_8h_baseline",
                status="COMPLETED",
                max_structure_duration_seconds=28800,
                structures_detected=10,
                average_structure_duration=24000,
                unique_states=7,
                most_common_state="DIRECTIONAL_DRIFT",
                average_forward_range_pips=8,
                direction_alignment_rate=0.4,
                low_sample_conditions_research=60,
                low_sample_conditions_price_outcome=40,
                states_generated=10,
                directional_displacement_count=5,
            )
        ],
        M15DurationCalibrationReviewConfig(),
    )

    findings = build_m15_duration_review_findings(rows)
    text = "\n".join(finding.message for finding in findings)

    assert {finding.finding_type for finding in findings} == {
        "DURATION_PROFILE",
        "STRUCTURAL_FRAGMENTATION",
        "LOW_SAMPLE_PRESSURE",
        "STATE_DIVERSITY",
    }
    assert not _contains_forbidden_language(text)


def _contains_forbidden_language(text: str) -> bool:
    forbidden = [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "trade setup",
        "take profit",
        "stop loss",
        "profitable",
        "opportunity",
        "edge",
        "best profile",
        "ranking",
        "should trade",
        "predicts",
        "optimal",
    ]
    lower = text.lower()
    return any(term in lower for term in forbidden)
