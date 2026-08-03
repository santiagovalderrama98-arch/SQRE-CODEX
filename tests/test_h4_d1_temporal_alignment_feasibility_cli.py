import subprocess
import sys
from pathlib import Path


def test_cli_runs_with_synthetic_temp_data(tmp_path: Path):
    h4_dir = tmp_path / "h4"
    d1_dir = tmp_path / "d1"
    output_dir = tmp_path / "out"
    h4_dir.mkdir()
    d1_dir.mkdir()
    (h4_dir / "h4_transition_state_context_interpretation_matrix.csv").write_text(
        "Context_ID,Source_State,Target_State,Transition_Label,Forward_Window\n"
        "CTX_1,EXPANSION,CONSOLIDATION,EXPANSION -> CONSOLIDATION,12\n",
        encoding="utf-8",
    )
    (d1_dir / "d1_condition_quality_inventory.csv").write_text(
        "Condition_Label,Forward_Window\nEXPANSION -> CONSOLIDATION,12\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_d1_temporal_alignment_feasibility_review.py",
            "--h4-combined-context-dir",
            str(h4_dir),
            "--h4-d1-structural-research-dir",
            str(tmp_path / "missing_structural"),
            "--h4-d1-validation-dir",
            str(tmp_path / "missing_validation"),
            "--d1-regime-normalized-dir",
            str(tmp_path / "missing_d1_normalized"),
            "--d1-regime-outcome-review-dir",
            str(d1_dir),
            "--d1-state-deep-dive-dir",
            str(tmp_path / "missing_d1_state"),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "H4/D1 temporal alignment feasibility review completed" in completed.stdout
    assert (output_dir / "h4_d1_temporal_alignment_feasibility_summary.csv").exists()
