from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.research_dashboard_prototype_pipeline import ResearchDashboardPrototypePipeline
from sqre.research_dashboard_prototype.reports import build_report_text

from test_research_dashboard_prototype_loader import write_minimal_snapshot_inputs


def test_report_includes_required_sections_and_excludes_forbidden_operational_language(tmp_path):
    snapshot_dir = tmp_path / "snapshot"
    write_minimal_snapshot_inputs(snapshot_dir)
    result = ResearchDashboardPrototypePipeline(
        ResearchDashboardPrototypeConfig(
            snapshot_research_dir=snapshot_dir,
            query_interface_dir=tmp_path / "query",
            reference_store_dir=tmp_path / "reference",
            output_dir=tmp_path / "out",
            report_path=tmp_path / "out" / "report.txt",
            html_path=tmp_path / "out" / "dashboard.html",
        )
    ).run()

    text = build_report_text(result)
    lowered = text.lower()

    assert "SQRE Research Dashboard Prototype" in text
    assert "Dashboard Snapshot Panel" in text
    assert "Readiness Assessment" in text
    assert "HTML Output" in text
    assert "does not create a Decision Engine" in text
    assert "buy" not in lowered
    assert "sell" not in lowered
    assert "trade signal" not in lowered
    assert "take profit" not in lowered
    assert "stop loss" not in lowered
