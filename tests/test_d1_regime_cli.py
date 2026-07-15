import subprocess
import sys

import pandas as pd


def test_cli_runs_with_synthetic_data(tmp_path):
    config = tmp_path / "config.yaml"
    summary = tmp_path / "summary.csv"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "research"
    report = output_dir / "report.txt"
    config.write_text(
        """
research_name: test
symbol: EURUSD
timeframe: D1
scenarios:
  - scenario_id: eurusd_d1_period_1
    timeframe: D1
    regime_id: R1
    regime_label: one
""",
        encoding="utf-8",
    )
    pd.DataFrame([_summary_row()]).to_csv(summary, index=False)
    price_dir = validation_dir / "eurusd_d1_period_1" / "research"
    price_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "Condition_Type": "STATE_CONDITION",
                "Condition_Label": "A",
                "Forward_Window": 6,
                "Sample_Size": 5,
                "Average_Forward_Range_Pips": 30,
                "Average_Outcome_Magnitude_Pips": 10,
            }
        ]
    ).to_csv(price_dir / "condition_price_outcome_summary.csv", index=False)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_d1_regime_normalized_research.py",
            "--config",
            str(config),
            "--validation-summary",
            str(summary),
            "--validation-output-dir",
            str(validation_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "D1 regime-normalized research completed" in completed.stdout
    assert report.exists()


def _summary_row():
    return {
        "Scenario_ID": "eurusd_d1_period_1",
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
