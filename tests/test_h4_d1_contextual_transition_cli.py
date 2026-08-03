import subprocess
import sys
from pathlib import Path


def test_cli_runs_with_synthetic_data(tmp_path: Path):
    h4_dir = tmp_path / "h4"
    d1_dir = tmp_path / "d1"
    h4_dir.mkdir()
    d1_dir.mkdir()
    (h4_dir / "h4_transition_state_context_interpretation_matrix.csv").write_text(
        "Context_ID,Scenario_ID,Transition_Label,Combined_Dispersion_Class,Combined_Sensitivity_Class\n"
        "CTX_1,eurusd_h4_period_1,A -> B,COMBINED_HIGH_DISPERSION,COMBINED_SCENARIO_SENSITIVE\n",
        encoding="utf-8",
    )
    (d1_dir / "d1_regime_outcome_review_summary.csv").write_text(
        "Scenario_ID,D1_Regime_Label,Outcome_Dispersion_Class,Sample_Adequacy_Class\n"
        "eurusd_h4_period_1,TREND_REGIME,HIGH_DISPERSION,SAMPLE_ADEQUATE\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "out"
    report = output_dir / "report.txt"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_d1_contextual_transition_review.py",
            "--h4-combined-context-dir",
            str(h4_dir),
            "--d1-regime-outcome-review-dir",
            str(d1_dir),
            "--d1-regime-normalized-dir",
            str(tmp_path / "missing_regime"),
            "--d1-state-deep-dive-dir",
            str(tmp_path / "missing_state"),
            "--h4-d1-structural-research-dir",
            str(tmp_path / "missing_structural"),
            "--h4-d1-validation-dir",
            str(tmp_path / "missing_validation"),
            "--partial-complement-dir",
            str(tmp_path / "missing_partial"),
            "--partial-validation-dir",
            str(tmp_path / "missing_partial_validation"),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "H4/D1 contextual transition review completed" in result.stdout
    assert report.exists()
