from __future__ import annotations

from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader
from sqre.dashboard_stability_indicators.reference_card_indicator_builder import build_reference_card_indicators
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_reference_card_builder_flags_fallback_dependent_references(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()

    result = build_reference_card_indicators(config, frames["reference_cards"], frames["fallback_panel"])

    row = result[result["Reference_Card_ID"] == "CARD_002"].iloc[0]
    assert row["Reference_Card_Stability_Class"] == "REFERENCE_CARD_STABLE_FOR_REVIEW"
    assert "Fallback-dependent" in row["Primary_Stability_Warning"]


def test_reference_card_builder_flags_directionally_unstable_references(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()

    result = build_reference_card_indicators(config, frames["reference_cards"], frames["fallback_panel"])

    row = result[result["Reference_Card_ID"] == "CARD_003"].iloc[0]
    assert row["Dashboard_Stability_Severity_Class"] == "HIGH_STABILITY_WARNING"
    assert "Directionally unstable" in row["Primary_Stability_Warning"]


def test_reference_card_builder_keeps_directional_primary_and_fallback_secondary(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()

    result = build_reference_card_indicators(config, frames["reference_cards"], frames["fallback_panel"])

    row = result[result["Reference_Card_ID"] == "CARD_003"].iloc[0]
    assert row["Primary_Stability_Warning"] == "Directionally unstable reference evidence."
    assert row["Secondary_Stability_Warning"] == "Fallback-dependent broader context used."
