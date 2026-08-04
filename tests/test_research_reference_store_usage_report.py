import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.findings import build_summary
from sqre.research_reference_store_usage_review.models import ResearchReferenceStoreUsageReviewResult
from sqre.research_reference_store_usage_review.reports import build_report_text


def test_report_contains_scope_statements(tmp_path):
    summary = build_summary(
        pd.DataFrame(),
        pd.DataFrame([{"Scenario_Source": "INPUT_MISSING"}]),
        pd.DataFrame(),
        pd.DataFrame([{"Reference_Availability_Ratio": 0.0}]),
        pd.DataFrame(),
        pd.DataFrame(),
        ResearchReferenceStoreUsageReviewConfig(),
    )
    result = ResearchReferenceStoreUsageReviewResult(
        output_dir=tmp_path,
        report_path=tmp_path / "report.txt",
        summary=summary,
    )

    text = build_report_text(result)

    assert "SQRE Research Reference Store Usage Review" in text
    assert "This phase reviews how the research reference store can be queried by research workflows." in text
    assert "This phase does not create a Decision Engine." in text
