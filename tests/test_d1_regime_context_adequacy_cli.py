from __future__ import annotations

import subprocess
import sys

from tests.d1_regime_context_adequacy_test_utils import (
    write_contextual_transition_inputs,
    write_optional_supporting_inputs,
)


def test_cli_works_with_synthetic_temp_data(tmp_path):
    contextual_dir = tmp_path / "contextual"
    alignment_dir = tmp_path / "alignment"
    timestamped_dir = tmp_path / "timestamped"
    output_dir = tmp_path / "out"
    write_contextual_transition_inputs(contextual_dir)
    write_optional_supporting_inputs(alignment_dir, timestamped_dir)
    command = [
        sys.executable,
        "scripts/run_d1_regime_context_adequacy_review.py",
        "--contextual-transition-dir",
        str(contextual_dir),
        "--same-time-alignment-dir",
        str(alignment_dir),
        "--timestamped-state-regime-dir",
        str(timestamped_dir),
        "--output-dir",
        str(output_dir),
        "--report",
        str(output_dir / "report.txt"),
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True)

    assert "D1 regime context adequacy review completed" in completed.stdout
    assert "Context profiles: 5" in completed.stdout
    assert (output_dir / "d1_regime_context_adequacy_review_summary.csv").exists()
