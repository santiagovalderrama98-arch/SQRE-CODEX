import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.models import ReviewSourceInventoryRow
from sqre.manual_research_dashboard_review.usability_findings import build_summary


def test_findings_produce_ready_flag_for_complete_safe_dashboard():
    inventory = [
        ReviewSourceInventoryRow("a", "REQUIRED_DASHBOARD_SOURCE", "a.csv", True, "LOADED", 1, "ok")
    ]
    completeness = pd.DataFrame([{"Panel_Completeness_Class": "PANEL_COMPLETE"}] * 8)
    readability = pd.DataFrame([{"Readability_Class": "HIGH_READABILITY"}] * 8)
    fields = pd.DataFrame([{"Field_Usefulness_Class": "CORE_RESEARCH_FIELD"}])
    redundancy = pd.DataFrame([{"Potential_Redundancy_Class": "NOT_REDUNDANT"}])
    scope = pd.DataFrame([{"Scope_Safety_Class": "SCOPE_SAFE"}])
    recos = pd.DataFrame([{"Recommendation_Priority": "LOW"}])

    summary = build_summary(
        ManualResearchDashboardReviewConfig(),
        inventory,
        completeness,
        readability,
        fields,
        redundancy,
        scope,
        recos,
    )

    assert summary.dashboard_usability_readiness_flag == "READY_FOR_REPEATED_MANUAL_RESEARCH_USE"
