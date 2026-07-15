"""Metrics for M15 duration calibration review."""

from __future__ import annotations

import statistics
from collections import defaultdict

from sqre.m15_duration_calibration_review.config import M15DurationCalibrationReviewConfig
from sqre.m15_duration_calibration_review.models import M15DurationExperimentRunRow, M15DurationReviewRow


COMPLETED_STATUSES = {"COMPLETED", "SKIPPED"}
SHORTER_PROFILES = {"m15_duration_4h", "m15_duration_6h"}
LONGER_PROFILES = {"m15_duration_10h", "m15_duration_12h"}


def build_m15_duration_review_rows(
    rows: list[M15DurationExperimentRunRow],
    config: M15DurationCalibrationReviewConfig,
) -> list[M15DurationReviewRow]:
    grouped: dict[tuple[str, str], list[M15DurationExperimentRunRow]] = defaultdict(list)
    for row in rows:
        if row.timeframe == "M15":
            grouped[(row.timeframe, row.experiment_profile)].append(row)

    review_rows = [_build_group(timeframe, profile, items, config) for (timeframe, profile), items in grouped.items()]
    baseline_lookup = {(row.timeframe, row.experiment_profile): row for row in review_rows}
    baseline = baseline_lookup.get(("M15", config.baseline_profile))
    return [
        _with_baseline(row, baseline, config)
        for row in sorted(review_rows, key=lambda item: (item.max_structure_duration_seconds, item.experiment_profile))
    ]


def _build_group(
    timeframe: str,
    profile: str,
    rows: list[M15DurationExperimentRunRow],
    config: M15DurationCalibrationReviewConfig,
) -> M15DurationReviewRow:
    metric_rows = [row for row in rows if row.status in COMPLETED_STATUSES] or rows
    structures = [row.structures_detected for row in metric_rows]
    durations = [row.average_structure_duration for row in metric_rows]
    duration_ratios = [
        _safe_ratio(row.average_structure_duration, row.max_structure_duration_seconds) for row in metric_rows
    ]
    unique_states = [row.unique_states for row in metric_rows]
    denominators = [row.states_generated or row.structures_detected for row in metric_rows]
    low_sample_research = [row.low_sample_conditions_research for row in metric_rows]
    low_sample_price = [row.low_sample_conditions_price_outcome for row in metric_rows]
    structure_cv = _cv(structures)
    average_duration_ratio = _mean(duration_ratios)
    average_unique_states = _mean(unique_states)
    average_low_sample_research = _mean(low_sample_research)
    average_low_sample_price = _mean(low_sample_price)

    return M15DurationReviewRow(
        timeframe=timeframe,
        experiment_profile=profile,
        scenario_count=len({row.scenario_id for row in rows}),
        completed_run_count=sum(1 for row in rows if row.status in COMPLETED_STATUSES),
        failed_run_count=sum(1 for row in rows if row.status == "FAILED"),
        missing_input_count=sum(1 for row in rows if row.status == "MISSING_INPUT"),
        scenario_ids=";".join(sorted({row.scenario_id for row in rows})),
        max_structure_duration_seconds=_mode_int([row.max_structure_duration_seconds for row in rows]),
        average_structures_detected=_mean(structures),
        min_structures_detected=min(structures) if structures else 0,
        max_structures_detected=max(structures) if structures else 0,
        structure_count_range=(max(structures) - min(structures)) if structures else 0,
        structure_count_cv=structure_cv,
        average_structure_duration=_mean(durations),
        average_duration_utilization_ratio=average_duration_ratio,
        min_duration_utilization_ratio=min(duration_ratios) if duration_ratios else 0.0,
        max_duration_utilization_ratio=max(duration_ratios) if duration_ratios else 0.0,
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
        average_forward_range_pips=_mean([row.average_forward_range_pips for row in metric_rows]),
        average_outcome_magnitude_pips=_mean([row.average_outcome_magnitude_pips for row in metric_rows]),
        average_direction_alignment_rate=_mean([row.direction_alignment_rate for row in metric_rows]),
        average_low_sample_conditions_research=average_low_sample_research,
        average_low_sample_conditions_price_outcome=average_low_sample_price,
        max_low_sample_conditions_research=max(low_sample_research, default=0),
        max_low_sample_conditions_price_outcome=max(low_sample_price, default=0),
        baseline_profile=config.baseline_profile,
        baseline_structures_detected=None,
        relative_structure_change_vs_baseline=None,
        relative_duration_utilization_change_vs_baseline=None,
        relative_unique_states_change_vs_baseline=None,
        relative_low_sample_research_change_vs_baseline=None,
        relative_low_sample_price_outcome_change_vs_baseline=None,
        relative_forward_range_change_vs_baseline=None,
        relative_direction_alignment_change_vs_baseline=None,
        structure_stability_flag="STABLE" if structure_cv <= config.high_structure_cv_threshold else "VARIABLE",
        duration_utilization_flag="NEAR_MAX"
        if average_duration_ratio >= config.duration_near_max_threshold
        else "MODERATE",
        state_diversity_flag=_state_diversity_flag(average_unique_states, config),
        low_sample_pressure_flag="HIGH"
        if (
            average_low_sample_research >= config.high_low_sample_threshold
            or average_low_sample_price >= config.high_low_sample_threshold
        )
        else "MODERATE",
        fragmentation_flag="BASELINE_REFERENCE",
        compression_flag="BASELINE_REFERENCE",
        profile_diagnostic="",
        recommended_follow_up="",
    )


