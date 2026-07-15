from pathlib import Path
import subprocess
import sys


def test_cli_runs_with_synthetic_data(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    outcome_review_dir = tmp_path / "review"
    regime_research_dir = tmp_path / "regime"
    output_dir = tmp_path / "output"
    report_path = output_dir / "report.txt"
    _write_inputs(outcome_review_dir, regime_research_dir)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_d1_state_outcome_deep_dive.py",
            "--outcome-review-dir",
            str(outcome_review_dir),
            "--regime-research-dir",
            str(regime_research_dir),
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
    assert "D1 state outcome deep dive completed" in result.stdout
    assert "Research-ready state profiles selected: 1" in result.stdout
    assert (output_dir / "d1_state_deep_dive_summary.csv").exists()
    assert report_path.exists()


def _write_inputs(outcome_review_dir: Path, regime_research_dir: Path) -> None:
    outcome_review_dir.mkdir()
    regime_research_dir.mkdir()
    (outcome_review_dir / "d1_research_ready_condition_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Condition_Research_Class",
                "STATE_CONDITION,DIRECTIONAL_EXPANSION,3,2,70,15,6,0.6,0.1,0.1,RESEARCH_READY_DESCRIPTIVE",
            ]
        ),
        encoding="utf-8",
    )
    (regime_research_dir / "d1_regime_condition_outcomes.csv").write_text(
        "\n".join(
            [
                "Regime_ID,Regime_Label,Scenario_ID,Timeframe,Condition_Type,Condition_Label,Forward_Window,"
                "Sample_Size,Average_Forward_Close_Return_Pips,Median_Forward_Close_Return_Pips,"
                "Average_Forward_Range_Pips,Average_Favorable_Displacement_Pips,Average_Adverse_Displacement_Pips,"
                "Average_Outcome_Magnitude_Pips,Direction_Alignment_Rate,Sample_Adequacy_Flag",
                "R1,Regime 1,S1,D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,30,1,1,10,8,2,4,0.5,ADEQUATE",
                "R2,Regime 2,S2,D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,40,3,3,20,14,3,8,0.7,ADEQUATE",
            ]
        ),
        encoding="utf-8",
    )
