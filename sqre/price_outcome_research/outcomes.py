"""Price outcome calculations."""

from __future__ import annotations

from sqre.price_outcome_research.alignment import find_reference_candle, get_forward_window
from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.models import (
    OHLCCandle,
    PriceOutcomeCondition,
    PriceOutcomeRow,
    PriceOutcomeState,
    PriceOutcomeTransition,
)


def calculate_price_outcome_for_occurrence(
    condition: PriceOutcomeCondition,
    occurrence: PriceOutcomeState | PriceOutcomeTransition,
    candles: list[OHLCCandle],
    forward_window_candles: int,
    config: PriceOutcomeResearchConfig,
) -> PriceOutcomeRow | None:
    occurrence_id, start_time, end_time, reference_time, direction, symbol, timeframe = _occurrence_context(
        occurrence
    )
    reference_index = find_reference_candle(candles, reference_time)
    if reference_index is None:
        return None

    reference_candle = candles[reference_index]
    forward_candles, complete_forward_window = get_forward_window(
        candles,
        reference_index,
        forward_window_candles,
    )
    if not forward_candles:
        return None

    future_close = forward_candles[-1].close
    max_future_high = max(candle.high for candle in forward_candles)
    min_future_low = min(candle.low for candle in forward_candles)
    forward_close_return = future_close - reference_candle.close
    forward_close_return_pips = forward_close_return / config.pip_size
    forward_range_pips = (max_future_high - min_future_low) / config.pip_size
    favorable_pips, adverse_pips = _displacements(
        direction=direction,
        reference_close=reference_candle.close,
        max_future_high=max_future_high,
        min_future_low=min_future_low,
        pip_size=config.pip_size,
    )

    return PriceOutcomeRow(
        outcome_id="",
        condition_id=condition.condition_id,
        condition_type=condition.condition_type,
        condition_value=condition.condition_value,
        occurrence_id=occurrence_id,
        symbol=symbol,
        timeframe=timeframe,
        occurrence_start_time=start_time,
        occurrence_end_time=end_time,
        reference_time=reference_time,
        reference_candle_time=reference_candle.date,
        reference_close=reference_candle.close,
        forward_window_candles=forward_window_candles,
        forward_end_time=forward_candles[-1].date,
        future_close=future_close,
        max_future_high=max_future_high,
        min_future_low=min_future_low,
        direction=direction,
        forward_close_return=forward_close_return,
        forward_close_return_pips=forward_close_return_pips,
        forward_close_return_percent=forward_close_return / reference_candle.close,
        max_favorable_displacement_pips=favorable_pips,
        max_adverse_displacement_pips=adverse_pips,
        forward_range_pips=forward_range_pips,
        direction_aligned=_direction_aligned(direction, forward_close_return),
        positive_close_return=forward_close_return_pips > 0,
        negative_close_return=forward_close_return_pips < 0,
        flat_close_return=forward_close_return_pips == 0,
        outcome_magnitude_pips=abs(forward_close_return_pips),
        complete_forward_window=complete_forward_window,
    )


def build_price_outcomes(
    states: list[PriceOutcomeState],
    transitions: list[PriceOutcomeTransition],
    candles: list[OHLCCandle],
    conditions: list[PriceOutcomeCondition],
    config: PriceOutcomeResearchConfig,
) -> list[PriceOutcomeRow]:
    rows: list[PriceOutcomeRow] = []
    for condition in conditions:
        occurrences = _matching_occurrences(condition, states, transitions)
        for occurrence in occurrences:
            for forward_window_candles in config.forward_candles:
                row = calculate_price_outcome_for_occurrence(
                    condition,
                    occurrence,
                    candles,
                    forward_window_candles,
                    config,
                )
                if row is not None:
                    rows.append(row)
    return [
        PriceOutcomeRow(
            outcome_id=f"OUT_{index:06d}",
            condition_id=row.condition_id,
            condition_type=row.condition_type,
            condition_value=row.condition_value,
            occurrence_id=row.occurrence_id,
            symbol=row.symbol,
            timeframe=row.timeframe,
            occurrence_start_time=row.occurrence_start_time,
            occurrence_end_time=row.occurrence_end_time,
            reference_time=row.reference_time,
            reference_candle_time=row.reference_candle_time,
            reference_close=row.reference_close,
            forward_window_candles=row.forward_window_candles,
            forward_end_time=row.forward_end_time,
            future_close=row.future_close,
            max_future_high=row.max_future_high,
            min_future_low=row.min_future_low,
            direction=row.direction,
            forward_close_return=row.forward_close_return,
            forward_close_return_pips=row.forward_close_return_pips,
            forward_close_return_percent=row.forward_close_return_percent,
            max_favorable_displacement_pips=row.max_favorable_displacement_pips,
            max_adverse_displacement_pips=row.max_adverse_displacement_pips,
            forward_range_pips=row.forward_range_pips,
            direction_aligned=row.direction_aligned,
            positive_close_return=row.positive_close_return,
            negative_close_return=row.negative_close_return,
            flat_close_return=row.flat_close_return,
            outcome_magnitude_pips=row.outcome_magnitude_pips,
            complete_forward_window=row.complete_forward_window,
        )
        for index, row in enumerate(rows, start=1)
    ]


def _matching_occurrences(
    condition: PriceOutcomeCondition,
    states: list[PriceOutcomeState],
    transitions: list[PriceOutcomeTransition],
) -> list[PriceOutcomeState | PriceOutcomeTransition]:
    if condition.condition_type == "STATE_CONDITION":
        return [state for state in states if state.market_state == condition.market_state]
    if condition.condition_type == "TRANSITION_CONDITION":
        return [
            transition
            for transition in transitions
            if transition.transition_label == condition.transition_label
        ]
    return []


def _occurrence_context(
    occurrence: PriceOutcomeState | PriceOutcomeTransition,
) -> tuple[str, object, object, object, str, str, str]:
    if isinstance(occurrence, PriceOutcomeState):
        return (
            occurrence.state_id,
            occurrence.start_time,
            occurrence.end_time,
            occurrence.end_time,
            occurrence.direction,
            occurrence.symbol,
            occurrence.timeframe,
        )
    return (
        occurrence.transition_id,
        occurrence.start_time,
        occurrence.end_time,
        occurrence.end_time,
        occurrence.to_direction,
        occurrence.symbol,
        occurrence.timeframe,
    )


def _displacements(
    *,
    direction: str,
    reference_close: float,
    max_future_high: float,
    min_future_low: float,
    pip_size: float,
) -> tuple[float, float]:
    normalized_direction = direction.upper()
    if normalized_direction == "UP":
        favorable = max_future_high - reference_close
        adverse = reference_close - min_future_low
    elif normalized_direction == "DOWN":
        favorable = reference_close - min_future_low
        adverse = max_future_high - reference_close
    else:
        favorable = max(abs(max_future_high - reference_close), abs(reference_close - min_future_low))
        adverse = favorable
    return favorable / pip_size, adverse / pip_size


def _direction_aligned(direction: str, forward_close_return: float) -> bool:
    normalized_direction = direction.upper()
    if normalized_direction == "UP":
        return forward_close_return > 0
    if normalized_direction == "DOWN":
        return forward_close_return < 0
    return False
