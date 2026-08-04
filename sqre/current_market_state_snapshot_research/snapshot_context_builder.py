"""Build current/latest-available snapshot context rows."""

from __future__ import annotations

import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.snapshot_validation import validate_snapshot_context
from sqre.research_reference_store_usage_review.reference_query_builder import int_value, row_value, text_value


SNAPSHOT_CONTEXT_COLUMNS = [
    "Snapshot_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Snapshot_Mode",
    "Snapshot_Source",
    "Snapshot_Timestamp",
    "Snapshot_Timestamp_Status",
    "H4_Transition_Label",
    "H4_Market_State",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Snapshot_Validation_Status",
    "Snapshot_Diagnostic",
]
TIMESTAMP_ALIASES = [
    "H4_Transition_Timestamp",
    "H4_Timestamp",
    "Timestamp",
    "Date",
    "H4_End_Timestamp",
    "Transition_Timestamp",
]


def build_snapshot_context(frames: dict[str, pd.DataFrame], config: CurrentMarketStateSnapshotResearchConfig) -> pd.DataFrame:
    mode = config.normalized_snapshot_mode()
    if mode == "USER_SUPPLIED_SNAPSHOT":
        record = _user_supplied(config)
    else:
        record = _latest_available(frames, config)
    status, diagnostic = validate_snapshot_context(pd.Series(record))
    record["Snapshot_Validation_Status"] = status
    record["Snapshot_Diagnostic"] = diagnostic
    return pd.DataFrame([record], columns=SNAPSHOT_CONTEXT_COLUMNS)


def _base(config: CurrentMarketStateSnapshotResearchConfig, mode: str, source: str) -> dict[str, object]:
    return {
        "Snapshot_ID": "CMS_000001",
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Snapshot_Mode": mode,
        "Snapshot_Source": source,
        "Snapshot_Timestamp": "",
        "Snapshot_Timestamp_Status": "TIMESTAMP_MISSING",
        "H4_Transition_Label": "",
        "H4_Market_State": "",
        "D1_Market_State": "",
        "D1_Regime_Label": "",
        "D1_Structure_Direction": "",
        "Snapshot_Validation_Status": "",
        "Snapshot_Diagnostic": "",
    }


def _user_supplied(config: CurrentMarketStateSnapshotResearchConfig) -> dict[str, object]:
    record = _base(config, "USER_SUPPLIED_SNAPSHOT", "USER_SUPPLIED_CONTEXT")
    record.update(
        {
            "Snapshot_Timestamp": text_value(config.snapshot_timestamp, ""),
            "Snapshot_Timestamp_Status": "USER_SUPPLIED_TIMESTAMP" if config.snapshot_timestamp else "TIMESTAMP_MISSING",
            "H4_Transition_Label": text_value(config.snapshot_h4_transition_label, ""),
            "H4_Market_State": text_value(config.snapshot_h4_market_state, ""),
            "D1_Market_State": text_value(config.snapshot_d1_market_state, ""),
            "D1_Regime_Label": text_value(config.snapshot_d1_regime_label, ""),
            "D1_Structure_Direction": text_value(config.snapshot_d1_structure_direction, ""),
        }
    )
    return record