def _with_baseline(
    row: M15DurationReviewRow,
    baseline: M15DurationReviewRow | None,
    config: M15DurationCalibrationReviewConfig,
) -> M15DurationReviewRow:
    is_baseline = row.experiment_profile == config.baseline_profile
    baseline_structures = baseline.average_structures_detected if baseline is not None else None
    structure_change = _relative_change(row.average_structures_detected, baseline_structures)
    duration_change = _relative_change(
        row.average_duration_utilization_ratio,
        baseline.average_duration_utilization_ratio if baseline is not None else None,
    )
    unique_change = _relative_change(row.average_unique_states, baseline.average_unique_states if baseline is not None else None)
    low_sample_research_change = _relative_change(
        row.average_low_sample_conditions_research,
        baseline.average_low_sample_conditions_research if baseline is not None else None,
    )
    low_sample_price_change = _relative_change(
        row.average_low_sample_conditions_price_outcome,
        baseline.average_low_sample_conditions_price_outcome if baseline is not None else None,
    )
    forward_range_change = _relative_change(
        row.average_forward_range_pips,
        baseline.average_forward_range_pips if baseline is not None else None,
    )
    alignment_change = _relative_change(
        row.average_direction_alignment_rate,
        baseline.average_direction_alignment_rate if baseline is not None else None,
    )
    fragmentation = _fragmentation_flag(is_baseline, structure_change, config)
    compression = _compression_flag(is_baseline, structure_change, config)

    return M15DurationReviewRow(
        **{
            **row.__dict__,
            "baseline_structures_detected": baseline_structures,
            "relative_structure_change_vs_baseline": 0.0 if is_baseline else structure_change,
            "relative_duration_utilization_change_vs_baseline": 0.0 if is_baseline else duration_change,
            "relative_unique_states_change_vs_baseline": 0.0 if is_baseline else unique_change,
            "relative_low_sample_research_change_vs_baseline": 0.0 if is_baseline else low_sample_research_change,
            "relative_low_sample_price_outcome_change_vs_baseline": 0.0 if is_baseline else low_sample_price_change,
            "relative_forward_range_change_vs_baseline": 0.0 if is_baseline else forward_range_change,
            "relative_direction_alignment_change_vs_baseline": 0.0 if is_baseline else alignment_change,
            "fragmentation_flag": fragmentation,
            "compression_flag": compression,
            "profile_diagnostic": _diagnostic(row, is_baseline, fragmentation, compression, low_sample_research_change),
            "recommended_follow_up": _follow_up(row, is_baseline, fragmentation, compression),
        }
    )


