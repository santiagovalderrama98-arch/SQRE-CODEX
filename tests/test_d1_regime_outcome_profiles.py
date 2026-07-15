import pandas as pd

from sqre.d1_regime_normalized_research.config import load_d1_regime_research_config
from sqre.d1_regime_normalized_research.loader import load_d1_regime_scenario_data
from sqre.d1_regime_normalized_research.outcome_profiles import (
    build_condition_outcomes,
    build_normalized_condition_profiles,
    state_condition_profiles,
    transition_condition_profiles,
)


def test_outcome_profiles_aggregate_across_regimes(tmp_path):
    config = load_d1_regime_research_config("configs/validation/d1_regime_normalized_research.yaml")
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    _write_summary(summary)
    _write_price_summary(output_dir / "eurusd_d1_period_1" / "research", "STATE_CONDITION", "A", 10, 30)
    _write_price_summary(output_dir / "eurusd_d1_period_2" / "research", "STATE_CONDITION", "A", 20, 90)
    _write_price_summary(output_dir / "eurusd_d1_period_3" / "research", "TRANSITION_CONDITION", "B", 10, 15)

    scenarios = load_d1_regime_scenario_data(summary, output_dir, config)
    outcomes = build_condition_outcomes(scenarios, config)
    profiles = build_normalized_condition_profiles(outcomes, config)

    state_profile = next(profile for profile in profiles if profile.condition_label == "A")
    assert len(outcomes) == 3
    assert state_profile.regime_count == 2
    assert state_profile.total_sample_size == 30
    assert state_profile.regime_coverage_flag == "SUFFICIENT"
    assert state_profile.regime_sensitivity_flag == "HIGH"
    assert len(state_condition_profiles(profiles)) == 1
    assert len(transition_condition_profiles(profiles)) == 1


def _write_summary(path):
    rows = []
    for scenario_id in ["eurusd_d1_period_1", "eurusd_d1_period_2", "eurusd_d1_period_3"]:
        rows.append(
            {
                "Scenario_ID": scenario_id,
                "Timeframe": "D1",
                "Status": "COMPLETED",
                "OHLC_Rows": 100,
                "Structures_Detected": 10,
                "States_Generated": 20,
                "Unique_States": 3,
                "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
                "Average_Forward_Range_Pips": 30,
                "Direction_Alignment_Rate": 0.5,
                "Low_Sample_Conditions_Research": 1,
                "Low_Sample_Conditions_Price_Outcome": 2,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_price_summary(path, condition_type, label, sample_size, range_pips):
    path.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "Condition_Type": condition_type,
                "Condition_Label": label,
                "Forward_Window": 6,
                "Sample_Size": sample_size,
                "Average_Forward_Close_Return_Pips": 1,
                "Median_Forward_Close_Return_Pips": 1,
                "Average_Forward_Range_Pips": range_pips,
                "Average_Favorable_Displacement_Pips": 2,
                "Average_Adverse_Displacement_Pips": 1,
                "Average_Outcome_Magnitude_Pips": range_pips / 2,
                "Direction_Alignment_Rate": 0.5,
            }
        ]
    ).to_csv(path / "condition_price_outcome_summary.csv", index=False)
