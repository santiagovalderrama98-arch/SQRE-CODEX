from pathlib import Path

import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.loader import ManualResearchDashboardReviewLoader


def test_loader_handles_missing_required_inputs_safely(tmp_path: Path):
    config = ManualResearchDashboardReviewConfig(dashboard_dir=tmp_path / "missing")
    loader = ManualResearchDashboardReviewLoader(config)

    assert loader.load_frames()["prototype_summary"].empty
    assert loader.load_texts()["prototype_html"] == ""


def test_loader_loads_dashboard_prototype_outputs(tmp_path: Path):
    dashboard_dir = tmp_path / "dashboard"
    dashboard_dir.mkdir()
    pd.DataFrame([{"Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT"}]).to_csv(
        dashboard_dir / "research_dashboard_summary.csv", index=False
    )
    (dashboard_dir / "research_dashboard_prototype.html").write_text("<html>Research-only</html>", encoding="utf-8")

    loader = ManualResearchDashboardReviewLoader(ManualResearchDashboardReviewConfig(dashboard_dir=dashboard_dir))

    assert len(loader.load_frames()["prototype_summary"]) == 1
    assert "Research-only" in loader.load_texts()["prototype_html"]
