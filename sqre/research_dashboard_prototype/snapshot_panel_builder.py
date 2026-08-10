"""Snapshot context panel for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.dashboard_panel_builder import first_value, panel_status, reindex


SNAPSHOT_PANEL_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Snapshot_Mode",
    "Snapshot_Source",
    "Snapshot_Timestamp",
    "Snapshot_Timestamp_Status",
    "Snapshot_Validation_Status",
    "H4_Transition_Label",
    "H4_Market_State",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Snapshot_Diagnostic",
    "Panel_Status",
]


def build_snapshot_panel(frames: dict[str, pd.DataFrame], config: ResearchDashboardPrototypeConfig) -> pd.DataFrame:
    context = frames.get("snapshot_context", pd.DataFrame())
    summary = frames.get("snapshot_research_summary", pd.DataFrame())
    missing = context.empty and summary.empty
    row = {
        "Symbol": first_value(summary, ["Symbol"], config.symbol),
        "H4_Timeframe": first_value(summary, ["H4_Timeframe"], config.h4_timeframe),
        "D1_Timeframe": first_value(summary, ["D1_Timeframe"], config.d1_timeframe),
        "Snapshot_Mode": first_value(context, ["Snapshot_Mode"], first_value(summary, ["Snapshot_Mode"], "INPUT_MISSING")),
        "Snapshot_Source": first_value(context, ["Snapshot_Source"], first_value(summary, ["Snapshot_Source"], "INPUT_MISSING")),
        "Snapshot_Timestamp": first_value(context, ["Snapshot_Timestamp"], first_value(summary, ["Snapshot_Timestamp"], "")),
        "Snapshot_Timestamp_Status": first_value(context, ["Snapshot_Timestamp_Status"], "INPUT_MISSING"),
        "Snapshot_Validation_Status": first_value(context, ["Snapshot_Validation_Status"], "INPUT_MISSING"),
        "H4_Transition_Label": first_value(context, ["H4_Transition_Label"], ""),
        "H4_Market_State": first_value(context, ["H4_Market_State"], ""),
        "D1_Market_State": first_value(context, ["D1_Market_State"], ""),
        "D1_Regime_Label": first_value(context, ["D1_Regime_Label"], ""),
        "D1_Structure_Direction": first_value(context, ["D1_Structure_Direction"], ""),
        "Snapshot_Diagnostic": "Snapshot context loaded." if not missing else "Snapshot context input is missing.",
        "Panel_Status": panel_status(context, missing_required=missing),
    }
    return reindex(pd.DataFrame([row]), SNAPSHOT_PANEL_COLUMNS)
