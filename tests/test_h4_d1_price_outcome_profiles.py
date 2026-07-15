import pandas as pd

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.loader import load_h4_d1_scenario_data
from sqre.h4_d1_structural_research.price_outcome_profiles import build_price_outcome_profiles


def test_price_outcome_profiles_aggregate_samples_and_metrics(tmp_path):
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    for scenario_id, sample_size, forward_range in [
        ("eurusd_h4_period_1", 4, 10.0),
        ("eurusd_h4_period_2", 6, 20.0),
    ]:
        research = output_dir / scenario_id / "research"
        research.mkdir(parents=True)
        pd.DataFrame(
            [
                {
                    "Condition_Type": "STATE_CONDITION",
                    "Condition_Value": "A",
                    "Forward_Window_Candles": 3,
                    "Sample_Size": sample_size,
                    "Average_Forward_Close_Return_Pips": 1.0,
                    "Median_Forward_Close_Return_Pips": 0.5,
                    "Average_Forward_Range_Pips": forward_range,
                    "Average_Max_Favorable_Displacement_Pips": 3.0,
                    "Average_Max_Adverse_Displacement_Pips": -2.0,
                    "Average_Outcome_Magnitude_Pips": 5.0,
                    "Direction_Alignment_Rate": 0.4,
                }
            ]
        ).to_csv(research / "condition_price_outcome_summary.csv", index=False)
    pd.DataFrame([_summary_row("eurusd_h4_period_1"), _summary_row("eurusd_h4_period_2")]).to_csv(summary, index=False)

    profiles = build_price_outcome_profiles(load_h4_d1_scenario_data(summary, output_dir), H4D1StructuralResearchConfig())
    profile = profiles[0]

    assert profile.total_sample_size == 10
    assert profile.average_sample_size_per_scenario == 5
    assert profile.average_forward_range_pips == 15
    assert profile.sample_adequacy_flag == "ADEQUATE"


def _summary_row(scenario_id):
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": "H4",
        "Status": "COMPLETED",
        "OHLC_Rows": 10,
        "Structures_Detected": 4,
        "States_Generated": 4,
        "Unique_States": 2,
        "Most_Common_State": "A",
        "Average_Forward_Range_Pips": 12,
        "Direction_Alignment_Rate": 0.4,
        "Low_Sample_Conditions_Research": 1,
        "Low_Sample_Conditions_Price_Outcome": 2,
    }
