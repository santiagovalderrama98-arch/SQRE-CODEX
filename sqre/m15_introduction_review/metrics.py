"""Metrics for M15 introduction review."""

from __future__ import annotations

import statistics

from sqre.m15_introduction_review.config import M15IntroductionReviewConfig
from sqre.m15_introduction_review.loader import COMPLETED_STATUSES
from sqre.m15_introduction_review.models import M15Context, M15ReviewRow, M15ValidationSummaryRow


def build_m15_review_rows(
    rows: list[M15ValidationSummaryRow],
    config: M15IntroductionReviewConfig,
    context: M15Context | None = None,
) -> list[M15ReviewRow]:
    m15_rows = [row for row in rows if row.timeframe == "M15"]
    if not m15_rows:
        return []
    active_context = context or M15Context(interpretation="No M5/H1 context summary was provided.")
    metric_rows = [row for row in m15_rows if row.status in COMPLETED_STATUSES] or m15_rows
    structures = [row.structures_detected for row in metric_rows]
    durations = [row.average_structure_duration for row in metric_rows]
    unique_states = [row.unique_states for row in metric_rows]
    forward_ranges = [row.average_forward_range_pips for row in metric_rows]
    denominators = [row.states_generated or row.structures_detected for row in metric_rows]
    low_sample_research = [row.low_sample_conditions_research for row in metric_rows]
    low_sample_price = [row.low_sample_conditions_price_outcome for row in metric_rows]
    duration_utilization = _safe_ratio(_mean(durations), config.duration_reference_seconds)
    structure_cv = _cv(structures)
    forward_cv = _cv(forward_ranges)
    average_unique_states = _mean(unique_states)
    average_low_sample_research = _mean(low_sample_research)
    average_low_sample_price = _mean(low_sample_price)

    structure_stability = "STABLE" if structure_cv <= config.high_structure_cv_threshold else "VARIABLE"
    duration_flag = "NEAR_MAX" if duration_utilization >= config.duration_near_max_threshold else "MODERATE"
    state_diversity = _state_diversity_flag(average_unique_states, config)
    low_sample_flag = (
        "HIGH"
        if average_low_sample_research >= config.high_low_sample_threshold
        or average_low_sample_price >= config.high_low_sample_threshold
        else "MODERATE"
    )
    forward_flag = "STABLE" if forward_cv <= config.forward_range_cv_threshold else "VARIABLE"
    diagnostic = _diagnostic_profile(structure_stability, duration_flag, state_diversity, low_sample_flag)

    return [
        M15ReviewRow(
            timeframe="M15",
            scenario_count=len({row.scenario_id for row in m15_rows}),
            completed_scenario_count=sum(1 for row in m15_rows if row.status in COMPLETED_STATUSES),
            failed_scenario_count=sum(1 for row in m15_rows if row.status == "FAILED"),
            missing_input_count=sum(1 for row in m15_rows if row.status == "MISSING_INPUT"),
            scenario_ids=";".join(sorted({row.scenario_id for row in m15_rows})),
            total_ohlc_rows=sum(row.ohlc_rows for row in metric_rows),
            average_ohlc_rows=_mean([row.ohlc_rows for row in metric_rows]),
            average_structures_detected=_mean(structures),
            min_structures_detected=min(structures) if structures else 0,
            max_structures_detected=max(structures) if structures else 0,
            structure_count_range=(max(structures) - min(structures)) if structures else 0,
            structure_count_cv=structure_cv,
            average_structure_duration=_mean(durations),
            average_duration_utilization_ratio=duration_utilization,
            duration_reference_seconds=config.duration_reference_seconds,
            average_unique_states=average_unique_states,
            min_unique_states=min(unique_states) if unique_states else 0,
            max_unique_states=max(unique_states) if unique_states else 0,
            state_diversity_range=(max(unique_states) - min(unique_states)) if unique_states else 0,
            most_common_state_mode=_mode([row.most_common_state for row in metric_rows]),
            directional_displacement_total=sum(row.directional_displacement_count for row in metric_rows),
            directional_expansion_total=sum(row.directional_expansion_count for row in metric_rows),
            directional_drift_total=sum(row.directional_drift_count for row in metric_rows),
            volatile_rotation_total=sum(row.volatile_rotation_count for row in metric_rows),
            complex_consolidation_total=sum(row.complex_consolidation_count for row in metric_rows),
            low_quality_structure_total=sum(row.low_quality_structure_count for row in metric_rows),
            unclassified_total=sum(row.unclassified_count for row in metric_rows),
            average_directional_state_ratio=_average_ratio(
                metric_rows,
                [
                    row.directional_displacement_count + row.directional_expansion_count + row.directional_drift_count
                    for row in metric_rows
                ],
                denominators,
                "directional_state_ratio",
                "has_directional_count_columns",
            ),
            average_complex_consolidation_ratio=_average_ratio(
                metric_rows,
                [row.complex_consolidation_count for row in metric_rows],
                denominators,
                "complex_consolidation_ratio",
                "has_complex_consolidation_count_column",
            ),
            average_volatile_rotation_ratio=_average_ratio(
                metric_rows,
                [row.volatile_rotation_count for row in metric_rows],
                denominators,
                "volatile_rotation_ratio",
                "has_volatile_rotation_count_column",
            ),
            average_low_quality_rate=_average_ratio(
                metric_rows,
                [row.low_quality_structure_count for row in metric_rows],
                denominators,
                "low_quality_rate",
                "has_low_quality_count_column",
            ),
            average_unclassified_rate=_average_ratio(
                metric_rows,
                [row.unclassified_count for row in metric_rows],
                denominators,
                "unclassified_rate",
                "has_unclassified_count_column",
            ),
            average_forward_range_pips=_mean(forward_ranges),
            min_forward_range_pips=min(forward_ranges) if forward_ranges else 0.0,
            max_forward_range_pips=max(forward_ranges) if forward_ranges else 0.0,
            forward_range_cv=forward_cv,
            average_outcome_magnitude_pips=_mean([row.average_outcome_magnitude_pips for row in metric_rows]),
            average_direction_alignment_rate=_mean([row.direction_alignment_rate for row in metric_rows]),
            average_low_sample_conditions_research=average_low_sample_research,
            average_low_sample_conditions_price_outcome=average_low_sample_price,
            max_low_sample_conditions_research=max(low_sample_research, default=0),
            max_low_sample_conditions_price_outcome=max(low_sample_price, default=0),
            structure_stability_flag=structure_stability,
            duration_utilization_flag=duration_flag,
            state_diversity_flag=state_diversity,
            low_sample_pressure_flag=low_sample_flag,
            forward_range_stability_flag=forward_flag,
            m15_diagnostic_profile=diagnostic,
            recommended_follow_up=_follow_up(diagnostic),
            m5_average_structures_context=active_context.m5_average_structures,
            h1_average_structures_context=active_context.h1_average_structures,
            m5_average_unique_states_context=active_context.m5_average_unique_states,
            h1_average_unique_states_context=active_context.h1_average_unique_states,
            m5_low_sample_context=active_context.m5_low_sample,
            h1_low_sample_context=active_context.h1_low_sample,
            context_interpretation=active_context.interpretation,
        )
    ]


