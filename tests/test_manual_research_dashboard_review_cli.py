from pathlib import Path
from subprocess import run

import pandas as pd


def test_cli_runs_with_synthetic_temp_data(tmp_path: Path):
    dashboard_dir = tmp_path / "dashboard"
    dashboard_dir.mkdir()
    for filename in [
        "research_dashboard_source_inventory.csv",
        "research_dashboard_snapshot_panel.csv",
        "research_dashboard_reference_cards.csv",
        "research_dashboard_evidence_panel.csv",
        "research_dashboard_behavior_panel.csv",
        "research_dashboard_fallback_panel.csv",
        "research_dashboard_diagnostic_panel.csv",
        "research_dashboard_summary.csv",
    ]:
        pd.DataFrame([{"Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT", "Snapshot_Source": "LOCAL"}]).to_csv(
            dashboard_dir / filename, index=False
        )
    (dashboard_dir / "research_dashboard_prototype_report.txt").write_text(
        "This phase does not generate trading signals.", encoding="utf-8"
    )
    (dashboard_dir / "research_dashboard_prototype.html").write_text(
        "<html><body>Research-only Limitations</body></html>", encoding="utf-8"
    )
    output_dir = tmp_path / "out"

    result = run(
        [
            "python3",
            "scripts/run_manual_research_dashboard_review.py",
            "--dashboard-dir",
            str(dashboard_dir),
            "--snapshot-research-dir",
            str(tmp_path / "empty_snapshot"),
            "--query-interface-dir",
            str(tmp_path / "empty_query"),
            "--output-dir",
            str(output_dir),
            "--report",
            str(output_dir / "report.txt"),
            "--html",
            str(output_dir / "dashboard.html"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Manual research dashboard review completed" in result.stdout
