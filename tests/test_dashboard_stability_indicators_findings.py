from __future__ import annotations

from sqre.dashboard_stability_indicators.dashboard_stability_indicators_pipeline import DashboardStabilityIndicatorsPipeline
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_findings_produce_partial_readiness_for_warning_annotated_cards(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    result = DashboardStabilityIndicatorsPipeline(config).run()

    assert result.summary is not None
    assert result.summary.dashboard_stability_readiness_flag == "PARTIAL_READY_FOR_STABILITY_AWARE_DASHBOARD_REVIEW"
    assert result.summary.warning_evidence_indicator_count >= 1
