from pathlib import Path

import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.manual_research_dashboard_review_pipeline import (
    ManualResearchDashboardReviewPipeline,
)


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    dashboard_dir = _write_dashboard_inputs(tmp_path)
    output_dir = tmp_path / "out"
    config = ManualResearchDashboardReviewConfig(
        dashboard_dir=dashboard_dir,
        snapshot_research_dir=tmp_path / "empty_snapshot",
        query_interface_dir=tmp_path / "empty_query",
        output_dir=output_dir,
        report_path=output_dir / "manual_research_dashboard_review_report.txt",
        html_path=output_dir / "manual_research_dashboard_refined.html",
    )

    result = ManualResearchDashboardReviewPipeline(config).run()

    assert result.summary is not None
    assert (output_dir / "manual_research_dashboard_review_summary.csv").exists()
    assert (output_dir / "manual_research_dashboard_panel_completeness_review.csv").exists()
    assert config.report_path.exists()
    assert config.html_path.exists()


def _write_dashboard_inputs(tmp_path: Path) -> Path:
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
    return dashboard_dir
