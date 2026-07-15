import pandas as pd

from sqre.d1_regime_normalized_research.d1_regime_normalized_research_pipeline import (
    run_d1_regime_normalized_research,
)


def test_pipeline_writes_all_expected_outputs(tmp_path):
    config = tmp_path / "config.yaml"
    summary = tmp_path / "summary.csv"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "research"
    report = output_dir / "report.txt"
    _write_config(config)
    _write_summary(summary)
    _write_price_summary(validation_dir / "eurusd_d1_period_1" / "research")
    _write_price_summary(validation_dir / "eurusd_d1_period_2" / "research")

    result = run_d1_regime_normalized_research(config, summary, validation_dir, output_dir, report)

    assert result.scenarios_loaded == 2
    assert result.regimes_loaded == 2
    assert (output_dir / "d1_regime_scenario_inventory.csv").exists()
    assert (output_dir / "d1_regime_condition_outcomes.csv").exists()
    assert (output_dir / "d1_regime_normalized_condition_profiles.csv").exists()
    assert (output_dir / "d1_regime_state_outcome_profiles.csv").exists()
    assert (output_dir / "d1_regime_transition_outcome_profiles.csv").exists()
    assert (output_dir / "d1_regime_research_summary.csv").exists()
    assert report.exists()


def _write_config(path):
    path.write_text(
        """
research_name: test
symbol: EURUSD
timeframe: D1
scenarios:
  - scenario_id: eurusd_d1_period_1
    timeframe: D1
    regime_id: R1
    regime_label: one
  - scenario_id: eurusd_d1_period_2
    timeframe: D1
    regime_id: R2
    regime_label: two
""",
        encoding="utf-8",
    )


def _write_summary(path):
    pd.DataFrame(
        [
            _summary_row("eurusd_d1_period_1"),
            _summary_row("eurusd_d1_period_2"),
        ]
    ).to_csv(path, index=False)


def _summary_row(scenario_id):
    return {
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


def _write_price_summary(path):
    path.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "Condition_Type": "STATE_CONDITION",
                "Condition_Label": "A",
                "Forward_Window": 6,
                "Sample_Size": 5,
                "Average_Forward_Close_Return_Pips": 1,
                "Median_Forward_Close_Return_Pips": 1,
                "Average_Forward_Range_Pips": 30,
                "Average_Outcome_Magnitude_Pips": 10,
                "Direction_Alignment_Rate": 0.5,
            }
        ]
    ).to_csv(path / "condition_price_outcome_summary.csv", index=False)
