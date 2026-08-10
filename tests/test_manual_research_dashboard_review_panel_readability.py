import pandas as pd

from sqre.manual_research_dashboard_review.panel_readability_review import build_panel_readability_review


def test_panel_readability_identifies_empty_and_overloaded_panels():
    frames = {
        "prototype_snapshot_panel": pd.DataFrame([{f"Field_{i}": i for i in range(30)}]),
        "prototype_reference_cards": pd.DataFrame(),
    }

    review = build_panel_readability_review(frames, {"prototype_html": ""})

    assert "LOW_READABILITY" in set(review["Readability_Class"])
    assert "INPUT_MISSING" in set(review["Readability_Class"])
