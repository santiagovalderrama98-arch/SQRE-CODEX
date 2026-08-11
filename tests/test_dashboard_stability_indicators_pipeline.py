from __future__ import annotations

from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs
from sqre.dashboard_stability_indicators.dashboard_stability_indicators_pipeline import DashboardStabilityIndicatorsPipeline


def test_pipeline_writes_all_expected_outputs(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    DashboardStabilityIndicatorsPipeline(config).run()

    expected = [
        "dashboard_stability_indicator_source_inventory.csv",
        "dashboard_stability_indicator_legend.csv",
        "dashboard_stability_indicator_map.csv",
        "dashboard_reference_card_stability_indicators.csv",
        "dashboard_evidence_stability_panel.csv",
        "dashboard_behavior_stability_panel.csv",
        "dashboard_fallback_stability_panel.csv",
        "dashboard_stability_warning_summary.csv",
        "dashboard_stability_scope_safety_review.csv",
        "dashboard_stability_indicators_summary.csv",
        "dashboard_stability_indicators_report.txt",
        "dashboard_stability_indicators.html",
    ]
    for filename in expected:
        assert (config.output_dir / filename).exists()
