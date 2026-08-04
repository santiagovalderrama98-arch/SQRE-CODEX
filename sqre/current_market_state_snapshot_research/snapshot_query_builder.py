"""Build snapshot query requests."""

from __future__ import annotations

import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.snapshot_context_builder import snapshot_requested_horizons
from sqre.research_reference_store_usage_review.reference_query_builder import text_value


SNAPSHOT_QUERY_COLUMNS = [
    "Snapshot_Query_ID",
    "Snapshot_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Requested_Forward_Horizon_H4_Candles",
    "Snapshot_Query_Source",
    "Snapshot_Query_Validation_Status",
    "Snapshot_Query_Diagnostic",
]


def build_snapshot_query_requests(
    snapshot_context: pd.DataFrame, config: CurrentMarketStateSnapshotResearchConfig
) -> pd.DataFrame:
    if snapshot_context.empty:
        return pd.DataFrame(columns=SNAPSHOT_QUERY_COLUMNS)
    context = snapshot_context.iloc[0]
    rows = []
    for index, horizon in enumerate(snapshot_requested_horizons(config), start=1):
        status, diagnostic = _validate_query(context, horizon)
        rows.append(
            {
                "Snapshot_Query_ID": f"CMSQ_{index:06d}",
                "Snapshot_ID": text_value(context.get("Snapshot_ID", "")),
                "Symbol": text_value(context.get("Symbol", config.symbol)),
                "H4_Timeframe": text_value(context.get("H4_Timeframe", config.h4_timeframe)),
                "D1_Timeframe": text_value(context.get("D1_Timeframe", config.d1_timeframe)),
                "H4_Transition_Label": text_value(context.get("H4_Transition_Label", "")),
                "D1_Market_State": text_value(context.get("D1_Market_State", "")),
                "D1_Regime_Label": text_value(context.get("D1_Regime_Label", "")),
                "D1_Structure_Direction": text_value(context.get("D1_Structure_Direction", "")),
                "Requested_Forward_Horizon_H4_Candles": int(horizon),
                "Snapshot_Query_Source": text_value(context.get("Snapshot_Source", "")),
                "Snapshot_Query_Validation_Status": status,
                "Snapshot_Query_Diagnostic": diagnostic,
            }
        )
    return pd.DataFrame(rows, columns=SNAPSHOT_QUERY_COLUMNS)


def _validate_query(context: pd.Series, horizon: int) -> tuple[str, str]:
    snapshot_status = text_value(context.get("Snapshot_Validation_Status", ""))
    if snapshot_status == "INPUT_MISSING":
        return "INPUT_MISSING", "Snapshot inputs are missing."
    if snapshot_status == "INVALID_SNAPSHOT_CONTEXT":
        return "INVALID_SNAPSHOT_QUERY", "Snapshot context is invalid."
    if not text_value(context.get("H4_Transition_Label", "")):
        return "INVALID_SNAPSHOT_QUERY", "H4 transition label is required."
    if horizon <= 0:
        return "INVALID_SNAPSHOT_QUERY", "Forward horizon must be positive."
    return "VALID_SNAPSHOT_QUERY", "Snapshot query is valid for descriptive reference lookup."
