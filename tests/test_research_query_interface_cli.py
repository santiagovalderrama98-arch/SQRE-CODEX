import subprocess
import sys
from pathlib import Path


def test_cli_runs_single_query_with_no_match(tmp_path: Path):
    reference_dir = tmp_path / "reference"
    usage_dir = tmp_path / "usage"
    output_dir = tmp_path / "output"
    reference_dir.mkdir()
    usage_dir.mkdir()
    (reference_dir / "research_reference_store.csv").write_text("Research_Reference_ID,H4_Transition_Label,Forward_Horizon_H4_Candles\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_research_query_interface_design.py",
            "--reference-store-dir",
            str(reference_dir),
            "--usage-review-dir",
            str(usage_dir),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "report.txt"),
            "--query-h4-transition-label",
            "A_TO_B",
            "--query-forward-horizon",
            "1",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Research query interface design completed" in completed.stdout
    assert (output_dir / "research_query_interface_design_summary.csv").exists()

