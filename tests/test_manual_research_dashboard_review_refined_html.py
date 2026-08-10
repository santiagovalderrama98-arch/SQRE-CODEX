import pandas as pd

from sqre.manual_research_dashboard_review.models import ManualResearchDashboardReviewResult
from sqre.manual_research_dashboard_review.refined_html_renderer import render_refined_html


def test_refined_html_renderer_creates_required_sections(tmp_path):
    result = ManualResearchDashboardReviewResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        html_path=tmp_path / "dashboard.html",
        frames={"prototype_snapshot_panel": pd.DataFrame([{"Snapshot_Source": "LOCAL"}])},
    )

    html = render_refined_html(result, "Dashboard")

    assert "<!doctype html>" in html
    assert "Research-Only Warning" in html
    assert "Historical Reference Cards" in html
    assert "Scope Statements" in html
