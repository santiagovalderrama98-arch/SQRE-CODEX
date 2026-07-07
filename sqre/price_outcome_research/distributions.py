"""Price outcome return distributions."""

from __future__ import annotations

from collections import Counter, defaultdict

from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.models import PriceOutcomeDistributionRow, PriceOutcomeRow


RETURN_BUCKET_ORDER = [
    "STRONG_NEGATIVE",
    "MODERATE_NEGATIVE",
    "NEUTRAL",
    "MODERATE_POSITIVE",
    "STRONG_POSITIVE",
]


def classify_return_bucket(
    forward_close_return_pips: float,
    config: PriceOutcomeResearchConfig,
) -> str:
    if forward_close_return_pips <= config.strong_negative_threshold_pips:
        return "STRONG_NEGATIVE"
    if forward_close_return_pips <= config.moderate_negative_threshold_pips:
        return "MODERATE_NEGATIVE"
    if forward_close_return_pips < config.moderate_positive_threshold_pips:
        return "NEUTRAL"
    if forward_close_return_pips < config.strong_positive_threshold_pips:
        return "MODERATE_POSITIVE"
    return "STRONG_POSITIVE"


def build_price_outcome_distributions(
    outcomes: list[PriceOutcomeRow],
    config: PriceOutcomeResearchConfig,
) -> list[PriceOutcomeDistributionRow]:
    rows: list[PriceOutcomeDistributionRow] = []
    for key, group in sorted(_group_complete_outcomes(outcomes).items()):
        condition_id, condition_type, condition_value, forward_window_candles = key
        sample_size = len(group)
        bucket_counts = Counter(
            classify_return_bucket(outcome.forward_close_return_pips, config) for outcome in group
        )
        for bucket in RETURN_BUCKET_ORDER:
            count = bucket_counts.get(bucket, 0)
            if count == 0:
                continue
            frequency = count / sample_size if sample_size else 0.0
            rows.append(
                PriceOutcomeDistributionRow(
                    condition_id=condition_id,
                    condition_type=condition_type,
                    condition_value=condition_value,
                    forward_window_candles=forward_window_candles,
                    return_bucket=bucket,
                    count=count,
                    frequency=frequency,
                    percentage=frequency * 100,
                    sample_size=sample_size,
                    low_sample_size=sample_size < config.minimum_sample_size,
                )
            )
    return rows


def _group_complete_outcomes(
    outcomes: list[PriceOutcomeRow],
) -> dict[tuple[str, str, str, int], list[PriceOutcomeRow]]:
    groups: dict[tuple[str, str, str, int], list[PriceOutcomeRow]] = defaultdict(list)
    for outcome in outcomes:
        if not outcome.complete_forward_window:
            continue
        groups[
            (
                outcome.condition_id,
                outcome.condition_type,
                outcome.condition_value,
                outcome.forward_window_candles,
            )
        ].append(outcome)
    return dict(groups)
