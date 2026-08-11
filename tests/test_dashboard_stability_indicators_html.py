from __future__ import annotations

from sqre.dashboard_stability_indicators.dashboard_stability_indicators_pipeline import DashboardStabilityIndicatorsPipeline
from sqre.dashboard_stability_indicators.scope_safety_review import build_scope_safety_review, scope_safety_class
from tests.test_dashboard_stability_indicators_loader import write_synthetic_dashboard_stability_inputs


def test_html_renderer_writes_self_contained_html_with_required_sections(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    result = DashboardStabilityIndicatorsPipeline(config).run()
    html = result.html_path.read_text(encoding="utf-8")

    assert "<html" in html
    assert "Indicator Legend" in html
    assert "Stability-Aware Reference Cards" in html
    assert "Fallback Stability Panel" in html
    assert "http://" not in html and "https://" not in html


def test_html_excludes_forbidden_language_except_negative_scope_statements(tmp_path):
    config = write_synthetic_dashboard_stability_inputs(tmp_path)

    result = DashboardStabilityIndicatorsPipeline(config).run()
    review = build_scope_safety_review(True, {"html": result.html_path.read_text(encoding="utf-8")})

    assert scope_safety_class(review) == "DASHBOARD_STABILITY_SCOPE_SAFE"
