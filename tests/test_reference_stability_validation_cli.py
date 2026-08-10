from __future__ import annotations

import subprocess
import sys

from tests.test_reference_stability_validation_loader import write_synthetic_inputs


def test_reference_stability_validation_cli_works_with_synthetic_temp_data(tmp_path):
    config = write_synthetic_inputs(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_reference_stability_validation.py",
            "--reference-store-dir",
            str(config.reference_store_dir),
            "--query-interface-dir",
            str(config.query_interface_dir),
            "--snapshot-research-dir",
            str(config.snapshot_research_dir),
            "--dashboard-dir",
            str(config.dashboard_dir),
            "--manual-dashboard-review-dir",
            str(config.manual_dashboard_review_dir),
            "--output-dir",
            str(config.output_dir),
            "--report",
            str(config.report_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Reference stability validation completed" in result.stdout
