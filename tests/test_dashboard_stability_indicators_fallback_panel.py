from __future__ import annotations

from sqre.dashboard_stability_indicators.fallback_indicator_builder import build_fallback_stability_panel
from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_fallback_stability_panel_records_fallback_warnings(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    fallback = DashboardStabilityIndicatorsLoader(config).load_frames()["fallback_panel"]

    panel = build_fallback_stability_panel(config, fallback)

    assert panel.iloc[0]["Dashboard_Warning_Class"] == "DASHBOARD_WARNING_FALLBACK_DEPENDENCY"
    assert panel.iloc[0]["Dashboard_Stability_Severity_Class"] == "MODERATE_STABILITY_WARNING"
