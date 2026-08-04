import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_fallback_engine import find_research_reference_matches


def test_fallback_skips_missing_d1_context_and_matches_h4_only():
    query = pd.Series(
        {
            "Research_Query_ID": "RQ_1",
            "Query_Validation_Status": "VALID_RESEARCH_QUERY",
            "H4_Transition_Label": "A_TO_B",
            "D1_Market_State": "",
            "D1_Regime_Label": "",
            "Requested_Forward_Horizon_H4_Candles": 1,
        }
    )
    store = pd.DataFrame(
        [{"H4_Transition_Label": "A_TO_B", "Forward_Horizon_H4_Candles": 1, "Research_Reference_ID": "RRS_1"}]
    )

    matches, traces, level = find_research_reference_matches(query, store, ResearchQueryInterfaceDesignConfig())

    assert len(matches) == 1
    assert level == "H4_TRANSITION_ONLY_QUERY_MATCH"
    assert traces[0]["Fallback_Attempt_Status"] == "SKIPPED_INSUFFICIENT_QUERY_FIELDS"

