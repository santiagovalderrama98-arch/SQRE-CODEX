import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.reference_lookup_engine import build_reference_lookup_results
from sqre.research_reference_store_usage_review.usage_scenario_builder import SCENARIO_COLUMNS


def test_lookup_engine_finds_exact_match():
    scenarios = pd.DataFrame(
        [
            {
                "Usage_Scenario_ID": "USAGE_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
                "Scenario_Source": "HISTORICAL_ALIGNMENT_SCENARIO",
                "Scenario_Diagnostic": "",
            }
        ],
        columns=SCENARIO_COLUMNS,
    )
    reference_store = _reference_store()

    lookups = build_reference_lookup_results(scenarios, reference_store, ResearchReferenceStoreUsageReviewConfig())

    assert lookups.iloc[0]["Reference_Match_Level"] == "EXACT_D1_STATE_REGIME_CONTEXT_MATCH"
    assert lookups.iloc[0]["Matched_Research_Reference_ID"] == "REF_1"


def test_lookup_engine_falls_back_to_transition_only_match():
    scenarios = pd.DataFrame(
        [
            {
                "Usage_Scenario_ID": "USAGE_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "OTHER",
                "D1_Regime_Label": "OTHER",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
                "Scenario_Source": "HISTORICAL_ALIGNMENT_SCENARIO",
                "Scenario_Diagnostic": "",
            }
        ],
        columns=SCENARIO_COLUMNS,
    )

    lookups = build_reference_lookup_results(scenarios, _reference_store(), ResearchReferenceStoreUsageReviewConfig())

    assert lookups.iloc[0]["Reference_Match_Level"] == "H4_TRANSITION_ONLY_CONTEXT_MATCH"


def test_lookup_engine_handles_empty_reference_store():
    scenarios = pd.DataFrame(
        [
            {
                "Usage_Scenario_ID": "USAGE_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
                "Scenario_Source": "HISTORICAL_ALIGNMENT_SCENARIO",
                "Scenario_Diagnostic": "",
            }
        ],
        columns=SCENARIO_COLUMNS,
    )

    lookups = build_reference_lookup_results(scenarios, pd.DataFrame(), ResearchReferenceStoreUsageReviewConfig())

    assert lookups.iloc[0]["Reference_Match_Level"] == "NO_REFERENCE_MATCH"


def _reference_store():
    return pd.DataFrame(
        [
            {
                "Research_Reference_ID": "REF_1",
                "Outcome_Profile_ID": "OUT_1",
                "Context_Granularity": "D1_STATE_REGIME",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
                "Outcome_Sample_Size": 25,
                "Outcome_Dispersion_Pips": 30.0,
                "Directional_Behavior_Class": "MIXED",
                "Dominant_Observed_Direction": "UP",
                "Excursion_Behavior_Class": "BALANCED",
                "Horizon_Stability_Class": "STABLE",
                "Reference_Tier": "CORE_REFERENCE",
            }
        ]
    )
