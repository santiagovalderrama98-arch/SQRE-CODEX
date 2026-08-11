from __future__ import annotations

from sqre.dashboard_stability_indicators.behavior_panel_indicator_builder import build_behavior_stability_panel
from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader
from sqre.dashboard_stability_indicators.reference_card_indicator_builder import build_reference_card_indicators
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_behavior_stability_panel_is_generated_from_dashboard_inputs(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)
    frames = DashboardStabilityIndicatorsLoader(config).load_frames()
    cards = build_reference_card_indicators(config, frames["reference_cards"])

    panel = build_behavior_stability_panel(cards, frames["behavior_panel"])

    assert len(panel) == 1
    assert panel.iloc[0]["Observed_Direction_Class_Count"] >= 2
