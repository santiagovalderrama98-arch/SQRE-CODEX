from __future__ import annotations

from sqre.dashboard_stability_indicators.dashboard_warning_builder import build_dashboard_warning_summary
from sqre.dashboard_stability_indicators.fallback_indicator_builder import build_fallback_stability_panel
from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader
from sqre.dashboard_stability_indicators.reference_card_indicator_builder import build_reference_card_indicators
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_warning_summary_counts_moderate_and_high_warnings(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()
    cards = build_reference_card_indicators(config, frames["reference_cards"], frames["fallback_panel"])
    fallback = build_fallback_stability_panel(config, frames["fallback_panel"])

    summary = build_dashboard_warning_summary(cards, fallback)

    assert "MODERATE_STABILITY_WARNING" in set(summary["Dashboard_Stability_Severity_Class"])
    assert "HIGH_STABILITY_WARNING" in set(summary["Dashboard_Stability_Severity_Class"])


def test_warning_summary_counts_fallback_dependent_queries_and_cards(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()
    cards = build_reference_card_indicators(config, frames["reference_cards"], frames["fallback_panel"])
    fallback = build_fallback_stability_panel(config, frames["fallback_panel"])

    summary = build_dashboard_warning_summary(cards, fallback)

    row = summary[summary["Dashboard_Warning_Class"] == "DASHBOARD_WARNING_FALLBACK_DEPENDENCY"].iloc[0]
    assert row["Affected_Reference_Card_Count"] == 2
    assert row["Affected_Query_Count"] == 2


def test_warning_summary_does_not_treat_successful_fallback_as_input_limited(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()
    cards = build_reference_card_indicators(config, frames["reference_cards"], frames["fallback_panel"])
    fallback = build_fallback_stability_panel(config, frames["fallback_panel"])

    summary = build_dashboard_warning_summary(cards, fallback)

    input_limited = summary[summary["Dashboard_Warning_Class"] == "DASHBOARD_WARNING_INPUT_LIMITED"]
    assert input_limited.iloc[0]["Affected_Query_Count"] == 1
