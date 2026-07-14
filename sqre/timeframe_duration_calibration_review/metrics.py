"""Metrics for H1/M5 duration calibration review."""

from __future__ import annotations

import statistics
from collections import defaultdict

from sqre.timeframe_duration_calibration_review.config import TimeframeDurationCalibrationReviewConfig
from sqre.timeframe_duration_calibration_review.models import DurationExperimentRunRow, DurationReviewRow


COMPLETED_STATUSES = {"COMPLETED", "SKIPPED"}


def build_duration_review_rows(
    rows: list[DurationExperimentRunRow],
    config: TimeframeDurationCalibrationReviewConfig,
) -> list[DurationReviewRow]:
    grouped: dict[tuple[str, str], list[DurationExperimentRunRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.timeframe, row.experiment_profile)].append(row)

    review_rows = [_build_group(timeframe, profile, items, config) for (timeframe, profile), items in grouped.items()]
    baseline_lookup = {(row.timeframe, row.experiment_profile): row for row in review_rows}
    return [
        _with_baseline(row, baseline_lookup.get((row.timeframe, _baseline_profile(row.timeframe, config))), config)
        for row in sorted(review_rows, key=lambda item: (item.timeframe, item.max_structure_duration_seconds, item.experiment_profile))
    ]


def _build_group(
    timeframe: str,
    profile: str,
    rows: list[DurationExperimentRunRow],
    config: TimeframeDurationCalibrationReviewConfig,
) -> DurationReviewRow:
    metric_rows = [row for row in rows if row.status in COMPLETED_STATUSES] or rows
    structures = [row.structures_detected for row in metric_rows]
    durations = [row.average_structure_duration for row in metric_rows]
    duration_ratios = [_safe_ratio(row.average_structure_duration, row.max_structure_duration_seconds) for row in metric_rows]
    unique_states = [row.unique_states for row in metric_rows]
    denominators = [row.states_generated or row.structures_detected for row in metric_rows]
    profile_duration = _mode_int([row.max_structure_duration_seconds for row in rows])
    average_low_sample_research = _mean([row.low_sample_conditions_research for row in metric_rows])
    average_low_sample_price = _mean([row.low_sample_conditions_price_outcome for row in metric_rows])
    structure_cv = _cv(structures)
    average_duration_ratio = _mean(duration_ratios)

    base = DurationReviewRow(
        timeframe=timeframe,
        experiment_profile=profile,
        scenario_count=len({row.scenario_id for row in rows}),
        completed_run_count=sum(1 for row in rows if row.status in COMPLETED_STATUSES),
        failed_run_count=sum(1 for row in rows if row.status == "FAILED"),
        missing_input_count=sum(1 for row in rows if row.status == "MISSING_INPUT"),
        scenario_ids=";".join(sorted({row.scenario_id for row in rows})),
        max_structure_duration_seconds=profile_duration,
        average_structures_detected=_mean(structures),
        min_structures_detected=min(structures) if structures else 0,
        max_structures_detected=max(structures) if structures else 0,
        structure_count_range=(max(structures) - min(structures)) if structures else 0,
        structure_count_cv=structure_cv,
        average_structure_duration=_mean(durations),
        average_duration_utilization_ratio=average_duration_ratio,
        min_duration_utilization_ratio=min(duration_ratios) if duration_ratios else 0.0,
        max_duration_utilization_ratio=max(duration_ratios) if duration_ratios else 0.0,
        average_unique_states=_mean(unique_states),
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
            [
                row.directional_displacement_count + row.directional_expansion_count + row.directional_drift_count
                for row in metric_rows
            ],
            denominators,
        ),
        average_complex_consolidation_ratio=_average_ratio(
            [row.complex_consolidation_count for row in metric_rows],
            denominators,
        ),
        average_volatile_rotation_ratio=_average_ratio(
            [row.volatile_rotation_count for row in metric_rows],
            denominators,
        ),
        average_low_quality_rate=_average_ratio(
            [row.low_quality_structure_count for row in metric_rows],
            denominators,
        ),
        average_unclassified_rate=_average_ratio(
            [row.unclassified_count for row in metric_rows],
            denominators,
        ),
        average_forward_range_pips=_mean([row.average_forward_range_pips for row in metric_rows]),
        average_outcome_magnitude_pips=_mean([row.average_outcome_magnitude_pips for row in metric_rows]),
        average_direction_alignment_rate=_mean([row.direction_alignment_rate for row in metric_rows]),
        average_low_sample_conditions_research=average_low_sample_research,
        average_low_sample_conditions_price_outcome=average_low_sample_price,
        max_low_sample_conditions_research=max([row.low_sample_conditions_research for row in metric_rows], default=0),
        max_low_sample_conditions_price_outcome=max([row.low_sample_conditions_price_outcome for row in metric_rows], default=0),
        baseline_profile=_baseline_profile(timeframe, config),
        baseline_structures_detected=None,
        relative_structure_change_vs_baseline=None,
        relative_duration_utilization_change_vs_baseline=None,
        relative_unique_states_change_vs_baseline=None,
        relative_low_sample_research_change_vs_baseline=None,
        relative_low_sample_price_outcome_change_vs_baseline=None,
        relative_forward_range_change_vs_baseline=None,
        relative_direction_alignment_change_vs_baseline=None,
        structure_stability_flag="STABLE"
        if structure_cv <= config.high_structure_cv_threshold
        else "VARIABLE",
        duration_utilization_flag="NEAR_MAX"
        if average_duration_ratio >= config.duration_near_max_threshold
        else "MODERATE",
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
    return base


