from pathlib import Path

import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.source_inventory import build_source_inventory


def test_source_inventory_reports_loaded_and_missing_files(tmp_path: Path):
    dashboard_dir = tmp_path / "dashboard"
    dashboard_dir.mkdir()
    pd.DataFrame([{"A": 1}]).to_csv(dashboard_dir / "research_dashboard_summary.csv", index=False)

    rows = build_source_inventory(ManualResearchDashboardReviewConfig(dashboard_dir=dashboard_dir))
    loaded = [row for row in rows if row.source_name == "prototype_summary"][0]
    missing = [row for row in rows if row.source_name == "prototype_snapshot_panel"][0]

    assert loaded.load_status == "LOADED"
    assert missing.load_status == "REQUIRED_INPUT_MISSING"
