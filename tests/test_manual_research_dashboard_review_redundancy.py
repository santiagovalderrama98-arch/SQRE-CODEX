import pandas as pd

from sqre.manual_research_dashboard_review.redundancy_review import build_redundancy_review


def test_redundancy_review_flags_repeated_fields():
    frames = {
        "prototype_snapshot_panel": pd.DataFrame([{"Shared_Diagnostic": "a"}]),
        "prototype_reference_cards": pd.DataFrame([{"Shared_Diagnostic": "b"}]),
    }

    review = build_redundancy_review(frames)

    assert "DUPLICATIVE_DIAGNOSTIC_FIELD" in set(review["Potential_Redundancy_Class"])
