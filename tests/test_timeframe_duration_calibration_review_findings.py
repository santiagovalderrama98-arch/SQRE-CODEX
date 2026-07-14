from sqre.timeframe_duration_calibration_review.config import TimeframeDurationCalibrationReviewConfig
from sqre.timeframe_duration_calibration_review.findings import build_duration_review_findings
from sqre.timeframe_duration_calibration_review.metrics import build_duration_review_rows
from sqre.timeframe_duration_calibration_review.models import DurationExperimentRunRow


def test_diagnostics_and_followups_are_descriptive():
    rows = build_duration_review_rows(
        [
            _run("one", "H1", "h1_duration_24h_baseline", structures=10),
            _run("one", "H1", "h1_duration_18h", structures=15),
        ],
        TimeframeDurationCalibrationReviewConfig(),
    )

    candidate = next(row for row in rows if row.experiment_profile == "h1_duration_18h")
    assert candidate.profile_diagnostic == "H1 profile increases structural fragmentation"
    assert "diagnostic comparison" in candidate.recommended_follow_up


def test_findings_do_not_use_ranking_or_operational_language():
    rows = build_duration_review_rows([_run("one", "M5", "m5_duration_4h_baseline")], TimeframeDurationCalibrationReviewConfig())
    findings = build_duration_review_findings(rows)
    text = " ".join(f"{item.message} {item.flag}" for item in findings).lower()

    forbidden = ["best", "worst", "ranking", "optimal", "trade", "signal", "profitable", "edge"]
    assert not [word for word in forbidden if word in text]


def _run(scenario_id: str, timeframe: str, profile: str, *, structures: int = 10) -> DurationExperimentRunRow:
    return DurationExperimentRunRow(
        scenario_id=scenario_id,
        timeframe=timeframe,
        experiment_profile=profile,
        status="COMPLETED",
        max_structure_duration_seconds=86400 if timeframe == "H1" else 14400,
        structures_detected=structures,
        average_structure_duration=3600,
        unique_states=5,
        most_common_state="DIRECTIONAL_DISPLACEMENT",
        average_forward_range_pips=12,
        direction_alignment_rate=0.55,
        low_sample_conditions_research=10,
        low_sample_conditions_price_outcome=8,
        states_generated=structures,
    )
