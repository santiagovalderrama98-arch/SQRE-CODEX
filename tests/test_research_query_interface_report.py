from pathlib import Path

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.findings import build_summary
from sqre.research_query_interface_design.models import ResearchQueryInterfaceDesignResult
from sqre.research_query_interface_design.query_coverage_review import build_query_coverage_review
from sqre.research_query_interface_design.reports import build_report_text


def test_report_contains_scope_statements_without_forbidden_terms(tmp_path: Path):
    requests = pd.DataFrame([{"Research_Query_ID": "RQ_1", "Query_Validation_Status": "VALID_RESEARCH_QUERY"}])
    results = pd.DataFrame(
        [
            {
                "Research_Query_ID": "RQ_1",
                "Research_Query_Match_Level": "NO_RESEARCH_REFERENCE_QUERY_MATCH",
                "Research_Query_Result_Quality_Class": "NO_USABLE_RESEARCH_QUERY_RESULT",
                "Research_Query_Evidence_Class": "INSUFFICIENT_RESEARCH_REFERENCE_EVIDENCE",
                "Matched_Forward_Horizon_H4_Candles": 0,
            }
        ]
    )
    coverage = build_query_coverage_review(requests, results, ResearchQueryInterfaceDesignConfig())
    summary = build_summary(pd.DataFrame([{"Research_Reference_ID": "RRS_1"}]), requests, results, coverage, ResearchQueryInterfaceDesignConfig())
    result = ResearchQueryInterfaceDesignResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        query_requests=requests,
        query_results=results,
        coverage_review=coverage,
        summary=summary,
    )

    text = build_report_text(result)

    assert "This phase designs a research-only query interface." in text
    assert "This phase does not create a Decision Engine." in text

