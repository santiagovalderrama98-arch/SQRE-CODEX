"""Temporal key inventory for H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_temporal_alignment_feasibility_review.loader import joined, read_optional_csv, resolve_columns
from sqre.h4_d1_temporal_alignment_feasibility_review.models import SourceInventoryRow, TemporalKeyInventoryRow


TIMESTAMP_ALIASES = [
    "Timestamp",
    "Date",
    "Datetime",
    "Time",
    "Event_Time",
    "State_Time",
    "Transition_Time",
    "Structure_Time",
    "Candle_Time",
]
START_TIME_ALIASES = [
    "Start_Time",
    "Start_Date",
    "Period_Start",
    "Scenario_Start",
    "Structure_Start",
    "State_Start",
    "Transition_Start",
    "From_Date",
]
END_TIME_ALIASES = [
    "End_Time",
    "End_Date",
    "Period_End",
    "Scenario_End",
    "Structure_End",
    "State_End",
    "Transition_End",
    "To_Date",
]
SCENARIO_ID_ALIASES = ["Scenario_ID", "Validation_Scenario_ID", "Sample_ID", "Period_ID"]
TIMEFRAME_ALIASES = ["Timeframe", "TF"]
CONDITION_ONLY_ALIASES = [
    "Context_ID",
    "Condition_Label",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Forward_Window",
    "Forward_Window_Candles",
]
REGIME_ALIASES = ["Regime_ID", "Regime_Label", "D1_Regime_Label", "Regimes_Present"]


def build_temporal_key_inventory(sources: list[SourceInventoryRow]) -> list[TemporalKeyInventoryRow]:
    return [_key_row(source) for source in sources]


def has_exact_timestamp(row: TemporalKeyInventoryRow) -> bool:
    return bool(row.timestamp_columns)


def has_start_end(row: TemporalKeyInventoryRow) -> bool:
    return bool(row.start_time_columns and row.end_time_columns)


def has_scenario_period(row: TemporalKeyInventoryRow) -> bool:
    return bool(row.scenario_id_columns and row.start_time_columns and row.end_time_columns)


def has_condition_only(row: TemporalKeyInventoryRow) -> bool:
    return bool(row.condition_only_columns)


def has_temporal_alignment_keys(row: TemporalKeyInventoryRow) -> bool:
    return has_exact_timestamp(row) or has_start_end(row) or has_scenario_period(row)


def _key_row(source: SourceInventoryRow) -> TemporalKeyInventoryRow:
    path = Path(source.path)
    frame = read_optional_csv(path)
    if not source.exists:
        return TemporalKeyInventoryRow(
            source.source_name,
            source.source_type,
            path.name,
            0,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "INPUT_MISSING",
            "Source file is missing, so temporal keys cannot be inspected.",
        )
    timestamp = resolve_columns(frame, TIMESTAMP_ALIASES)
    start = resolve_columns(frame, START_TIME_ALIASES)
    end = resolve_columns(frame, END_TIME_ALIASES)
    scenario = resolve_columns(frame, SCENARIO_ID_ALIASES)
    timeframe = resolve_columns(frame, TIMEFRAME_ALIASES)
    condition = resolve_columns(frame, CONDITION_ONLY_ALIASES)
    regime = resolve_columns(frame, REGIME_ALIASES)
    status = _status(timestamp, start, end, scenario, condition)
    return TemporalKeyInventoryRow(
        source.source_name,
        source.source_type,
        path.name,
        source.rows_loaded,
        joined(timestamp),
        joined(start),
        joined(end),
        joined(scenario),
        joined(timeframe),
        joined(condition),
        joined(regime),
        status,
        _diagnostic(status),
    )


def _status(
    timestamp: list[str],
    start: list[str],
    end: list[str],
    scenario: list[str],
    condition: list[str],
) -> str:
    if timestamp:
        return "EXACT_TIMESTAMP_KEYS_AVAILABLE"
    if scenario and start and end:
        return "SCENARIO_PERIOD_KEYS_AVAILABLE"
    if start and end:
        if _date_range_only(start, end):
            return "DATE_RANGE_KEYS_AVAILABLE"
        return "START_END_TIME_KEYS_AVAILABLE"
    if condition:
        return "CONDITION_ONLY_KEYS_AVAILABLE"
    return "TEMPORAL_KEYS_MISSING"


def _date_range_only(start: list[str], end: list[str]) -> bool:
    text = "|".join([*start, *end]).lower()
    return "date" in text and "time" not in text and "period" not in text and "scenario" not in text


def _diagnostic(status: str) -> str:
    diagnostics = {
        "EXACT_TIMESTAMP_KEYS_AVAILABLE": "Exact timestamp columns are available for same-time inspection.",
        "START_END_TIME_KEYS_AVAILABLE": "Start/end interval columns are available for overlap inspection.",
        "SCENARIO_PERIOD_KEYS_AVAILABLE": "Scenario and period interval keys are available.",
        "DATE_RANGE_KEYS_AVAILABLE": "Date-range columns are available without explicit scenario identifiers.",
        "CONDITION_ONLY_KEYS_AVAILABLE": (
            "Only condition/state/transition/window keys are available; this is not same-time temporal alignment."
        ),
        "TEMPORAL_KEYS_MISSING": "No temporal, scenario-period, or condition-level keys were detected.",
        "INPUT_MISSING": "Input file is missing.",
    }
    return diagnostics[status]
