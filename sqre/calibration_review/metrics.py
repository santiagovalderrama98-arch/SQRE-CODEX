"""Build diagnostic calibration metrics from validation summaries."""

from __future__ import annotations

from sqre.calibration_review.config import CalibrationReviewConfig
from sqre.calibration_review.models import CalibrationMetricsRow, ValidationScenarioSummary


STATE_COUNT_ATTRS = {
    "DIRECTIONAL_DISPLACEMENT": "directional_displacement_count",
    "DIRECTIONAL_EXPANSION": "directional_expansion_count",
    "DIRECTIONAL_DRIFT": "directional_drift_count",
    "VOLATILE_ROTATION": "volatile_rotation_count",
    "COMPLEX_CONSOLIDATION": "complex_consolidation_count",
    "NEUTRAL_COMPRESSION": "neutral_compression_count",
    "LOW_QUALITY_STRUCTURE": "low_quality_structure_count",
    "UNCLASSIFIED": "unclassified_count",
}


def build_calibration_metrics(
    scenarios: list[ValidationScenarioSummary],
    config: CalibrationReviewConfig,
) -> list[CalibrationMetricsRow]:
    return [_row_from_scenario(scenario, config) for scenario in scenarios]


def _row_from_scenario(scenario: ValidationScenarioSummary, config: CalibrationReviewConfig) -> CalibrationMetricsRow:
    duration_utilization = _safe_ratio(
        scenario.average_structure_duration,
        scenario.max_structure_duration_seconds,
    )
    most_common_state_ratio = _safe_ratio(_most_common_state_count(scenario), scenario.states_generated)
    directional_ratio = _safe_ratio(
        scenario.directional_displacement_count
        + scenario.directional_expansion_count
        + scenario.directional_drift_count,
        scenario.states_generated,
    )
    compression_ratio = _safe_ratio(
        scenario.complex_consolidation_count + scenario.neutral_compression_count,
        scenario.states_generated,
    )
    volatile_rotation_ratio = _safe_ratio(scenario.volatile_rotation_count, scenario.states_generated)
    unclassified_rate = _safe_ratio(scenario.unclassified_count, scenario.states_generated)
    low_quality_rate = _safe_ratio(scenario.low_quality_structure_count, scenario.states_generated)
    research_low_sample_rate = _safe_ratio(scenario.low_sample_conditions_research, scenario.conditions_evaluated)
    price_outcome_low_sample_rate = _safe_ratio(
        scenario.low_sample_conditions_price_outcome,
        scenario.price_outcome_summary_rows,
    )

    duration_near_max = duration_utilization >= config.duration_near_max_threshold
    high_state_dominance = most_common_state_ratio >= config.state_dominance_threshold
    low_state_diversity = scenario.unique_states <= config.low_state_diversity_threshold
    high_directional_ratio = directional_ratio >= config.high_directional_ratio_threshold
    high_research_low_sample = research_low_sample_rate >= config.low_sample_rate_threshold
    high_price_outcome_low_sample = price_outcome_low_sample_rate >= config.low_sample_rate_threshold
    calibration_status = _calibration_status(
        status=scenario.status,
        high_research_low_sample=high_research_low_sample,
        high_price_outcome_low_sample=high_price_outcome_low_sample,
        low_state_diversity=low_state_diversity,
        high_state_dominance=high_state_dominance,
        flags=[
            duration_near_max,
            high_state_dominance,
            low_state_diversity,
            high_directional_ratio,
            high_research_low_sample,
            high_price_outcome_low_sample,
        ],
    )

    return CalibrationMetricsRow(
        scenario_id=scenario.scenario_id,
        symbol=scenario.symbol,
        timeframe=scenario.timeframe,
        status=scenario.status,
        period_start=scenario.period_start,
        period_end=scenario.period_end,
        ohlc_rows=scenario.ohlc_rows,
        duration_utilization_ratio=duration_utilization,
        most_common_state_ratio=most_common_state_ratio,
        directional_state_ratio=directional_ratio,
        compression_consolidation_ratio=compression_ratio,
        volatile_rotation_ratio=volatile_rotation_ratio,
        unclassified_rate=unclassified_rate,
        low_quality_rate=low_quality_rate,
        state_diversity=scenario.unique_states,
        transition_diversity=scenario.unique_transitions,
        state_change_rate=scenario.state_change_rate,
        direction_change_rate=scenario.direction_change_rate,
        transition_stability=scenario.average_transition_stability,
        research_low_sample_rate=research_low_sample_rate,
        price_outcome_low_sample_rate=price_outcome_low_sample_rate,
        average_forward_range_pips=scenario.average_forward_range_pips,
        average_outcome_magnitude_pips=scenario.average_outcome_magnitude_pips,
        direction_alignment_rate=scenario.direction_alignment_rate,
        average_forward_close_return_pips=scenario.average_forward_close_return_pips,
        duration_near_max_flag=duration_near_max,
        high_state_dominance_flag=high_state_dominance,
        low_state_diversity_flag=low_state_diversity,
        high_directional_ratio_flag=high_directional_ratio,
        high_research_low_sample_flag=high_research_low_sample,
        high_price_outcome_low_sample_flag=high_price_outcome_low_sample,
        calibration_status=calibration_status,
        calibration_notes=_notes(calibration_status),
    )


def _most_common_state_count(scenario: ValidationScenarioSummary) -> int:
    attr = STATE_COUNT_ATTRS.get(scenario.most_common_state.upper())
    return int(getattr(scenario, attr, 0)) if attr else 0


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def _calibration_status(
    *,
    status: str,
    high_research_low_sample: bool,
    high_price_outcome_low_sample: bool,
    low_state_diversity: bool,
    high_state_dominance: bool,
    flags: list[bool],
) -> str:
    if status != "COMPLETED":
        return "NOT_AVAILABLE"
    if (high_research_low_sample and high_price_outcome_low_sample) or (
        low_state_diversity and high_state_dominance
    ):
        return "REVIEW"
    if any(flags):
        return "WATCH"
    return "OK"


def _notes(status: str) -> str:
    if status == "NOT_AVAILABLE":
        return "Scenario did not complete; diagnostics unavailable."
    if status == "REVIEW":
        return "One or more diagnostic metrics require calibration review."
    if status == "WATCH":
        return "One or more diagnostic metrics should be monitored."
    return "No diagnostic flags triggered."
