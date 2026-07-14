import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m15_introduction_review_cli_runs(tmp_path):
    input_path = tmp_path / "m15_summary.csv"
    output_path = tmp_path / "m15_review.csv"
    report_path = tmp_path / "m15_review.txt"
    input_path.write_text(
        "\n".join(
            [
                "Scenario_ID,Timeframe,Status,OHLC_Rows,Structures_Detected,Average_Structure_Duration,"
                "Unique_States,Most_Common_State,Average_Forward_Range_Pips,Direction_Alignment_Rate,"
                "Low_Sample_Conditions_Research,Low_Sample_Conditions_Price_Outcome",
                "eurusd_m15_period_1,M15,COMPLETED,100,10,7200,5,DIRECTIONAL_DRIFT,8,0.4,4,3",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_m15_introduction_review.py"),
            "--m15-summary-csv",
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
    assert "SQRE M15 introduction review started" in result.stdout
    assert "Scenarios reviewed: 1" in result.stdout
    assert output_path.exists()
    assert report_path.exists()