def _state_diversity_flag(average_unique_states: float, config: M15IntroductionReviewConfig) -> str:
    if average_unique_states >= config.high_state_diversity_threshold:
        return "HIGH_DIVERSITY"
    if average_unique_states <= config.low_state_diversity_threshold:
        return "LOW_DIVERSITY"
    return "BALANCED_DIVERSITY"


def _diagnostic_profile(
    structure_stability: str,
    duration_flag: str,
    state_diversity: str,
    low_sample_flag: str,
) -> str:
    if duration_flag == "NEAR_MAX":
        return "Intraday timeframe requiring duration review"
    if low_sample_flag == "HIGH":
        return "Intraday timeframe with elevated sample pressure"
    if structure_stability == "VARIABLE":
        return "Intraday timeframe with variable structural behavior"
    if structure_stability == "STABLE" and state_diversity in {"BALANCED_DIVERSITY", "HIGH_DIVERSITY"}:
        return "Candidate intraday research timeframe"
    return "M15 requires further diagnostic review"


def _follow_up(diagnostic: str) -> str:
    if diagnostic == "Candidate intraday research timeframe":
        return "Review M15 against additional periods and compare with H1/M5 context."
    if "duration" in diagnostic:
        return "Consider M15 duration calibration experiments in a later phase."
    if "sample pressure" in diagnostic:
        return "Review M15 sample pressure before downstream aggregation."
    if "variable structural" in diagnostic:
        return "Review whether M15 needs separate calibration before inclusion in master calibration."
    return "M15 requires further review before later aggregation."


def _average_ratio(
    rows: list[M15ValidationSummaryRow],
    numerators: list[int],
    denominators: list[int],
    ratio_attribute: str,
    count_flag_attribute: str,
) -> float:
    if rows and all(bool(getattr(row, count_flag_attribute)) for row in rows):
        return _mean([_safe_ratio(numerator, denominator) for numerator, denominator in zip(numerators, denominators)])
    fallback_ratios = [getattr(row, ratio_attribute) for row in rows if getattr(row, ratio_attribute) is not None]
    if fallback_ratios:
        return _mean(fallback_ratios)
    return 0.0


def _cv(values: list[int | float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    if mean == 0:
        return 0.0
    return float(statistics.pstdev(values) / mean)


def _mean(values: list[int | float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def _mode(values: list[str]) -> str:
    clean = [value for value in values if value]
    if not clean:
        return ""
    return max(sorted(set(clean)), key=clean.count)
