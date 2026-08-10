import pandas as pd

from sqre.manual_research_dashboard_review.panel_completeness_review import build_panel_completeness_review


def test_panel_completeness_classifies_ready_and_missing_panels():
    frames = {
        "prototype_snapshot_panel": pd.DataFrame([{"Snapshot_Mode": "LATEST"}]),
        "prototype_reference_cards": pd.DataFrame(),
    }

    review = build_panel_completeness_review(frames, {"prototype_html": "<html></html>"})

    assert "PANEL_COMPLETE" in set(review["Panel_Completeness_Class"])
    assert "PANEL_EMPTY" in set(review["Panel_Completeness_Class"])
