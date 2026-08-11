from __future__ import annotations

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.source_inventory import build_source_inventory
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_source_inventory_reports_loaded_files(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    rows = build_source_inventory(config)

    assert any(row.source_name == "interpretation_guide" and row.load_status == "LOADED" for row in rows)


def test_source_inventory_reports_missing_required_files(tmp_path):
    config = DashboardStabilityIndicatorsConfig(
        stability_documentation_dir=tmp_path / "missing_docs",
        stability_validation_dir=tmp_path / "missing_validation",
        dashboard_dir=tmp_path / "missing_dashboard",
        manual_dashboard_review_dir=tmp_path / "missing_manual",
    )

    rows = build_source_inventory(config)

    assert any(row.load_status == "REQUIRED_INPUT_MISSING" for row in rows)
