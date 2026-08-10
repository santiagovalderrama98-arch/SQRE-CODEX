import pandas as pd

from sqre.research_dashboard_prototype.behavior_panel_builder import build_behavior_panel


def test_behavior_panel_builder_remains_descriptive_only():
    frames = {
        "snapshot_query_requests": pd.DataFrame([{"Snapshot_Query_ID": "Q1"}]),
        "snapshot_reference_results": pd.DataFrame(
            [{"Snapshot_Query_ID": "Q1", "Snapshot_Research_Result_Class": "HIGH_EVIDENCE_SNAPSHOT_REFERENCE"}]
        ),
        "snapshot_behavior_summary": pd.DataFrame(),
    }

    panel = build_behavior_panel(frames)
    text = " ".join(str(value).lower() for value in panel.iloc[0].to_dict().values())

    assert panel.iloc[0]["Snapshot_Query_Count"] == 1
    assert "buy" not in text
    assert "sell" not in text
