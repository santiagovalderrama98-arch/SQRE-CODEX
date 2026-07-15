import pandas as pd

from scripts.run_h4_d1_structural_research import main


def test_cli_runs_with_synthetic_data(tmp_path):
    summary = tmp_path / "summary.csv"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "research"
    report = output_dir / "report.txt"
    processed = validation_dir / "eurusd_h4_period_1" / "processed"
    processed.mkdir(parents=True)
    pd.DataFrame({"Market_State": ["A"], "State_Confidence": [0.8]}).to_csv(
        processed / "market_states.csv",
        index=False,
    )
    pd.DataFrame([_summary_row()]).to_csv(summary, index=False)

    code = main(
        [
            "--validation-summary",
            str(summary),
            "--validation-output-dir",
            str(validation_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report),
        ]
    )

    assert code == 0
    assert report.exists()


def _summary_row():
    return {
        "Scenario_ID": "eurusd_h4_period_1",
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
