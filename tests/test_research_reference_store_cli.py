import subprocess
import sys
from pathlib import Path

from tests.test_research_reference_store_pipeline import _write_synthetic_inputs


def test_cli_works_with_synthetic_temp_data(tmp_path: Path):
    interpretation_dir = tmp_path / "interpretation"
    forward_dir = tmp_path / "forward"
    output_dir = tmp_path / "output"
    _write_synthetic_inputs(interpretation_dir, forward_dir)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_research_reference_store_design.py",
            "--interpretation-dir",
            str(interpretation_dir),
            "--forward-outcome-dir",
            str(forward_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "research_reference_store_design_report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "Research reference store design completed" in completed.stdout
    assert (output_dir / "research_reference_store_design_summary.csv").exists()
