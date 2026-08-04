import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_coverage_review import build_query_coverage_review


def test_coverage_review_counts_matched_queries():
    requests = pd.DataFrame(
        [
            {"Research_Query_ID": "RQ_1", "Query_Validation_Status": "VALID_RESEARCH_QUERY"},
            {"Research_Query_ID": "RQ_2", "Query_Validation_Status": "VALID_RESEARCH_QUERY"},
        ]
    )
    results = pd.DataFrame(
        [
            {"Research_Query_ID": "RQ_1", "Research_Query_Match_Level": "H4_TRANSITION_ONLY_QUERY_MATCH"},
            {"Research_Query_ID": "RQ_2", "Research_Query_Match_Level": "NO_RESEARCH_REFERENCE_QUERY_MATCH"},
        ]
    )

    review = build_query_coverage_review(requests, results, ResearchQueryInterfaceDesignConfig())

    assert review.iloc[0]["Query_With_Result_Count"] == 1
    assert review.iloc[0]["Research_Query_Coverage_Ratio"] == 0.5

