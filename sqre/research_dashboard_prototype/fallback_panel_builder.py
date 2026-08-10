"""Fallback trace panel for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.dashboard_panel_builder import reindex


FALLBACK_PANEL_COLUMNS = [
    "Snapshot_Query_ID",
    "Fallback_Attempt_Order",
    "Attempted_Match_Level",
    "Attempted_H4_Transition_Label",
    "Attempted_D1_Market_State",
    "Attempted_D1_Regime_Label",
    "Attempted_Forward_Horizon_H4_Candles",
    "Candidate_Reference_Count",
    "Selected_Result_Count",
    "Fallback_Attempt_Status",
    "Fallback_Diagnostic",
    "Panel_Status",
]


def build_fallback_panel(frames: dict[str, pd.DataFrame], config: ResearchDashboardPrototypeConfig) -> pd.DataFrame:
    trace = frames.get("snapshot_fallback_trace", pd.DataFrame())
    if trace.empty:
        return reindex(pd.DataFrame(), FALLBACK_PANEL_COLUMNS)
    panel = trace.head(config.maximum_fallback_rows).copy()
    panel["Panel_Status"] = "PANEL_READY"
    return reindex(panel, FALLBACK_PANEL_COLUMNS)
