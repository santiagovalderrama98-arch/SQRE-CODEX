import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.reference_panel_builder import build_reference_cards


def test_reference_panel_builder_creates_limited_reference_cards():
    frames = {
        "snapshot_reference_results": pd.DataFrame(
            [
                {"Snapshot_Query_ID": "Q1", "Matched_Research_Reference_ID": "R1", "Result_Rank": 2},
                {"Snapshot_Query_ID": "Q2", "Matched_Research_Reference_ID": "R2", "Result_Rank": 1},
            ]
        )
    }

    cards = build_reference_cards(frames, ResearchDashboardPrototypeConfig(maximum_reference_cards=1))

    assert len(cards) == 1
    assert cards.iloc[0]["Matched_Research_Reference_ID"] == "R2"


def test_reference_panel_builder_omits_unmatched_results():
    frames = {
        "snapshot_reference_results": pd.DataFrame(
            [
                {
                    "Snapshot_Query_ID": "Q1",
                    "Matched_Research_Reference_ID": "",
                    "Snapshot_Research_Result_Class": "NO_USABLE_SNAPSHOT_REFERENCE",
                }
            ]
        )
    }

    cards = build_reference_cards(frames, ResearchDashboardPrototypeConfig())

    assert cards.empty
