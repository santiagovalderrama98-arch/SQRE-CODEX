"""Extract timestamped H4 context rows from discovered sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.loader import (
    FORWARD_WINDOW_ALIASES,
    PERIOD_END_ALIASES,
    PERIOD_START_ALIASES,
    SCENARIO_ALIASES,
    SINGLE_STATE_ALIASES,
    SOURCE_STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TRANSITION_ALIASES,
    read_optional_csv,
    row_text,
)
from sqre.h4_timestamped_context_table_generation.models import ScenarioInventoryRow, TimestampedContextRow
from sqre.h4_timestamped_context_table_generation.temporal_key_builder import event_date, temporal_key_class
from sqre.h4_timestamped_context_table_generation.timestamped_source_discovery import TimestampedSource


def extract_timestamped_context_rows(
    sources: list[TimestampedSource],
    scenarios: list[ScenarioInventoryRow],
    config: H4TimestampedContextTableGenerationConfig,
) -> tuple[list[TimestampedContextRow], set[str], set[str]]:
    scenario_lookup = {scenario.scenario_id: scenario for scenario in scenarios}
    rows: list[TimestampedContextRow] = []
    state_scenario_ids: set[str] = set()
    transition_scenario_ids: set[str] = set()
    for source in sources:
        frame = read_optional_csv(source.path)
        if source.source_type == "TIMESTAMPED_TRANSITION_SOURCE":
            extracted = _extract_transition_rows(frame, source.path, scenario_lookup, config, len(rows))
            transition_scenario_ids.update(row.scenario_id for row in extracted)
            rows.extend(extracted)
        else:
            state_scenario_ids.update(_state_scenario_ids(frame))
            extracted = _extract_sequential_state_rows(frame, source.path, scenario_lookup, config, len(rows))
            rows.extend(extracted)
    return rows, state_scenario_ids, transition_scenario_ids


def _extract_transition_rows(
    frame: pd.DataFrame,
    path: Path,
    scenario_lookup: dict[str, ScenarioInventoryRow],
    config: H4TimestampedContextTableGenerationConfig,
    offset: int,
) -> list[TimestampedContextRow]:
    rows: list[TimestampedContextRow] = []
    for index, row in frame.iterrows():
        event_time = row_text(row, ["Timestamp", "Date", "Datetime", "Time", "Event_Time", "Transition_Time", "Candle_Time"])
        if not event_time:
            continue
        scenario_id = row_text(row, SCENARIO_ALIASES, "")
        scenario = scenario_lookup.get(scenario_id)
        period_start = row_text(row, PERIOD_START_ALIASES, scenario.period_start if scenario else "")
        period_end = row_text(row, PERIOD_END_ALIASES, scenario.period_end if scenario else "")
        source_state = row_text(row, SOURCE_STATE_ALIASES)
        target_state = row_text(row, TARGET_STATE_ALIASES)
        transition_label = row_text(row, TRANSITION_ALIASES, _transition_label(source_state, target_state))
        forward_window = row_text(row, FORWARD_WINDOW_ALIASES)
        rows.append(
            TimestampedContextRow(
                h4_timestamped_context_id=f"H4_TS_CTX_{offset + len(rows) + 1:06d}",
                aggregate_context_id="",
                symbol=config.symbol,
                timeframe=config.timeframe,
                scenario_id=scenario_id or "SCENARIO_UNKNOWN",
                scenario_period_start=period_start,
                scenario_period_end=period_end,
                h4_event_time=event_time,
                h4_event_date=event_date(event_time),
                h4_source_state=source_state,
                h4_target_state=target_state,
                h4_transition_label=transition_label,
                h4_forward_window=forward_window,
                h4_temporal_key_class=temporal_key_class(event_time, period_start, period_end),
                h4_d1_alignment_date_key=event_date(event_time),
                aggregate_context_match_method="NO_AGGREGATE_CONTEXT_MATCH",
                aggregate_context_match_confidence="NO_CONTEXT_MATCH",
                context_row_diagnostic=f"Timestamped H4 transition row extracted from {path.name}.",
            )
        )
    return rows


def _extract_sequential_state_rows(
    frame: pd.DataFrame,
    path: Path,
    scenario_lookup: dict[str, ScenarioInventoryRow],
    config: H4TimestampedContextTableGenerationConfig,
    offset: int,
) -> list[TimestampedContextRow]:
    if frame.empty:
        return []
    work = frame.copy()
    time_col = _first_existing_column(work, ["Timestamp", "Date", "Datetime", "Time", "Event_Time", "State_Time", "Candle_Time"])
    state_col = _first_existing_column(work, SINGLE_STATE_ALIASES)
    if time_col is None or state_col is None:
        return []
    scenario_col = _first_existing_column(work, SCENARIO_ALIASES)
    work["_parsed_time"] = pd.to_datetime(work[time_col], errors="coerce")
    if work["_parsed_time"].isna().any():
        return []
    if work.duplicated(subset=[scenario_col, "_parsed_time"] if scenario_col else ["_parsed_time"]).any():
        return []
    sort_columns = [scenario_col, "_parsed_time"] if scenario_col else ["_parsed_time"]
    work = work.sort_values(sort_columns)
    rows: list[TimestampedContextRow] = []
    grouped = work.groupby(scenario_col, dropna=False) if scenario_col else [(None, work)]
    for scenario_id_raw, group in grouped:
        previous = None
        scenario_id = str(scenario_id_raw).strip() if scenario_id_raw is not None and not pd.isna(scenario_id_raw) else ""
        scenario = scenario_lookup.get(scenario_id)
        for _, row in group.iterrows():
            if previous is None:
                previous = row
                continue
            source_state = str(previous[state_col]).strip()
            target_state = str(row[state_col]).strip()
            event_time = str(row[time_col]).strip()
            period_start = row_text(row, PERIOD_START_ALIASES, scenario.period_start if scenario else "")
            period_end = row_text(row, PERIOD_END_ALIASES, scenario.period_end if scenario else "")
            rows.append(
                TimestampedContextRow(
                    h4_timestamped_context_id=f"H4_TS_CTX_{offset + len(rows) + 1:06d}",
                    aggregate_context_id="",
                    symbol=config.symbol,
                    timeframe=config.timeframe,
                    scenario_id=scenario_id or "SCENARIO_UNKNOWN",
                    scenario_period_start=period_start,
                    scenario_period_end=period_end,
                    h4_event_time=event_time,
                    h4_event_date=event_date(event_time),
                    h4_source_state=source_state,
                    h4_target_state=target_state,
                    h4_transition_label=_transition_label(source_state, target_state),
                    h4_forward_window=row_text(row, FORWARD_WINDOW_ALIASES),
                    h4_temporal_key_class=temporal_key_class(event_time, period_start, period_end),
                    h4_d1_alignment_date_key=event_date(event_time),
                    aggregate_context_match_method="NO_AGGREGATE_CONTEXT_MATCH",
                    aggregate_context_match_confidence="NO_CONTEXT_MATCH",
                    context_row_diagnostic=f"Sequential timestamped H4 state row extracted from {path.name}.",
                )
            )
            previous = row
    return rows


def _state_scenario_ids(frame: pd.DataFrame) -> set[str]:
    column = _first_existing_column(frame, SCENARIO_ALIASES)
    if column is None:
        return set()
    return {str(value).strip() for value in frame[column].dropna() if str(value).strip()}


def _first_existing_column(frame: pd.DataFrame, aliases: list[str]) -> str | None:
    lookup = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = lookup.get(alias.lower())
        if column is not None:
            return column
    return None


def _transition_label(source_state: str, target_state: str) -> str:
    if source_state and target_state:
        return f"{source_state} -> {target_state}"
    return ""
