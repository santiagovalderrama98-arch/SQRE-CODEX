from pathlib import Path
import subprocess
import sys


def test_cli_runs_d1_regime_outcome_review(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    report_path = output_dir / "d1_regime_outcome_review_report.txt"
    _write_profiles(input_dir)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_d1_regime_outcome_review.py",
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "D1 regime outcome review completed" in result.stdout
    assert (output_dir / "d1_regime_outcome_review_summary.csv").exists()
    assert report_path.exists()


def _write_profiles(input_dir: Path) -> None:
    input_dir.mkdir()
    (input_dir / "d1_regime_normalized_condition_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Regime_Sensitivity_Flag",
                "STATE,EXPANSION,20,4,80,22.5,8.0,0.61,0.12,0.18,STABLE",
            ]
        ),
        encoding="utf-8",
    )
