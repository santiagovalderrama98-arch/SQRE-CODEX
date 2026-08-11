from __future__ import annotations

from sqre.dashboard_stability_indicators.dashboard_stability_indicators_pipeline import DashboardStabilityIndicatorsPipeline
from sqre.dashboard_stability_indicators.scope_safety_review import build_scope_safety_review, scope_safety_class
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_report_includes_all_required_sections_and_safe_scope(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    result = DashboardStabilityIndicatorsPipeline(config).run()
    report = result.report_path.read_text(encoding="utf-8")

    for section in [
        "Generated At",
        "Input Directories",
        "Output Directory",
        "Source Inventory",
        "Stability Indicator Legend",
        "Stability Indicator Map",
        "Reference Card Stability Indicators",
        "Evidence Stability Panel",
        "Behavior Stability Panel",
        "Fallback Stability Panel",
        "Warning Summary",
        "Scope Safety Review",
        "Readiness Assessment",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
        "Scope Statements",
        "HTML Output",
    ]:
        assert section in report
    assert scope_safety_class(build_scope_safety_review(True, {"report": report})) == "DASHBOARD_STABILITY_SCOPE_SAFE"
