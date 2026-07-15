import pandas as pd

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.loader import load_h4_d1_scenario_data
from sqre.h4_d1_structural_research.transition_profiles import build_transition_research_profiles


def test_transition_profile_metrics_compute_counts_and_frequency(tmp_path):
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    for scenario_id, labels in {
        "eurusd_d1_period_1": ["A_TO_B", "A_TO_B"],
        "eurusd_d1_period_2": ["A_TO_B", "B_TO_A"],
    }.items():
        processed = output_dir / scenario_id / "processed"
        processed.mkdir(parents=True)
        pd.DataFrame({"Transition_Label": labels, "From_Market_State": ["A"] * 2, "To_Market_State": ["B"] * 2}).to_csv(
            processed / "state_transitions.csv",
            index=False,
        )
    pd.DataFrame([_summary_row("eurusd_d1_period_1"), _summary_row("eurusd_d1_period_2")]).to_csv(summary, index=False)

    profiles = build_transition_research_profiles(
        load_h4_d1_scenario_data(summary, output_dir),
        H4D1StructuralResearchConfig(),
    )
    profile = next(row for row in profiles if row.transition_label == "A_TO_B")

    assert profile.timeframe == "D1"
    assert profile.total_transition_count == 3
    assert profile.transition_frequency_ratio == 0.75
    assert profile.transition_sample_adequacy_flag == "LOW_SAMPLE"


def _summary_row(scenario_id):
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": "D1",
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
