"""Condition-level price outcome summaries."""

from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Iterable

from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.models import ConditionPriceOutcomeSummaryRow, PriceOutcomeRow


def build_condition_price_outcome_summaries(
    outcomes: list[PriceOutcomeRow],
    config: PriceOutcomeResearchConfig,
) -> list[ConditionPriceOutcomeSummaryRow]:
    rows: list[ConditionPriceOutcomeSummaryRow] = []
    for key, group in sorted(_group_outcomes(outcomes).items()):
        condition_id, condition_type, condition_value, forward_window_candles = key
        complete = [outcome for outcome in group if outcome.complete_forward_window]
        incomplete_forward_cases = len(group) - len(complete)
        sample_size = len(complete)
        rows.append(
            ConditionPriceOutcomeSummaryRow(
                condition_id=condition_id,
                condition_type=condition_type,
                condition_value=condition_value,
                forward_window_candles=forward_window_candles,
                sample_size=sample_size,
                incomplete_forward_cases=incomplete_forward_cases,
                low_sample_size=sample_size < config.minimum_sample_size,
                average_forward_close_return_pips=_average(
                    outcome.forward_close_return_pips for outcome in complete
                ),
                median_forward_close_return_pips=_median(
                    outcome.forward_close_return_pips for outcome in complete
                ),
                average_forward_range_pips=_average(
                    outcome.forward_range_pips for outcome in complete
                ),
                average_max_favorable_displacement_pips=_average(
                    outcome.max_favorable_displacement_pips for outcome in complete
                ),
                average_max_adverse_displacement_pips=_average(
                    outcome.max_adverse_displacement_pips for outcome in complete
                ),
                average_outcome_magnitude_pips=_average(
                    outcome.outcome_magnitude_pips for outcome in complete
                ),
                direction_alignment_rate=_rate(
                    sum(outcome.direction_aligned for outcome in complete),
                    sample_size,
                ),
                positive_close_return_rate=_rate(
                    sum(outcome.positive_close_return for outcome in complete),
                    sample_size,
                ),
                negative_close_return_rate=_rate(
                    sum(outcome.negative_close_return for outcome in complete),
                    sample_size,
                ),
                flat_close_return_rate=_rate(
                    sum(outcome.flat_close_return for outcome in complete),
                    sample_size,
                ),
            )
        )
    return rows


def _group_outcomes(
    outcomes: list[PriceOutcomeRow],
) -> dict[tuple[str, str, str, int], list[PriceOutcomeRow]]:
    groups: dict[tuple[str, str, str, int], list[PriceOutcomeRow]] = defaultdict(list)
    for outcome in outcomes:
        groups[
            (
                outcome.condition_id,
                outcome.condition_type,
                outcome.condition_value,
                outcome.forward_window_candles,
            )
        ].append(outcome)
    return dict(groups)


def _average(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


def _median(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return float(median(items))


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return count / total
