from __future__ import annotations

import subprocess
import sys

from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_dashboard_stability_indicators_cli_runs_with_synthetic_inputs(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_dashboard_stability_indicators.py",
            "--stability-documentation-dir",
            str(config.stability_documentation_dir),
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
            "--html",
            str(config.html_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Dashboard stability indicators completed" in completed.stdout
    assert config.html_path.exists()
