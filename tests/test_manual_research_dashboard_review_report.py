import pandas as pd

from sqre.manual_research_dashboard_review.models import ManualDashboardReviewSummary, ManualResearchDashboardReviewResult
from sqre.manual_research_dashboard_review.reports import build_report_text


def test_report_includes_required_sections(tmp_path):
    summary = ManualDashboardReviewSummary(
        "EURUSD",
        "H4",
        "D1",
        1,
        8,
        0,
        0,
        8,
        0,
        0,
        1,
        1,
        1,
        0,
        "SCOPE_SAFE",
        0,
        0,
        1,
        0,
        0,
        1,
        "MANUAL_RESEARCH_DASHBOARD_READY",
        "READY_FOR_REPEATED_MANUAL_RESEARCH_USE",
        "ok",
        "Dashboard documentation",
    )
    result = ManualResearchDashboardReviewResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        html_path=tmp_path / "dashboard.html",
        panel_completeness=pd.DataFrame([{"Panel_Completeness_Class": "PANEL_COMPLETE"}]),
        panel_readability=pd.DataFrame([{"Readability_Class": "HIGH_READABILITY"}]),
        field_usefulness=pd.DataFrame([{"Field_Usefulness_Class": "CORE_RESEARCH_FIELD"}]),
        redundancy_review=pd.DataFrame([{"Potential_Redundancy_Class": "NOT_REDUNDANT"}]),
        scope_safety=pd.DataFrame([{"Scope_Safety_Class": "SCOPE_SAFE"}]),
        refinement_recommendations=pd.DataFrame(
            [{"Recommendation_ID": "R1", "Recommendation_Priority": "LOW", "Recommendation_Category": "DOCUMENTATION_ONLY", "Recommendation_Text": "Document"}]
        ),
        summary=summary,
    )

    report = build_report_text(result)

    assert "SQRE Manual Research Dashboard Review" in report
    assert "Panel Completeness Review" in report
    assert "Scope Statements" in report
    assert "No Decision Engine was added." in report
