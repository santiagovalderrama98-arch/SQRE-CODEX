import pandas as pd

from sqre.current_market_state_snapshot_research.snapshot_diagnostic_review import build_snapshot_diagnostic_review


def test_diagnostic_review_reports_queries_without_results():
    context = pd.DataFrame([{"Snapshot_Validation_Status": "VALID_SNAPSHOT_CONTEXT", "Snapshot_Diagnostic": "ok"}])
    queries = pd.DataFrame([{"Snapshot_Query_ID": "Q1"}])
    results = pd.DataFrame(
        [{"Snapshot_Query_ID": "Q1", "Matched_Research_Reference_ID": "", "Snapshot_Query_Match_Level": "NO_MATCH"}]
    )

    review = build_snapshot_diagnostic_review(context, queries, results, pd.DataFrame([{"A": 1}]))

    assert set(review["Diagnostic_Category"]) == {"SNAPSHOT_CONTEXT", "SNAPSHOT_QUERY_COVERAGE", "FALLBACK_TRACE"}
    assert review.loc[review["Diagnostic_Category"] == "SNAPSHOT_QUERY_COVERAGE", "Diagnostic_Count"].iloc[0] == 1
