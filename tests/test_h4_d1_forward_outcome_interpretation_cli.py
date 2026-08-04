import subprocess
import sys

from tests.h4_d1_forward_outcome_interpretation_test_utils import write_contextual_inputs, write_phase_7515_inputs


def test_cli_runs_with_synthetic_temp_data(tmp_path):
    forward_dir = tmp_path / "forward"
    context_dir = tmp_path / "context"
    output_dir = tmp_path / "out"
    write_phase_7515_inputs(forward_dir)
    write_contextual_inputs(context_dir)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_h4_d1_forward_outcome_interpretation_review.py",
            "--forward-outcome-dir",
            str(forward_dir),
            "--contextual-transition-dir",
            str(context_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "H4/D1 forward outcome interpretation review completed" in result.stdout
    assert (output_dir / "h4_d1_forward_outcome_interpretation_review_summary.csv").exists()