def _state_diversity_flag(average_unique_states: float, config: M15DurationCalibrationReviewConfig) -> str:
    if average_unique_states >= config.high_state_diversity_threshold:
        return "HIGH_DIVERSITY"
    if average_unique_states <= config.low_state_diversity_threshold:
        return "LOW_DIVERSITY"
    return "BALANCED_DIVERSITY"


def _fragmentation_flag(
    is_baseline: bool,
    relative_structure_change: float | None,
    config: M15DurationCalibrationReviewConfig,
) -> str:
    if is_baseline:
        return "BASELINE_REFERENCE"
    if relative_structure_change is not None and relative_structure_change >= config.fragmentation_increase_threshold:
        return "INCREASED_FRAGMENTATION"
    return "STABLE"


def _compression_flag(
    is_baseline: bool,
    relative_structure_change: float | None,
    config: M15DurationCalibrationReviewConfig,
) -> str:
    if is_baseline:
        return "BASELINE_REFERENCE"
    if relative_structure_change is not None and relative_structure_change <= -config.compression_decrease_threshold:
        return "INCREASED_COMPRESSION"
    return "STABLE"


def _diagnostic(
    row: M15DurationReviewRow,
    is_baseline: bool,
    fragmentation: str,
    compression: str,
    low_sample_research_change: float | None,
) -> str:
    if is_baseline:
        return "Baseline reference profile"
    if row.experiment_profile in SHORTER_PROFILES:
        if fragmentation == "INCREASED_FRAGMENTATION" and row.low_sample_pressure_flag == "HIGH":
            return "M15 shorter-duration profile increases structural fragmentation"
        if fragmentation == "STABLE" and row.low_sample_pressure_flag == "HIGH":
            return "M15 shorter-duration profile requires further low-sample review"
        if row.duration_utilization_flag == "MODERATE" and fragmentation == "STABLE":
            return "M15 shorter-duration candidate requiring further review"
    if row.experiment_profile in LONGER_PROFILES:
        if compression == "INCREASED_COMPRESSION":
            return "M15 longer-duration profile increases structural compression"
        if low_sample_research_change is not None and low_sample_research_change < 0 and row.duration_utilization_flag == "NEAR_MAX":
            return "M15 longer-duration profile reduces sample pressure but remains duration-constrained"
        if row.state_diversity_flag == "LOW_DIVERSITY":
            return "M15 longer-duration profile reduces state diversity"
    return "Duration profile requires further diagnostic review"


def _follow_up(
    row: M15DurationReviewRow,
    is_baseline: bool,
    fragmentation: str,
    compression: str,
) -> str:
    if is_baseline:
        return "Use as reference only; do not change production defaults."
    if fragmentation == "INCREASED_FRAGMENTATION" or compression == "INCREASED_COMPRESSION":
        return "Do not promote; retain for diagnostic comparison only."
    if row.low_sample_pressure_flag == "HIGH":
        return "Review M15 sample pressure before downstream aggregation."
    return "Review M15 duration candidate against additional periods before any calibration decision."


def _average_ratio(
    rows: list[M15DurationExperimentRunRow],
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


def _relative_change(value: float | None, baseline: float | None) -> float | None:
    if baseline is None:
        return None
    if baseline == 0:
        if value == 0:
            return 0.0
        return None
    return float(((value or 0.0) - baseline) / baseline)


def _mode(values: list[str]) -> str:
    clean = [value for value in values if value]
    if not clean:
        return ""
    return max(sorted(set(clean)), key=clean.count)


def _mode_int(values: list[int]) -> int:
    if not values:
        return 0
    return max(sorted(set(values)), key=values.count)
