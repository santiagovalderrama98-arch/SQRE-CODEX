import pandas as pd

from sqre.research_query_interface_design.query_validation import validate_query_request


def test_validation_requires_h4_transition_label():
    status, diagnostic = validate_query_request(pd.Series({"Research_Query_Mode": "SINGLE_RESEARCH_QUERY", "H4_Transition_Label": ""}))

    assert status == "INVALID_RESEARCH_QUERY"
    assert "H4_Transition_Label" in diagnostic


def test_validation_marks_missing_horizon_partial():
    status, _ = validate_query_request(
        pd.Series({"Research_Query_Mode": "SINGLE_RESEARCH_QUERY", "H4_Transition_Label": "A_TO_B", "Requested_Forward_Horizon_H4_Candles": 0})
    )

    assert status == "PARTIAL_RESEARCH_QUERY"

