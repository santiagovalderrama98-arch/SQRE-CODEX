"""Normalize or derive timestamped state transition outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_state_transition_outputs.loader import (
    CONFIDENCE_ALIASES,
    SCENARIO_ALIASES,
    SOURCE_STATE_ALIASES,
    STATE_START_ALIASES,
    STATE_END_ALIASES,
    SYMBOL_ALIASES,
    TARGET_STATE_ALIASES,
    TIMEFRAME_ALIASES,
    TIMESTAMP_ALIASES,
    TRANSITION_ALIASES,
    iso_date,
    read_optional_csv,
    resolve_column,
    row_text,
    stable_time,
)
from sqre.h4_timestamped_state_transition_outputs.models import (
    ScenarioInventoryRow,
    TimestampedMarketStateRow,
    TimestampedStateTransitionRow,
)
from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import TimestampedOutputSource


def normalize_transition_outputs(
    sources: list[TimestampedOutputSource],
    scenarios: list[ScenarioInventoryRow],
    symbol: str,
    timeframe: str,
) -> list[TimestampedStateTransitionRow]:
    scenario_map = {scenario.scenario_id: scenario for scenario in scenarios}
    rows: list[TimestampedStateTransitionRow] = []
    for source in sources:
        if source.source_type != "TIMESTAMPED_TRANSITION_SOURCE":
            continue
        rows.extend(_normalize_source(source.path, scenario_map, scenarios, symbol, timeframe, len(rows)))
    return rows


def build_transitions_from_states(
    state_rows: list[TimestampedMarketStateRow],
) -> list[TimestampedStateTransitionRow]:
    by_scenario: dict[str, list[TimestampedMarketStateRow]] = {}
    for row in state_rows:
        by_scenario.setdefault(row.scenario_id, []).append(row)
    transitions: list[TimestampedStateTransitionRow] = []
    for rows in by_scenario.values():
        parsed = [pd.to_datetime(row.state_event_time or row.state_start_time, errors="coerce") for row in rows]
        if any(pd.isna(value) for value in parsed):
            continue
        if parsed != sorted(parsed):
            continue
        for previous, current in zip(rows, rows[1:]):
            transition_time = current.state_start_time or current.state_event_time
            label = f"{previous.market_state} -> {current.market_state}"
            transitions.append(
                TimestampedStateTransitionRow(
                    h4_timestamped_transition_id=f"H4_TRANSITION_{len(transitions) + 1:06d}",
                    scenario_id=current.scenario_id,
                    symbol=current.symbol,
                    timeframe=current.timeframe,
                    scenario_period_start=current.scenario_period_start,
                    scenario_period_end=current.scenario_period_end,
                    transition_time=transition_time,
                    transition_date=iso_date(transition_time),
                    source_state=previous.market_state,
                    target_state=current.market_state,
                    transition_label=label,
                    source_state_start_time=previous.state_start_time,
                    source_state_end_time=previous.state_end_time,
                    target_state_start_time=current.state_start_time,
                    target_state_end_time=current.state_end_time,
                    source_state_confidence=previous.state_confidence,
                    target_state_confidence=current.state_confidence,
                    transition_row_source="DERIVED_FROM_TIMESTAMPED_STATES",
                    transition_row_diagnostic="Transition derived from ordered timestamped state rows.",
                )
            )
    return transitions


def _normalize_source(
    path: Path,
    scenario_map: dict[str, ScenarioInventoryRow],
    scenarios: list[ScenarioInventoryRow],
    default_symbol: str,
    default_timeframe: str,
    offset: int,
) -> list[TimestampedStateTransitionRow]:
    frame = read_optional_csv(path)
    timestamp_column = resolve_column(frame, TIMESTAMP_ALIASES)
    source_column = resolve_column(frame, SOURCE_STATE_ALIASES)
    target_column = resolve_column(frame, TARGET_STATE_ALIASES)
    if frame.empty or timestamp_column is None or source_column is None or target_column is None:
        return []
    scenario_column = resolve_column(frame, SCENARIO_ALIASES)
    normalized: list[TimestampedStateTransitionRow] = []
    for _, row in frame.iterrows():
        scenario = _resolve_scenario(row, scenario_column, scenario_map, scenarios)
        if scenario is None:
            continue
        row_timeframe = row_text(row, TIMEFRAME_ALIASES, scenario.timeframe or default_timeframe)
        if row_timeframe and row_timeframe.upper() != default_timeframe.upper():
            continue
        source_state = row_text(row, SOURCE_STATE_ALIASES)
        target_state = row_text(row, TARGET_STATE_ALIASES)
        transition_time = stable_time(row_text(row, TIMESTAMP_ALIASES))
        if not transition_time or not source_state or not target_state:
            continue
        label = row_text(row, TRANSITION_ALIASES, f"{source_state} -> {target_state}") or f"{source_state} -> {target_state}"
        transition_id = f"H4_TRANSITION_{offset + len(normalized) + 1:06d}"
        normalized.append(
            TimestampedStateTransitionRow(
                h4_timestamped_transition_id=transition_id,
                scenario_id=scenario.scenario_id,
                symbol=row_text(row, SYMBOL_ALIASES, scenario.symbol or default_symbol) or default_symbol,
                timeframe=row_timeframe or default_timeframe,
                scenario_period_start=scenario.period_start,
                scenario_period_end=scenario.period_end,
                transition_time=transition_time,
                transition_date=iso_date(transition_time),
                source_state=source_state,
                target_state=target_state,
                transition_label=label,
                source_state_start_time=stable_time(row_text(row, ["Source_State_Start_Time"] + STATE_START_ALIASES)),
                source_state_end_time=stable_time(row_text(row, ["Source_State_End_Time"] + STATE_END_ALIASES)),
                target_state_start_time=stable_time(row_text(row, ["Target_State_Start_Time"] + STATE_START_ALIASES)),
                target_state_end_time=stable_time(row_text(row, ["Target_State_End_Time"] + STATE_END_ALIASES)),
                source_state_confidence=row_text(row, ["Source_State_Confidence"] + CONFIDENCE_ALIASES),
                target_state_confidence=row_text(row, ["Target_State_Confidence"] + CONFIDENCE_ALIASES),
                transition_row_source=str(path),
                transition_row_diagnostic="Timestamped transition row normalized from source output.",
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
