import pandas as pd

from sqre.research_dashboard_prototype.diagnostic_panel_builder import build_diagnostic_panel


def test_diagnostic_panel_builder_loads_diagnostic_review():
    frames = {
        "snapshot_diagnostic_review": pd.DataFrame(
            [{"Diagnostic_Category": "SNAPSHOT_CONTEXT", "Diagnostic_Status": "VALID", "Diagnostic_Message": "Loaded"}]
        )
    }

    panel = build_diagnostic_panel(frames)

    assert panel.iloc[0]["Diagnostic_Count"] == 1
    assert panel.iloc[0]["Panel_Status"] == "PANEL_READY"
