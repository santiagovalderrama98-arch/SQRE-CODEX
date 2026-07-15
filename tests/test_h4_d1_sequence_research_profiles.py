import pandas as pd

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.loader import load_h4_d1_scenario_data
from sqre.h4_d1_structural_research.sequence_profiles import build_sequence_research_profiles


def test_sequence_profiles_work_when_sequence_file_exists(tmp_path):
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    research = output_dir / "eurusd_d1_period_1" / "research"
    research.mkdir(parents=True)
    pd.DataFrame({"Sequence": ["A -> B", "A -> B"], "Count": [2, 3]}).to_csv(
        research / "sequence_outcomes.csv",
        index=False,
    )
    pd.DataFrame([_summary_row("eurusd_d1_period_1")]).to_csv(summary, index=False)

    profiles = build_sequence_research_profiles(
        load_h4_d1_scenario_data(summary, output_dir),
        H4D1StructuralResearchConfig(),
    )

    assert profiles[0].sequence_label == "A -> B"
    assert profiles[0].total_sequence_count == 5
    assert profiles[0].sequence_sample_adequacy_flag == "ADEQUATE"


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
