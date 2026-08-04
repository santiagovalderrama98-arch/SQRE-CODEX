import pandas as pd

from sqre.research_query_interface_design.query_result_quality_review import (
    build_query_evidence_quality_review,
    build_query_result_quality_review,
)


def test_quality_reviews_group_results():
    results = pd.DataFrame(
        [
            _row("RQ_1", "HIGH_QUALITY_RESEARCH_QUERY_RESULT", "CORE_RESEARCH_REFERENCE_EVIDENCE"),
            _row("RQ_2", "LOW_QUALITY_RESEARCH_QUERY_RESULT", "SUPPORTING_RESEARCH_REFERENCE_EVIDENCE"),
        ]
    )

    quality = build_query_result_quality_review(results)
    evidence = build_query_evidence_quality_review(results)

    assert set(quality["Research_Query_Result_Quality_Class"]) == {
        "HIGH_QUALITY_RESEARCH_QUERY_RESULT",
        "LOW_QUALITY_RESEARCH_QUERY_RESULT",
    }
    assert evidence["Query_Result_Count"].sum() == 2


def _row(query_id: str, quality: str, evidence: str) -> dict[str, object]:
    return {
        "Research_Query_ID": query_id,
        "Research_Query_Result_Quality_Class": quality,
        "Research_Query_Evidence_Class": evidence,
        "Matched_Reference_Tier": "CORE_REFERENCE",
        "Matched_Outcome_Sample_Size": 20,
        "Matched_Outcome_Dispersion_Pips": 10,
    }

