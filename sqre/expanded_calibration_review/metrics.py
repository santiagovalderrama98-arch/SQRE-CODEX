"""Compute expanded historical calibration review metrics by timeframe."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, pstdev

from sqre.expanded_calibration_review.config import ExpandedCalibrationReviewConfig
from sqre.expanded_calibration_review.models import ExpandedValidationScenarioSummary, TimeframeCalibrationReviewRow


def build_timeframe_metrics(
    scenarios: list[ExpandedValidationScenarioSummary],
    config: ExpandedCalibrationReviewConfig,
) -> list[TimeframeCalibrationReviewRow]:
    grouped: dict[str, list[ExpandedValidationScenarioSummary]] = defaultdict(list)
    for scenario in scenarios:
        if scenario.timeframe:
            grouped[scenario.timeframe].append(scenario)
    return [_row_for_timeframe(timeframe, grouped[timeframe], config) for timeframe in sorted(grouped)]


def _row_for_timeframe(
    timeframe: str,
    scenarios: list[ExpandedValidationScenarioSummary],
    config: ExpandedCalibrationReviewConfig,
) -> TimeframeCalibrationReviewRow:
    structures = [scenario.structures_detected for scenario in scenarios]
    durations = [scenario.average_structure_duration for scenario in scenarios]
    unique_states = [scenario.unique_states for scenario in scenarios]
    forward_ranges = [scenario.average_forward_range_pips for scenario in scenarios]
    outcome_magnitudes = [scenario.average_outcome_magnitude_pips for scenario in scenarios]
    alignment_rates = [scenario.direction_alignment_rate for scenario in scenarios]
    research_low_samples = [scenario.low_sample_conditions_research for scenario in scenarios]
    price_low_samples = [scenario.low_sample_conditions_price_outcome for scenario in scenarios]
    directional_ratios = [_directional_ratio(scenario) for scenario in scenarios]
    complex_ratios = [_safe_ratio(scenario.complex_consolidation_count, _state_denominator(scenario)) for scenario in scenarios]
    volatile_ratios = [_safe_ratio(scenario.volatile_rotation_count, _state_denominator(scenario)) for scenario in scenarios]
    low_quality_rates = [_safe_ratio(scenario.low_quality_structure_count, _state_denominator(scenario)) for scenario in scenarios]
    unclassified_rates = [_safe_ratio(scenario.unclassified_count, _state_denominator(scenario)) for scenario in scenarios]
    structure_count_cv = _cv(structures)
    structure_duration_cv = _cv(durations)
    forward_range_cv = _cv(forward_ranges)
    average_unique_states = mean(unique_states) if unique_states else 0.0
    average_research_low_samples = mean(research_low_samples) if research_low_samples else 0.0
    average_price_low_samples = mean(price_low_samples) if price_low_samples else 0.0
    average_unclassified_rate = mean(unclassified_rates) if unclassified_rates else 0.0
    average_low_quality_rate = mean(low_quality_rates) if low_quality_rates else 0.0
    structural_flag = "STABLE" if structure_count_cv <= config.high_structure_variation_threshold else "VARIABLE"
    diversity_flag = _state_diversity_flag(average_unique_states, config)
    low_sample_flag = (
        "HIGH"
        if average_research_low_samples >= config.high_low_sample_threshold
        or average_price_low_samples >= config.high_low_sample_threshold
        else "MODERATE"
    )
    forward_flag = "HIGH" if forward_range_cv >= config.high_forward_range_variation_threshold else "MODERATE"
    unclassified_flag = "HIGH" if average_unclassified_rate >= config.high_unclassified_rate_threshold else "LOW"
    low_quality_flag = "HIGH" if average_low_quality_rate >= config.high_low_quality_rate_threshold else "LOW"
    profile = _diagnostic_profile(
        timeframe=timeframe,
        structural_flag=structural_flag,
        diversity_flag=diversity_flag,
        forward_flag=forward_flag,
        low_sample_flag=low_sample_flag,
        complex_ratio=mean(complex_ratios) if complex_ratios else 0.0,
    )
    return TimeframeCalibrationReviewRow(
        timeframe=timeframe,
        scenario_count=len(scenarios),
        scenario_ids=";".join(scenario.scenario_id for scenario in scenarios),
        average_ohlc_rows=_avg([scenario.ohlc_rows for scenario in scenarios]),
        total_ohlc_rows=sum(scenario.ohlc_rows for scenario in scenarios),
        average_structures_detected=_avg(structures),
        min_structures_detected=min(structures) if structures else 0,
        max_structures_detected=max(structures) if structures else 0,
        structure_count_range=(max(structures) - min(structures)) if structures else 0,
        structure_count_cv=structure_count_cv,
        average_structure_duration=_avg(durations),
        min_average_structure_duration=min(durations) if durations else 0.0,
        max_average_structure_duration=max(durations) if durations else 0.0,
        structure_duration_cv=structure_duration_cv,
        average_unique_states=average_unique_states,
        min_unique_states=min(unique_states) if unique_states else 0,
        max_unique_states=max(unique_states) if unique_states else 0,
        state_diversity_range=(max(unique_states) - min(unique_states)) if unique_states else 0,
        most_common_state_mode=_mode([scenario.most_common_state for scenario in scenarios]),
        directional_displacement_total=sum(scenario.directional_displacement_count for scenario in scenarios),
        directional_expansion_total=sum(scenario.directional_expansion_count for scenario in scenarios),
        volatile_rotation_total=sum(scenario.volatile_rotation_count for scenario in scenarios),
        complex_consolidation_total=sum(scenario.complex_consolidation_count for scenario in scenarios),
        low_quality_structure_total=sum(scenario.low_quality_structure_count for scenario in scenarios),
        unclassified_total=sum(scenario.unclassified_count for scenario in scenarios),
        average_directional_state_ratio=_avg(directional_ratios),
        average_complex_consolidation_ratio=_avg(complex_ratios),
        average_volatile_rotation_ratio=_avg(volatile_ratios),
        average_low_quality_rate=average_low_quality_rate,
        average_unclassified_rate=average_unclassified_rate,
        average_forward_range_pips=_avg(forward_ranges),
        min_forward_range_pips=min(forward_ranges) if forward_ranges else 0.0,
        max_forward_range_pips=max(forward_ranges) if forward_ranges else 0.0,
        forward_range_cv=forward_range_cv,
        average_outcome_magnitude_pips=_avg(outcome_magnitudes),
        average_direction_alignment_rate=_avg(alignment_rates),
        min_direction_alignment_rate=min(alignment_rates) if alignment_rates else 0.0,
        max_direction_alignment_rate=max(alignment_rates) if alignment_rates else 0.0,
        average_low_sample_conditions_research=average_research_low_samples,
        average_low_sample_conditions_price_outcome=average_price_low_samples,
        max_low_sample_conditions_research=max(research_low_samples) if research_low_samples else 0,
        max_low_sample_conditions_price_outcome=max(price_low_samples) if price_low_samples else 0,
        structural_stability_flag=structural_flag,
        state_diversity_flag=diversity_flag,
        low_sample_pressure_flag=low_sample_flag,
        forward_range_regime_sensitivity_flag=forward_flag,
        unclassified_pressure_flag=unclassified_flag,
        low_quality_pressure_flag=low_quality_flag,
        diagnostic_profile=profile,
        recommended_follow_up=_recommended_follow_up(timeframe, profile),
    )


def _state_denominator(scenario: ExpandedValidationScenarioSummary) -> int:
    return scenario.states_generated or scenario.structures_detected


def _directional_ratio(scenario: ExpandedValidationScenarioSummary) -> float:
    return _safe_ratio(
        scenario.directional_displacement_count
        + scenario.directional_expansion_count
        + scenario.directional_drift_count,
        _state_denominator(scenario),
    )


def _cv(values: list[float | int]) -> float:
    if not values:
        return 0.0
    value_mean = mean(values)
    if value_mean == 0:
        return 0.0
    return pstdev(values) / value_mean


def _avg(values: list[float | int]) -> float:
    return mean(values) if values else 0.0


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def _mode(values: list[str]) -> str:
    selected = [value for value in values if value]
    if not selected:
        return ""
    return Counter(selected).most_common(1)[0][0]


def _state_diversity_flag(average_unique_states: float, config: ExpandedCalibrationReviewConfig) -> str:
    if average_unique_states <= config.low_state_diversity_threshold:
        return "LOW_DIVERSITY"
    if average_unique_states >= config.high_state_diversity_threshold:
        return "HIGH_DIVERSITY"
    return "BALANCED_DIVERSITY"


def _diagnostic_profile(
    *,
    timeframe: str,
    structural_flag: str,
    diversity_flag: str,
    forward_flag: str,
    low_sample_flag: str,
    complex_ratio: float,
) -> str:
    if timeframe == "D1" and structural_flag == "STABLE" and forward_flag == "HIGH":
        return "Stable structural timeframe with regime-sensitive price outcomes"
    if timeframe == "H4" and structural_flag == "STABLE" and diversity_flag == "BALANCED_DIVERSITY":
        return "Balanced structural research timeframe"
    if timeframe == "H1" and low_sample_flag == "HIGH" and diversity_flag in {"BALANCED_DIVERSITY", "HIGH_DIVERSITY"}:
        return "Intermediate timeframe requiring sample/control review"
    if timeframe == "M5" and (complex_ratio >= 0.50 or diversity_flag == "HIGH_DIVERSITY"):
        return "Microstructure/consolidation-heavy timeframe"
    return "Diagnostic review required"


def _recommended_follow_up(timeframe: str, profile: str) -> str:
    if timeframe == "D1":
        return "Review regime-normalized price outcome interpretation."
    if timeframe == "H4":
        return "Maintain baseline structure settings and continue calibration monitoring."
    if timeframe == "H1":
        return "Consider H1-specific duration and state-threshold experiments."
    if timeframe == "M5":
        return "Consider M5-specific microstructure calibration and state taxonomy compression."
    return "Continue descriptive validation before changing defaults."
