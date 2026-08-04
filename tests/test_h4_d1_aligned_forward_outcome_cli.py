from __future__ import annotations

import subprocess
import sys

from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_cli_works_with_synthetic_temp_data(tmp_path):
    alignment_dir, synchronized_dir, contextual_dir = write_forward_outcome_inputs(tmp_path)
    output_dir = tmp_path / "out"
    command = [
        sys.executable,
        "scripts/run_h4_d1_aligned_forward_outcome_research.py",
        "--same-time-alignment-dir",
        str(alignment_dir),
        "--synchronized-data-dir",
        str(synchronized_dir),
        "--contextual-transition-dir",
        str(contextual_dir),
        "--output-dir",
        str(output_dir),
        "--report",
        str(output_dir / "report.txt"),
        "--forward-horizons",
        "1,3",
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True)

    assert "H4/D1 aligned forward outcome research completed" in completed.stdout
    assert (output_dir / "h4_d1_aligned_forward_outcome_research_summary.csv").exists()