def _latest_available(frames: dict[str, pd.DataFrame], config: CurrentMarketStateSnapshotResearchConfig) -> dict[str, object]:
    alignment = frames.get("transition_alignment", pd.DataFrame())
    if not alignment.empty:
        row, timestamp, timestamp_status = _latest_row(alignment)
        return _from_row(row, config, "LATEST_AVAILABLE_SNAPSHOT", "SAME_TIME_ALIGNMENT_LATEST_ROW", timestamp, timestamp_status)
    transitions = frames.get("h4_timestamped_transitions", pd.DataFrame())
    if not transitions.empty:
        row, timestamp, timestamp_status = _latest_row(transitions)
        record = _from_row(
            row,
            config,
            "LATEST_AVAILABLE_SNAPSHOT",
            "TIMESTAMPED_STATE_REGIME_LATEST_ROW",
            timestamp,
            timestamp_status,
        )
        d1 = frames.get("d1_timestamped_states", pd.DataFrame())
        if not d1.empty:
            d1_row, _, _ = _latest_row(d1)
            record["D1_Market_State"] = _first_text(d1_row, ["D1_Market_State", "Market_State", "State", "D1_State"])
            record["D1_Regime_Label"] = _first_text(d1_row, ["D1_Regime_Label", "Regime_Label", "Regime", "D1_Regime"])
            record["D1_Structure_Direction"] = _first_text(
                d1_row, ["D1_Structure_Direction", "Structure_Direction", "D1_Direction", "Direction"]
            )
        return record
    usage = frames.get("usage_scenarios", pd.DataFrame())
    if not usage.empty:
        row = usage.tail(1).iloc[0]
        return _from_row(
            row,
            config,
            "FALLBACK_REFERENCE_USAGE_SNAPSHOT",
            "REFERENCE_USAGE_SCENARIO_LATEST_ROW",
            "",
            "TIMESTAMP_UNAVAILABLE_LAST_ROW_USED",
        )
    return _base(config, "INPUT_MISSING", "INPUT_MISSING")


def _latest_row(frame: pd.DataFrame) -> tuple[pd.Series, str, str]:
    best_column = next((column for column in TIMESTAMP_ALIASES if column in frame.columns), None)
    if best_column is None:
        return frame.tail(1).iloc[0], "", "TIMESTAMP_UNAVAILABLE_LAST_ROW_USED"
    dated = frame.copy()
    dated["_snapshot_timestamp"] = pd.to_datetime(dated[best_column], errors="coerce", utc=True)
    dated = dated.sort_values("_snapshot_timestamp", na_position="first")
    row = dated.tail(1).iloc[0]
    timestamp = text_value(row.get(best_column, ""))
    return row.drop(labels=["_snapshot_timestamp"]), timestamp, "TIMESTAMP_AVAILABLE" if timestamp else "TIMESTAMP_MISSING"


def _from_row(
    row: pd.Series,
    config: CurrentMarketStateSnapshotResearchConfig,
    mode: str,
    source: str,
    timestamp: str,
    timestamp_status: str,
) -> dict[str, object]:
    record = _base(config, mode, source)
    record.update(
        {
            "Snapshot_Timestamp": timestamp,
            "Snapshot_Timestamp_Status": timestamp_status,
            "H4_Transition_Label": _first_text(
                row, ["H4_Transition_Label", "Transition_Label", "Transition", "Condition_Value", "Condition_Label"]
            ),
            "H4_Market_State": _first_text(row, ["H4_Market_State", "H4_State", "Market_State", "State"]),
            "D1_Market_State": _first_text(row, ["D1_Market_State", "D1_State", "D1_State_Label"]),
            "D1_Regime_Label": _first_text(row, ["D1_Regime_Label", "D1_Regime", "Regime_Label", "Regime"]),
            "D1_Structure_Direction": _first_text(
                row, ["D1_Structure_Direction", "D1_Direction", "Structure_Direction", "Direction"]
            ),
        }
    )
    if not record["H4_Transition_Label"]:
        record["H4_Transition_Label"] = _first_text(row, ["Query_H4_Transition_Label", "H4_Transition"])
    if not record["D1_Market_State"]:
        record["D1_Market_State"] = _first_text(row, ["Query_D1_Market_State"])
    if not record["D1_Regime_Label"]:
        record["D1_Regime_Label"] = _first_text(row, ["Query_D1_Regime_Label"])
    return record


def _first_text(row: pd.Series, aliases: list[str]) -> str:
    return text_value(row_value(row, aliases, ""))


def snapshot_requested_horizons(config: CurrentMarketStateSnapshotResearchConfig) -> list[int]:
    if config.snapshot_forward_horizon is not None:
        return [int_value(config.snapshot_forward_horizon)]
    return [int(item) for item in config.preferred_horizons]
