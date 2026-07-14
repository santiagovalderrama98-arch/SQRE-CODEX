import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_build_master_calibration_summary_cli_works_with_synthetic_csvs(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "master.csv"
    report = tmp_path / "report.txt"
    pd.DataFrame([_row("one", "M5"), _row("dup", "H1", structures=10)]).to_csv(first, index=False)
    pd.DataFrame([_row("dup", "H1", structures=20), _row("two", "H4")]).to_csv(second, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_master_calibration_summary.py",
            "--summary-csv",
            str(first),
            "--summary-csv",
            str(second),
            "--output",
            str(output),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "SQRE master historical calibration summary started" in result.stdout
    assert "Rows loaded: 4" in result.stdout
    assert "Rows retained: 3" in result.stdout
    assert "Duplicate Scenario_IDs: 1" in result.stdout
    assert output.exists()
    assert report.exists()
    frame = pd.read_csv(output)
    assert frame.loc[frame["Scenario_ID"] == "dup", "Structures_Detected"].iloc[0] == 20


def test_build_master_calibration_summary_cli_fails_for_missing_input(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_master_calibration_summary.py",
            "--summary-csv",
            str(tmp_path / "missing.csv"),
            "--output",
            str(tmp_path / "out.csv"),
            "--report",
            str(tmp_path / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Master historical calibration summary failed: Validation summary CSV not found" in result.stdout


def test_build_master_calibration_summary_cli_skips_missing_input_when_allowed(tmp_path: Path):
    first = tmp_path / "first.csv"
    output = tmp_path / "master.csv"
    report = tmp_path / "report.txt"
    pd.DataFrame([_row("one", "M5")]).to_csv(first, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_master_calibration_summary.py",
            "--summary-csv",
            str(first),
            "--summary-csv",
            str(tmp_path / "missing.csv"),
            "--output",
            str(output),
            "--report",
            str(report),
            "--allow-missing-inputs",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Input summaries missing: 1" in result.stdout
    assert "Rows retained: 1" in result.stdout


def _row(scenario_id: str, timeframe: str, *, structures: int = 10) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Status": "COMPLETED",
        "Symbol": "EURUSD",
        "Timeframe": timeframe,
        "OHLC_File": f"data/raw/{scenario_id}.csv",
        "Period_Start": "2026-01-01",
        "Period_End": "2026-01-31",
        "OHLC_Rows": 100,
        "Structures_Detected": structures,
        "Average_Structure_Duration": 3600,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 12.5,
        "Direction_Alignment_Rate": 0.55,
    }
