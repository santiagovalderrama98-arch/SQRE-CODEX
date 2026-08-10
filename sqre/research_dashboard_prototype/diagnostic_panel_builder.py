"""Diagnostic panel for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.dashboard_panel_builder import reindex


DIAGNOSTIC_PANEL_COLUMNS = [
    "Diagnostic_Category",
    "Diagnostic_Status",
    "Diagnostic_Count",
    "Diagnostic_Message",
    "Panel_Status",
]


def build_diagnostic_panel(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    diagnostics = frames.get("snapshot_diagnostic_review", pd.DataFrame())
    if diagnostics.empty:
        return reindex(pd.DataFrame(), DIAGNOSTIC_PANEL_COLUMNS)
    panel = diagnostics.copy()
    if "Diagnostic_Count" not in panel.columns:
        panel["Diagnostic_Count"] = 1
    panel["Panel_Status"] = "PANEL_READY"
    return reindex(panel, DIAGNOSTIC_PANEL_COLUMNS)