def _with_baseline(
    row: DurationReviewRow,
    baseline: DurationReviewRow | None,
    config: TimeframeDurationCalibrationReviewConfig,
) -> DurationReviewRow:
    is_baseline = row.experiment_profile == row.baseline_profile
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
    diagnostic = _diagnostic(row, is_baseline, fragmentation, compression, low_sample_research_change)

    return DurationReviewRow(
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
            "profile_diagnostic": diagnostic,
            "recommended_follow_up": _follow_up(row, is_baseline, fragmentation, compression),
        }
    )


def _baseline_profile(timeframe: str, config: TimeframeDurationCalibrationReviewConfig) -> str:
    if timeframe == "H1":
        return config.baseline_profile_h1
    if timeframe == "M5":
        return config.baseline_profile_m5
    return ""


def _fragmentation_flag(
    is_baseline: bool,
    relative_structure_change: float | None,
    config: TimeframeDurationCalibrationReviewConfig,
) -> str:
    if is_baseline:
        return "BASELINE_REFERENCE"
    if relative_structure_change is not None and relative_structure_change >= config.fragmentation_increase_threshold:
        return "INCREASED_FRAGMENTATION"
    return "STABLE"


def _compression_flag(
    is_baseline: bool,
    relative_structure_change: float | None,
    config: TimeframeDurationCalibrationReviewConfig,
) -> str:
    if is_baseline:
        return "BASELINE_REFERENCE"
    if relative_structure_change is not None and relative_structure_change <= -config.compression_decrease_threshold:
        return "INCREASED_COMPRESSION"
    return "STABLE"


def _diagnostic(
    row: DurationReviewRow,
    is_baseline: bool,
    fragmentation: str,
    compression: str,
    low_sample_research_change: float | None,
) -> str:
    if is_baseline:
        return "Baseline reference profile"
    if row.timeframe == "H1":
        if fragmentation == "INCREASED_FRAGMENTATION":
            return "H1 profile increases structural fragmentation"
        if row.duration_utilization_flag == "NEAR_MAX":
            return "H1 profile still duration-constrained"
        if low_sample_research_change is not None and low_sample_research_change < 0:
            return "H1 duration candidate requiring further review"
    if row.timeframe == "M5":
        if fragmentation == "INCREASED_FRAGMENTATION":
            return "M5 shorter-duration profile increases structural fragmentation"
        if compression == "INCREASED_COMPRESSION":
            return "M5 longer-duration profile increases structural compression"
        if row.structure_stability_flag == "VARIABLE" and row.low_sample_pressure_flag == "HIGH":
            return "M5 profile remains microstructure-stressed"
    return "Duration profile requires further diagnostic review"


def _follow_up(row: DurationReviewRow, is_baseline: bool, fragmentation: str, compression: str) -> str:
    if is_baseline:
        return "Use as reference only; do not change production defaults."
    if fragmentation != "STABLE" or compression != "STABLE":
        return "Do not promote; retain for diagnostic comparison only."
    if row.timeframe == "H1":
        return "Review H1 duration candidates against low-sample and fragmentation diagnostics."
    if row.timeframe == "M5":
        return "Review M5 duration candidates together with microstructure taxonomy compression."
    return "Requires further review."


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


def _average_ratio(numerators: list[int], denominators: list[int]) -> float:
    ratios = [_safe_ratio(numerator, denominator) for numerator, denominator in zip(numerators, denominators)]
    return _mean(ratios)


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
