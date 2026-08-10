import subprocess
import sys

from test_research_dashboard_prototype_loader import write_minimal_snapshot_inputs


def test_cli_works_with_synthetic_temp_data(tmp_path):
    snapshot_dir = tmp_path / "snapshot"
    out = tmp_path / "out"
    write_minimal_snapshot_inputs(snapshot_dir)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_research_dashboard_prototype.py",
            "--snapshot-research-dir",
            str(snapshot_dir),
            "--query-interface-dir",
            str(tmp_path / "query"),
            "--reference-store-dir",
            str(tmp_path / "reference"),
            "--output-dir",
            str(out),
            "--report",
            str(out / "research_dashboard_prototype_report.txt"),
            "--html",
            str(out / "research_dashboard_prototype.html"),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Research dashboard prototype completed" in completed.stdout
    assert (out / "research_dashboard_summary.csv").exists()
    assert (out / "research_dashboard_prototype.html").exists()
