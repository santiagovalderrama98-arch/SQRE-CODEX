import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_request_builder import build_query_requests
from sqre.research_query_interface_design.research_query_engine import run_research_queries


def test_query_engine_returns_exact_match():
    config = ResearchQueryInterfaceDesignConfig(query_h4_transition_label="A_TO_B", query_d1_market_state="STATE", query_d1_regime_label="REGIME", query_forward_horizon=1)
    requests = build_query_requests(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), config)
    store = pd.DataFrame([_reference()])

    results, trace = run_research_queries(requests, store, config)

    assert results.iloc[0]["Research_Query_Match_Level"] == "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH"
    assert results.iloc[0]["Research_Query_Result_Quality_Class"] == "HIGH_QUALITY_RESEARCH_QUERY_RESULT"
    assert trace.iloc[0]["Fallback_Attempt_Status"] == "MATCH_FOUND"


def test_query_engine_falls_back_to_d1_regime_match():
    config = ResearchQueryInterfaceDesignConfig(query_h4_transition_label="A_TO_B", query_d1_market_state="OTHER", query_d1_regime_label="REGIME", query_forward_horizon=1)
    requests = build_query_requests(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), config)
    store = pd.DataFrame([{**_reference(), "D1_Market_State": "STATE"}])

    results, _ = run_research_queries(requests, store, config)

    assert results.iloc[0]["Research_Query_Match_Level"] == "D1_REGIME_CONTEXT_QUERY_MATCH"


def test_query_engine_falls_back_to_d1_market_state_match():
    config = ResearchQueryInterfaceDesignConfig(query_h4_transition_label="A_TO_B", query_d1_market_state="STATE", query_d1_regime_label="OTHER", query_forward_horizon=1)
    requests = build_query_requests(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), config)
    store = pd.DataFrame([{**_reference(), "D1_Regime_Label": "REGIME"}])

    results, _ = run_research_queries(requests, store, config)

    assert results.iloc[0]["Research_Query_Match_Level"] == "D1_MARKET_STATE_CONTEXT_QUERY_MATCH"


def test_query_engine_falls_back_to_broader_any_horizon_match():
    config = ResearchQueryInterfaceDesignConfig(query_h4_transition_label="A_TO_B", query_d1_market_state="OTHER", query_d1_regime_label="OTHER", query_forward_horizon=6)
    requests = build_query_requests(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), config)
    store = pd.DataFrame([{**_reference(), "Forward_Horizon_H4_Candles": 1}])

    results, _ = run_research_queries(requests, store, config)

    assert results.iloc[0]["Research_Query_Match_Level"] == "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH"
    assert results.iloc[0]["Matched_Forward_Horizon_H4_Candles"] == 1


def test_query_engine_marks_no_reference_match_safely():
    config = ResearchQueryInterfaceDesignConfig(query_h4_transition_label="UNKNOWN", query_forward_horizon=1)
    requests = build_query_requests(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), config)
    store = pd.DataFrame([_reference()])

    results, _ = run_research_queries(requests, store, config)

    assert results.iloc[0]["Research_Query_Match_Level"] == "NO_RESEARCH_REFERENCE_QUERY_MATCH"
    assert results.iloc[0]["Research_Query_Result_Quality_Class"] == "NO_USABLE_RESEARCH_QUERY_RESULT"


def _reference() -> dict[str, object]:
    return {
        "Research_Reference_ID": "RRS_1",
        "Outcome_Profile_ID": "OP_1",
        "Context_Granularity": "EXACT",
        "H4_Transition_Label": "A_TO_B",
        "D1_Market_State": "STATE",
        "D1_Regime_Label": "REGIME",
        "D1_Structure_Direction": "UP",
        "Forward_Horizon_H4_Candles": 1,
        "Outcome_Sample_Size": 30,
        "Outcome_Dispersion_Pips": 20,
        "Reference_Tier": "CORE_REFERENCE",
    }
