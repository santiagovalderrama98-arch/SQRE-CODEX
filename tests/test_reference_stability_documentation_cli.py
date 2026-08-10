from __future__ import annotations

import subprocess
import sys

from tests.test_reference_stability_documentation_loader import write_synthetic_documentation_inputs


def test_reference_stability_documentation_cli_works_with_synthetic_temp_data(tmp_path):
    config = write_synthetic_documentation_inputs(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_reference_stability_documentation.py",
            "--stability-validation-dir",
            str(config.stability_validation_dir),
            "--dashboard-dir",
            str(config.dashboard_dir),
            "--manual-dashboard-review-dir",
            str(config.manual_dashboard_review_dir),
            "--output-dir",
            str(config.output_dir),
            "--report",
            str(config.report_path),
            "--markdown",
            str(config.markdown_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Reference stability documentation completed" in result.stdout
