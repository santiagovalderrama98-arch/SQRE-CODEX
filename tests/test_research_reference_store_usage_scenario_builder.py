import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.usage_scenario_builder import build_usage_scenarios


def test_usage_scenarios_prefer_historical_alignment():
    alignment = pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
            }
        ]
    )
    config = ResearchReferenceStoreUsageReviewConfig(preferred_horizons=[1, 2])

    scenarios = build_usage_scenarios(alignment, pd.DataFrame(), config)

    assert len(scenarios) == 2
    assert set(scenarios["Scenario_Source"]) == {"HISTORICAL_ALIGNMENT_SCENARIO"}


def test_usage_scenarios_fallback_to_reference_store():
    reference_store = pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 6,
            }
        ]
    )

    scenarios = build_usage_scenarios(pd.DataFrame(), reference_store, ResearchReferenceStoreUsageReviewConfig())

    assert len(scenarios) == 1
    assert scenarios.iloc[0]["Scenario_Source"] == "REFERENCE_STORE_DERIVED_SCENARIO"


def test_usage_scenarios_input_missing_when_no_sources():
    scenarios = build_usage_scenarios(pd.DataFrame(), pd.DataFrame(), ResearchReferenceStoreUsageReviewConfig())

    assert scenarios.iloc[0]["Scenario_Source"] == "INPUT_MISSING"
