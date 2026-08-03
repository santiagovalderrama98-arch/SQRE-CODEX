from __future__ import annotations

import subprocess
import sys

from tests.h4_d1_same_time_contextual_transition_test_utils import write_transition_alignment


def test_cli_works_with_synthetic_temp_data(tmp_path):
    same_time_dir = tmp_path / "same_time"
    write_transition_alignment(same_time_dir)
    output_dir = tmp_path / "out"
    command = [
        sys.executable,
        "scripts/run_h4_d1_same_time_contextual_transition_review.py",
        "--same-time-alignment-dir",
        str(same_time_dir),
        "--timestamped-state-regime-dir",
        str(tmp_path / "optional"),
        "--output-dir",
        str(output_dir),
        "--report",
        str(output_dir / "report.txt"),
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True)

    assert "H4/D1 same-time contextual transition review completed" in completed.stdout
    assert (output_dir / "h4_d1_context_sample_adequacy_review.csv").exists()
