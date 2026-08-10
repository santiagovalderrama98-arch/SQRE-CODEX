import pandas as pd

from sqre.manual_research_dashboard_review.refinement_recommendations import build_refinement_recommendations


def test_recommendations_are_created_for_missing_or_low_readability_panels():
    completeness = pd.DataFrame(
        [{"Panel_Name": "Reference Cards", "Panel_Completeness_Class": "PANEL_EMPTY", "Completeness_Diagnostic": "empty"}]
    )
    readability = pd.DataFrame([{"Panel_Name": "Reference Cards", "Readability_Class": "LOW_READABILITY"}])

    recommendations = build_refinement_recommendations(completeness, readability, pd.DataFrame(), pd.DataFrame())

    assert len(recommendations) >= 1
    assert "HIGH" in set(recommendations["Recommendation_Priority"])
