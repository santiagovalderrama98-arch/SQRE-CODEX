from __future__ import annotations

from datetime import datetime

from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.models import PriceOutcomeRow
from sqre.price_outcome_research.summaries import build_condition_price_outcome_summaries


def test_price_outcome_summaries_use_complete_windows_only_and_count_incomplete() -> None:
    outcomes = [
        _row("O1", 10.0, True, aligned=True, positive=True),
        _row("O2", -5.0, True, negative=True),
        _row("O3", 20.0, False, positive=True),
    ]

    rows = build_condition_price_outcome_summaries(
        outcomes,
        PriceOutcomeResearchConfig(minimum_sample_size=3),
    )

    assert len(rows) == 1
    row = rows[0]
    assert row.sample_size == 2
    assert row.incomplete_forward_cases == 1
    assert row.low_sample_size is True
    assert row.average_forward_close_return_pips == 2.5
    assert row.median_forward_close_return_pips == 2.5
    assert row.average_forward_range_pips == 30.0
    assert row.average_max_favorable_displacement_pips == 15.0
    assert row.average_max_adverse_displacement_pips == 5.0
    assert row.average_outcome_magnitude_pips == 7.5
    assert row.direction_alignment_rate == 0.5
    assert row.positive_close_return_rate == 0.5
    assert row.negative_close_return_rate == 0.5
    assert row.flat_close_return_rate == 0.0


def test_price_outcome_summaries_are_safe_when_sample_size_is_zero() -> None:
    rows = build_condition_price_outcome_summaries(
        [_row("O1", 10.0, False, positive=True)],
        PriceOutcomeResearchConfig(),
    )

    assert rows[0].sample_size == 0
    assert rows[0].average_forward_close_return_pips == 0.0
    assert rows[0].direction_alignment_rate == 0.0


def _row(
    outcome_id: str,
    return_pips: float,
    complete: bool,
    *,
    aligned: bool = False,
    positive: bool = False,
    negative: bool = False,
) -> PriceOutcomeRow:
    now = datetime(2026, 1, 1)
    return PriceOutcomeRow(
        outcome_id=outcome_id,
        condition_id="COND_000001",
        condition_type="STATE_CONDITION",
        condition_value="A",
        occurrence_id="S1",
        symbol="EURUSD",
        timeframe="H1",
        occurrence_start_time=now,
        occurrence_end_time=now,
        reference_time=now,
        reference_candle_time=now,
        reference_close=1.1,
        forward_window_candles=3,
        forward_end_time=now,
        future_close=1.1 + return_pips * 0.0001,
        max_future_high=1.102,
        min_future_low=1.099,
        direction="UP",
        forward_close_return=return_pips * 0.0001,
        forward_close_return_pips=return_pips,
        forward_close_return_percent=0.0,
        max_favorable_displacement_pips=15.0,
        max_adverse_displacement_pips=5.0,
        forward_range_pips=30.0,
        direction_aligned=aligned,
        positive_close_return=positive,
        negative_close_return=negative,
        flat_close_return=not positive and not negative,
        outcome_magnitude_pips=abs(return_pips),
        complete_forward_window=complete,
    )
