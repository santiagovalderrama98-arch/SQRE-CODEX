import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m15_duration_calibration_review_cli_runs_with_synthetic_csv(tmp_path):
    input_path = tmp_path / "experiment_summary.csv"
    output_path = tmp_path / "review.csv"
    report_path = tmp_path / "review.txt"
    input_path.write_text(
        "\n".join(
            [
                "Scenario_ID,Timeframe,Experiment_Profile,Status,Max_Structure_Duration_Seconds,"
                "Structures_Detected,Average_Structure_Duration,Unique_States,Most_Common_State,"
                "Average_Forward_Range_Pips,Direction_Alignment_Rate,Low_Sample_Conditions_Research,"
                "Low_Sample_Conditions_Price_Outcome",
                "eurusd_m15_period_1,M15,m15_duration_8h_baseline,COMPLETED,28800,20,24000,7,"
                "DIRECTIONAL_DRIFT,8,0.4,50,20",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_m15_duration_calibration_review.py"),
            "--experiment-summary",
            str(input_path),
            "--output",
            str(output_path),
            "--report",
            str(report_path),
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "SQRE M15 duration calibration review started" in result.stdout
    assert "Profiles reviewed: 1" in result.stdout
    assert output_path.exists()
    assert report_path.exists()
