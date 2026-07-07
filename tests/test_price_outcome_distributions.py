from __future__ import annotations

from tests.test_price_outcome_summaries import _row

from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.distributions import (
    build_price_outcome_distributions,
    classify_return_bucket,
)


def test_return_bucket_classification() -> None:
    config = PriceOutcomeResearchConfig()

    assert classify_return_bucket(-20.0, config) == "STRONG_NEGATIVE"
    assert classify_return_bucket(-6.0, config) == "MODERATE_NEGATIVE"
    assert classify_return_bucket(0.0, config) == "NEUTRAL"
    assert classify_return_bucket(5.0, config) == "MODERATE_POSITIVE"
    assert classify_return_bucket(20.0, config) == "STRONG_POSITIVE"


def test_price_outcome_distributions_use_complete_windows_only() -> None:
    outcomes = [
        _row("O1", -25.0, True, negative=True),
        _row("O2", 10.0, True, positive=True),
        _row("O3", 2.0, True, positive=True),
        _row("O4", 30.0, False, positive=True),
    ]

    rows = build_price_outcome_distributions(
        outcomes,
        PriceOutcomeResearchConfig(minimum_sample_size=5),
    )

    assert sum(row.count for row in rows) == 3
    assert {row.return_bucket for row in rows} == {
        "STRONG_NEGATIVE",
        "MODERATE_POSITIVE",
        "NEUTRAL",
    }
    assert all(row.sample_size == 3 for row in rows)
    assert all(row.low_sample_size for row in rows)
    assert round(sum(row.frequency for row in rows), 4) == 1.0
