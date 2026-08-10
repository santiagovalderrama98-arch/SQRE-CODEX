import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.source_inventory import build_source_inventory


def test_source_inventory_reports_loaded_and_missing_files(tmp_path):
    snapshot_dir = tmp_path / "snapshot"
    snapshot_dir.mkdir()
    pd.DataFrame([{"Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT"}]).to_csv(
        snapshot_dir / "current_market_state_snapshot_context.csv", index=False
    )
    config = ResearchDashboardPrototypeConfig(snapshot_research_dir=snapshot_dir, query_interface_dir=tmp_path / "query")

    rows = build_source_inventory(config)
    statuses = {row.source_name: row.load_status for row in rows}

    assert statuses["snapshot_context"] == "LOADED"
    assert statuses["snapshot_reference_results"] == "REQUIRED_INPUT_MISSING"
    assert statuses["query_results"] == "OPTIONAL_INPUT_MISSING"
