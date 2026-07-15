import pandas as pd

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.loader import load_h4_d1_scenario_data
from sqre.h4_d1_structural_research.state_profiles import build_state_research_profiles


def test_state_profile_metrics_compute_counts_and_frequency(tmp_path):
    summary, output_dir = _fixture(tmp_path)

    profiles = build_state_research_profiles(load_h4_d1_scenario_data(summary, output_dir), H4D1StructuralResearchConfig())
    profile = next(row for row in profiles if row.market_state == "DIRECTIONAL_DRIFT")

    assert profile.timeframe == "H4"
    assert profile.total_state_count == 3
    assert profile.scenario_count == 2
    assert profile.state_frequency_ratio == 0.75
    assert round(profile.average_state_confidence, 4) == 0.7333
    assert profile.state_sample_adequacy_flag == "LOW_SAMPLE"


def _fixture(tmp_path):
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    for scenario_id, states in {
        "eurusd_h4_period_1": ["DIRECTIONAL_DRIFT", "DIRECTIONAL_DRIFT"],
        "eurusd_h4_period_2": ["DIRECTIONAL_DRIFT", "VOLATILE_ROTATION"],
    }.items():
        processed = output_dir / scenario_id / "processed"
        processed.mkdir(parents=True)
        pd.DataFrame({"Market_State": states, "State_Confidence": [0.8, 0.6]}).to_csv(
            processed / "market_states.csv",
            index=False,
        )
    pd.DataFrame(
        [
            _summary_row("eurusd_h4_period_1"),
            _summary_row("eurusd_h4_period_2"),
        ]
    ).to_csv(summary, index=False)
    return summary, output_dir


def _summary_row(scenario_id):
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": "H4",
        "Status": "COMPLETED",
        "OHLC_Rows": 10,
        "Structures_Detected": 4,
        "States_Generated": 4,
        "Unique_States": 2,
        "Most_Common_State": "DIRECTIONAL_DRIFT",
        "Average_Forward_Range_Pips": 12,
        "Direction_Alignment_Rate": 0.4,
        "Low_Sample_Conditions_Research": 1,
        "Low_Sample_Conditions_Price_Outcome": 2,
    }
