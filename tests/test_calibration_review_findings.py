from sqre.calibration_review.config import CalibrationReviewConfig
from sqre.calibration_review.findings import generate_calibration_findings
from sqre.calibration_review.models import CalibrationMetricsRow


def _row(**overrides) -> CalibrationMetricsRow:
    values = {
        "scenario_id": "eurusd_m5_period_1",
        "symbol": "EURUSD",
        "timeframe": "M5",
        "status": "COMPLETED",
        "period_start": "2026-01-01",
        "period_end": "2026-01-31",
        "ohlc_rows": 1000,
        "duration_utilization_ratio": 0.5,
        "most_common_state_ratio": 0.3,
        "directional_state_ratio": 0.4,
        "compression_consolidation_ratio": 0.2,
        "volatile_rotation_ratio": 0.1,
        "unclassified_rate": 0.0,
        "low_quality_rate": 0.0,
        "state_diversity": 6,
        "transition_diversity": 5,
        "state_change_rate": 0.4,
        "direction_change_rate": 0.3,
        "transition_stability": 0.8,
        "research_low_sample_rate": 0.1,
        "price_outcome_low_sample_rate": 0.1,
        "average_forward_range_pips": 10.0,
        "average_outcome_magnitude_pips": 7.0,
        "direction_alignment_rate": 0.5,
        "average_forward_close_return_pips": 1.0,
        "duration_near_max_flag": False,
        "high_state_dominance_flag": False,
        "low_state_diversity_flag": False,
        "high_directional_ratio_flag": False,
        "high_research_low_sample_flag": False,
        "high_price_outcome_low_sample_flag": False,
        "calibration_status": "OK",
        "calibration_notes": "No diagnostic flags triggered.",
    }
    values.update(overrides)
    return CalibrationMetricsRow(**values)


def test_generate_calibration_findings_emits_scenario_findings():
    findings = generate_calibration_findings(
        [
            _row(
                duration_utilization_ratio=0.9,
                duration_near_max_flag=True,
                most_common_state_ratio=0.7,
                high_state_dominance_flag=True,
                state_diversity=2,
                low_state_diversity_flag=True,
                directional_state_ratio=0.8,
                high_directional_ratio_flag=True,
                research_low_sample_rate=0.6,
                high_research_low_sample_flag=True,
                price_outcome_low_sample_rate=0.7,
                high_price_outcome_low_sample_flag=True,
            )
        ],
        CalibrationReviewConfig(),
    )

    finding_types = {finding.finding_type for finding in findings}
    assert {"STRUCTURE_DURATION", "STATE_DISTRIBUTION", "STATE_DIVERSITY", "LOW_SAMPLE_SIZE"} <= finding_types
    assert any(finding.severity == "REVIEW" for finding in findings)


def test_generate_calibration_findings_skips_incomplete_scenario_flags():
    findings = generate_calibration_findings(
        [_row(status="MISSING_INPUT", duration_near_max_flag=True)],
        CalibrationReviewConfig(),
    )

    assert findings == []


def test_generate_calibration_findings_adds_temporal_consistency_findings():
    findings = generate_calibration_findings(
        [
            _row(scenario_id="eurusd_m5_period_1", ohlc_rows=1000, average_forward_range_pips=10.0),
            _row(scenario_id="eurusd_m5_period_2", ohlc_rows=1020, average_forward_range_pips=10.5),
        ],
        CalibrationReviewConfig(),
    )

    temporal = [finding for finding in findings if finding.finding_type == "TEMPORAL_CONSISTENCY"]
    assert len(temporal) == 1
    assert temporal[0].severity == "INFO"


def test_generate_calibration_findings_adds_timeframe_sensitivity_findings():
    findings = generate_calibration_findings(
        [
            _row(scenario_id="m5", timeframe="M5", average_forward_range_pips=5.0),
            _row(scenario_id="h1", timeframe="H1", average_forward_range_pips=10.0),
            _row(scenario_id="h4", timeframe="H4", average_forward_range_pips=8.0),
        ],
        CalibrationReviewConfig(),
    )

    timeframe = [finding for finding in findings if finding.finding_type == "TIMEFRAME_SENSITIVITY"]
    assert len(timeframe) == 1
    assert timeframe[0].severity == "WATCH"
