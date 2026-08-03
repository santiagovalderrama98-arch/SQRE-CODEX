"""Normalize timestamped market state outputs into the SQRE research schema."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.loader import (
    CONFIDENCE_ALIASES,
    SCENARIO_ALIASES,
    STATE_ALIASES,
    STATE_END_ALIASES,
    STATE_START_ALIASES,
    STRUCTURAL_CONFIDENCE_ALIASES,
    STRUCTURAL_EFFICIENCY_ALIASES,
    STRUCTURE_DIRECTION_ALIASES,
    STRUCTURE_ID_ALIASES,
    SYMBOL_ALIASES,
    TIMEFRAME_ALIASES,
    TIMESTAMP_ALIASES,
    iso_date,
    read_optional_csv,
    resolve_column,
    row_text,
    stable_time,
)
from sqre.h4_timestamped_state_transition_outputs.models import ScenarioInventoryRow, TimestampedMarketStateRow
from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import TimestampedOutputSource


def normalize_state_outputs(
    sources: list[TimestampedOutputSource],
    scenarios: list[ScenarioInventoryRow],
    symbol: str,
    timeframe: str,
) -> list[TimestampedMarketStateRow]:
    scenario_map = {scenario.scenario_id: scenario for scenario in scenarios}
    rows: list[TimestampedMarketStateRow] = []
    for source in sources:
        if source.source_type != "TIMESTAMPED_STATE_SOURCE":
            continue
        rows.extend(_normalize_source(source.path, scenario_map, scenarios, symbol, timeframe, len(rows)))
    return rows


def _normalize_source(
    path: Path,
    scenario_map: dict[str, ScenarioInventoryRow],
    scenarios: list[ScenarioInventoryRow],
    default_symbol: str,
    default_timeframe: str,
    offset: int,
) -> list[TimestampedMarketStateRow]:
    frame = read_optional_csv(path)
    timestamp_column = resolve_column(frame, TIMESTAMP_ALIASES)
    state_column = resolve_column(frame, STATE_ALIASES)
    if frame.empty or timestamp_column is None or state_column is None:
        return []
    scenario_column = resolve_column(frame, SCENARIO_ALIASES)
    normalized: list[TimestampedMarketStateRow] = []
    for _, row in frame.iterrows():
        scenario = _resolve_scenario(row, scenario_column, scenario_map, scenarios)
        if scenario is None:
            continue
        row_timeframe = row_text(row, TIMEFRAME_ALIASES, scenario.timeframe or default_timeframe)
        if row_timeframe and row_timeframe.upper() != default_timeframe.upper():
            continue
        event_time = stable_time(row_text(row, TIMESTAMP_ALIASES))
        start_time = stable_time(row_text(row, STATE_START_ALIASES, event_time))
        end_time = stable_time(row_text(row, STATE_END_ALIASES))
        market_state = row_text(row, STATE_ALIASES)
        if not event_time or not market_state:
            continue
        state_id = f"H4_STATE_{offset + len(normalized) + 1:06d}"
        normalized.append(
            TimestampedMarketStateRow(
                h4_timestamped_state_id=state_id,
                scenario_id=scenario.scenario_id,
                symbol=row_text(row, SYMBOL_ALIASES, scenario.symbol or default_symbol) or default_symbol,
                timeframe=row_timeframe or default_timeframe,
                scenario_period_start=scenario.period_start,
                scenario_period_end=scenario.period_end,
                state_start_time=start_time,
                state_end_time=end_time,
                state_event_time=event_time,
                state_event_date=iso_date(event_time),
                market_state=market_state,
                state_confidence=row_text(row, CONFIDENCE_ALIASES),
                structure_id=row_text(row, STRUCTURE_ID_ALIASES),
                structure_direction=row_text(row, STRUCTURE_DIRECTION_ALIASES),
                structural_efficiency=row_text(row, STRUCTURAL_EFFICIENCY_ALIASES),
                structural_confidence=row_text(row, STRUCTURAL_CONFIDENCE_ALIASES),
                state_row_source=str(path),
                state_row_diagnostic="Timestamped state row normalized from source output.",
            )
        )
    return normalized


def _resolve_scenario(row, scenario_column: str | None, scenario_map: dict[str, ScenarioInventoryRow], scenarios):
    if scenario_column is not None:
        scenario_id = str(row.get(scenario_column, "")).strip()
        return scenario_map.get(scenario_id)
    if len(scenarios) == 1:
        return scenarios[0]
    return None
