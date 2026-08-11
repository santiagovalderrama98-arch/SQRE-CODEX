from __future__ import annotations

from sqre.dashboard_stability_indicators.fallback_indicator_builder import build_fallback_stability_panel
from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_fallback_stability_panel_records_fallback_warnings(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    fallback = DashboardStabilityIndicatorsLoader(config).load_frames()["fallback_panel"]

    panel = build_fallback_stability_panel(config, fallback)

    q2 = panel[panel["Snapshot_Query_ID"] == "Q2"]
    assert set(q2["Dashboard_Warning_Class"]) == {"DASHBOARD_WARNING_FALLBACK_DEPENDENCY"}
    assert set(q2["Dashboard_Stability_Severity_Class"]) == {"MODERATE_STABILITY_WARNING"}


def test_fallback_stability_panel_keeps_exact_match_as_no_warning(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    fallback = DashboardStabilityIndicatorsLoader(config).load_frames()["fallback_panel"]

    panel = build_fallback_stability_panel(config, fallback)

    q1 = panel[panel["Snapshot_Query_ID"] == "Q1"]
    assert set(q1["Dashboard_Warning_Class"]) == {"DASHBOARD_WARNING_NONE"}
    assert set(q1["Dashboard_Stability_Severity_Class"]) == {"LOW_STABILITY_WARNING"}


def test_fallback_stability_panel_marks_no_usable_reference_as_input_limited(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    fallback = DashboardStabilityIndicatorsLoader(config).load_frames()["fallback_panel"]

    panel = build_fallback_stability_panel(config, fallback)

    q4 = panel[panel["Snapshot_Query_ID"] == "Q4"]
    assert set(q4["Dashboard_Warning_Class"]) == {"DASHBOARD_WARNING_INPUT_LIMITED"}
    assert set(q4["Dashboard_Stability_Severity_Class"]) == {"HIGH_STABILITY_WARNING"}
