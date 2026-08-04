import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_request_builder import build_query_requests


def test_single_query_request_is_user_supplied():
    config = ResearchQueryInterfaceDesignConfig(query_h4_transition_label="A_TO_B", query_forward_horizon=1)

    requests = build_query_requests(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), config)

    assert requests.iloc[0]["Research_Query_Mode"] == "SINGLE_RESEARCH_QUERY"
    assert requests.iloc[0]["Query_Source"] == "USER_SUPPLIED_QUERY"
    assert requests.iloc[0]["Query_Validation_Status"] == "VALID_RESEARCH_QUERY"


def test_batch_query_request_uses_usage_scenarios():
    usage = pd.DataFrame(
        [
            {
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
            }
        ]
    )

    requests = build_query_requests(usage, pd.DataFrame(), pd.DataFrame(), ResearchQueryInterfaceDesignConfig())

    assert requests.iloc[0]["Query_Source"] == "REFERENCE_USAGE_BATCH_QUERY"
    assert requests.iloc[0]["Research_Query_ID"] == "RQ_000001"

