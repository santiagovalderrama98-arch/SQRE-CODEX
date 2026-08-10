import pandas as pd

from sqre.research_dashboard_prototype.html_renderer import render_html
from sqre.research_dashboard_prototype.models import ResearchDashboardPrototypeResult, ResearchDashboardSummary


def test_html_renderer_creates_self_contained_html_with_required_sections(tmp_path):
    result = ResearchDashboardPrototypeResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        html_path=tmp_path / "dashboard.html",
        snapshot_panel=pd.DataFrame([{"Snapshot_Mode": "LATEST_AVAILABLE_SNAPSHOT"}]),
        evidence_panel=pd.DataFrame([{"Snapshot_Evidence_Class": "CORE"}]),
        reference_cards=pd.DataFrame([{"Reference_Card_ID": "REF_CARD_000001"}]),
        fallback_panel=pd.DataFrame([{"Snapshot_Query_ID": "Q1"}]),
        diagnostic_panel=pd.DataFrame([{"Diagnostic_Category": "SNAPSHOT_CONTEXT"}]),
        summary=_summary(),
    )

    html = render_html(result, "SQRE Research Dashboard Prototype")
    lowered = html.lower()

    assert "snapshot context" in lowered
    assert "evidence summary" in lowered
    assert "historical reference cards" in lowered
    assert "fallback trace" in lowered
    assert "diagnostics" in lowered
    assert "research-only" in lowered
    assert "not live market data" in lowered
    assert "http://" not in lowered
    assert "https://" not in lowered
    assert "<script" not in lowered
    assert "buy" not in lowered
    assert "sell" not in lowered


def _summary() -> ResearchDashboardSummary:
    return ResearchDashboardSummary(
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
        snapshot_mode="LATEST_AVAILABLE_SNAPSHOT",
        snapshot_source="SAME_TIME_ALIGNMENT_LATEST_ROW",
        research_reference_count=1,
        snapshot_query_count=1,
        snapshot_result_count=1,
        snapshot_reference_coverage_ratio=1.0,
        reference_card_count=1,
        evidence_panel_row_count=1,
        behavior_panel_row_count=1,
        fallback_panel_row_count=1,
        diagnostic_panel_row_count=1,
        primary_snapshot_query_match_level="D1_REGIME_CONTEXT_QUERY_MATCH",
        primary_snapshot_horizon="1",
        dashboard_readiness_class="RESEARCH_DASHBOARD_PROTOTYPE_READY",
        dashboard_readiness_flag="READY_FOR_MANUAL_RESEARCH_REVIEW",
        dashboard_diagnostic="Ready for manual dashboard review.",
        recommended_follow_up="Manual research dashboard review",
    )
