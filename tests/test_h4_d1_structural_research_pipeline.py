import pandas as pd

from sqre.h4_d1_structural_research import run_h4_d1_structural_research


def test_pipeline_writes_expected_outputs(tmp_path):
    summary, validation_dir = _fixture(tmp_path)
    output_dir = tmp_path / "research"
    report = output_dir / "h4_d1_structural_research_report.txt"

    result = run_h4_d1_structural_research(
        validation_summary=summary,
        validation_output_dir=validation_dir,
        output_dir=output_dir,
        report_path=report,
    )

    assert result.scenarios_loaded == 2
    assert (output_dir / "h4_d1_scenario_inventory.csv").exists()
    assert (output_dir / "h4_d1_state_research_profiles.csv").exists()
    assert (output_dir / "h4_d1_transition_research_profiles.csv").exists()
    assert (output_dir / "h4_d1_price_outcome_profiles.csv").exists()
    assert (output_dir / "h4_d1_sequence_research_profiles.csv").exists()
    assert (output_dir / "h4_d1_timeframe_research_summary.csv").exists()
    assert report.exists()


def _fixture(tmp_path):
    summary = tmp_path / "summary.csv"
    validation_dir = tmp_path / "validation"
    rows = []
    for scenario_id, timeframe in [("eurusd_h4_period_1", "H4"), ("eurusd_d1_period_1", "D1")]:
        processed = validation_dir / scenario_id / "processed"
        research = validation_dir / scenario_id / "research"
        processed.mkdir(parents=True)
        research.mkdir(parents=True)
        pd.DataFrame({"Market_State": ["A", "A", "B"], "State_Confidence": [0.8, 0.7, 0.6]}).to_csv(
            processed / "market_states.csv",
            index=False,
        )
        pd.DataFrame({"Transition_Label": ["A_TO_B"], "From_Market_State": ["A"], "To_Market_State": ["B"]}).to_csv(
            processed / "state_transitions.csv",
            index=False,
        )
        pd.DataFrame(
            {
                "Condition_Type": ["STATE_CONDITION"],
                "Condition_Value": ["A"],
                "Forward_Window_Candles": [3],
                "Sample_Size": [6],
                "Average_Forward_Range_Pips": [12],
            }
        ).to_csv(research / "condition_price_outcome_summary.csv", index=False)
        pd.DataFrame({"Sequence": ["A -> B"], "Count": [5]}).to_csv(research / "sequence_outcomes.csv", index=False)
        rows.append(_summary_row(scenario_id, timeframe))
    pd.DataFrame(rows).to_csv(summary, index=False)
    return summary, validation_dir


def _summary_row(scenario_id, timeframe):
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
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
