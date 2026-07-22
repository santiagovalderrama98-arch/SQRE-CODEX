"""Descriptive partial-vs-baseline review."""

from __future__ import annotations

from sqre.h4_targeted_partial_expansion_validation.models import (
    BaselineMetrics,
    PartialBaselineComparison,
    PartialCandidate,
    PartialPriceOutcomeSummary,
    PartialStructureStateSummary,
    PartialTransitionSummary,
)


def build_partial_vs_baseline_comparison(
    candidate: PartialCandidate,
    structure_state: PartialStructureStateSummary,
    transition_summary: PartialTransitionSummary,
    price_summary: PartialPriceOutcomeSummary,
    baseline: BaselineMetrics,
) -> PartialBaselineComparison:
    forward_range_ratio = ratio(price_summary.average_forward_range_pips, baseline.average_forward_range_pips)
    outcome_ratio = ratio(price_summary.average_outcome_magnitude_pips, baseline.average_outcome_magnitude_pips)
    comparison_class = classify_comparison(forward_range_ratio, outcome_ratio)
    return PartialBaselineComparison(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        baseline_scenario_count=baseline.scenario_count,
        partial_ohlc_rows=structure_state.ohlc_rows,
        baseline_average_ohlc_rows=baseline.average_ohlc_rows,
        partial_structure_count=structure_state.structure_count,
        baseline_average_structure_count=baseline.average_structure_count,
        structure_count_vs_baseline_ratio=round(ratio(structure_state.structure_count, baseline.average_structure_count), 4),
        partial_state_count=structure_state.unique_state_count,
        baseline_average_state_count=baseline.average_state_count,
        partial_transition_count=transition_summary.transition_count,
        baseline_average_transition_count=baseline.average_transition_count,
        partial_average_forward_range_pips=price_summary.average_forward_range_pips,
        baseline_average_forward_range_pips=baseline.average_forward_range_pips,
        forward_range_vs_baseline_ratio=round(forward_range_ratio, 4),
        partial_average_outcome_magnitude_pips=price_summary.average_outcome_magnitude_pips,
        baseline_average_outcome_magnitude_pips=baseline.average_outcome_magnitude_pips,
        outcome_magnitude_vs_baseline_ratio=round(outcome_ratio, 4),
        partial_comparison_class=comparison_class,
        partial_comparison_diagnostic=diagnostic_for_comparison(comparison_class),
    )


def ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def classify_comparison(forward_range_ratio: float, outcome_ratio: float) -> str:
    if 0.70 <= forward_range_ratio <= 1.30 and 0.70 <= outcome_ratio <= 1.30:
        return "CONSISTENT_WITH_BASELINE_RANGE"
    if forward_range_ratio > 1.30 or outcome_ratio > 1.30:
        return "ELEVATED_VS_BASELINE"
    if forward_range_ratio < 0.70 and outcome_ratio < 0.70:
        return "LOWER_THAN_BASELINE"
    return "INCONCLUSIVE_COMPARISON"


def diagnostic_for_comparison(comparison_class: str) -> str:
    return {
        "CONSISTENT_WITH_BASELINE_RANGE": "Partial sample metrics sit within the prior H4 baseline range.",
        "ELEVATED_VS_BASELINE": "Partial sample metrics are higher than the prior H4 baseline range.",
        "LOWER_THAN_BASELINE": "Partial sample metrics are lower than the prior H4 baseline range.",
    }.get(comparison_class, "Partial sample comparison requires manual review.")
