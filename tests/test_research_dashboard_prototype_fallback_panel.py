import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.fallback_panel_builder import build_fallback_panel


def test_fallback_panel_builder_limits_rows():
    frames = {"snapshot_fallback_trace": pd.DataFrame([{"Snapshot_Query_ID": f"Q{i}"} for i in range(5)])}

    panel = build_fallback_panel(frames, ResearchDashboardPrototypeConfig(maximum_fallback_rows=2))

    assert len(panel) == 2
    assert set(panel["Panel_Status"]) == {"PANEL_READY"}
