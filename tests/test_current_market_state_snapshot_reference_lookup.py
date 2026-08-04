import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.snapshot_reference_lookup import lookup_snapshot_references


def test_reference_lookup_exact_match_and_trace():
    results, trace = lookup_snapshot_references(_query("STATE", "REGIME", 1), pd.DataFrame([_reference()]), _config())

    assert results.iloc[0]["Snapshot_Query_Match_Level"] == "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH"
    assert results.iloc[0]["Snapshot_Research_Result_Class"] == "HIGH_EVIDENCE_SNAPSHOT_REFERENCE"
    assert trace.iloc[0]["Fallback_Attempt_Status"] == "MATCH_FOUND"


def test_reference_lookup_fallbacks_to_d1_regime():
    results, _ = lookup_snapshot_references(_query("OTHER", "REGIME", 1), pd.DataFrame([_reference()]), _config())

    assert results.iloc[0]["Snapshot_Query_Match_Level"] == "D1_REGIME_CONTEXT_QUERY_MATCH"


def test_reference_lookup_fallbacks_to_d1_market_state():
    results, _ = lookup_snapshot_references(_query("STATE", "OTHER", 1), pd.DataFrame([_reference()]), _config())

    assert results.iloc[0]["Snapshot_Query_Match_Level"] == "D1_MARKET_STATE_CONTEXT_QUERY_MATCH"


def test_reference_lookup_fallbacks_to_h4_and_any_horizon():
    results, _ = lookup_snapshot_references(_query("OTHER", "OTHER", 6), pd.DataFrame([_reference()]), _config())

    assert results.iloc[0]["Snapshot_Query_Match_Level"] == "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH"


def test_reference_lookup_no_match():
    query = _query("STATE", "REGIME", 1)
    query.loc[0, "H4_Transition_Label"] = "UNKNOWN"
    results, _ = lookup_snapshot_references(query, pd.DataFrame([_reference()]), _config())

    assert results.iloc[0]["Snapshot_Query_Match_Level"] == "NO_RESEARCH_REFERENCE_QUERY_MATCH"
    assert results.iloc[0]["Snapshot_Evidence_Class"] == "INSUFFICIENT_SNAPSHOT_REFERENCE_EVIDENCE"


def _config() -> CurrentMarketStateSnapshotResearchConfig:
    return CurrentMarketStateSnapshotResearchConfig(maximum_results_per_snapshot_query=5)


def _query(d1_state: str, d1_regime: str, horizon: int) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Snapshot_Query_ID": "CMSQ_1",
                "Snapshot_ID": "CMS_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": d1_state,
                "D1_Regime_Label": d1_regime,
                "D1_Structure_Direction": "UP",
                "Requested_Forward_Horizon_H4_Candles": horizon,
                "Snapshot_Query_Validation_Status": "VALID_SNAPSHOT_QUERY",
            }
        ]
    )


def _reference() -> dict[str, object]:
    return {
        "Research_Reference_ID": "RRS_1",
        "Outcome_Profile_ID": "OP_1",
        "Context_Granularity": "EXACT",
        "Reference_Tier": "CORE_REFERENCE",
        "H4_Transition_Label": "A_TO_B",
        "D1_Market_State": "STATE",
        "D1_Regime_Label": "REGIME",
        "D1_Structure_Direction": "UP",
        "Forward_Horizon_H4_Candles": 1,
        "Outcome_Sample_Size": 30,
        "Outcome_Dispersion_Pips": 20,
        "Mean_Forward_Close_Change_Pips": 1,
        "Median_Forward_Close_Change_Pips": 1,
        "Directional_Behavior_Class": "MIXED",
        "Dominant_Observed_Direction": "UP",
    }
