import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.snapshot_panel_builder import build_snapshot_panel


def test_snapshot_panel_builder_creates_panel_from_context():
    frames = {
        "snapshot_context": pd.DataFrame(
            [
                {
                    "Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT",
                    "Snapshot_Source": "SAME_TIME_ALIGNMENT_LATEST_ROW",
                    "Snapshot_Validation_Status": "VALID_SNAPSHOT_CONTEXT",
                    "H4_Market_State": "EXPANSION",
                }
            ]
        ),
        "snapshot_research_summary": pd.DataFrame([{"Symbol": "EURUSD"}]),
    }

    panel = build_snapshot_panel(frames, ResearchDashboardPrototypeConfig())

    assert panel.iloc[0]["Snapshot_Mode"] == "LATEST_AVAILABLE_SNAPSHOT"
    assert panel.iloc[0]["Panel_Status"] == "PANEL_READY"
