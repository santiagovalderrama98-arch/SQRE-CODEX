import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.findings import build_summary
from sqre.research_reference_store_design.models import ResearchReferenceStoreDesignResult
from sqre.research_reference_store_design.reports import FORBIDDEN_REPORT_TERMS, build_report_text


def test_report_includes_required_sections_and_scope_statements(tmp_path):
    candidates = pd.DataFrame([{"Reference_Tier": "CORE_RESEARCH_REFERENCE"}])
    store = pd.DataFrame([{"Research_Reference_ID": "RRS_1"}])
    granularity = pd.DataFrame(
        [{"Context_Granularity": "H4_TRANSITION_ONLY", "Granularity_Reference_Utility_Class": "PRIMARY_REFERENCE_GRANULARITY"}]
    )
    horizon = pd.DataFrame(
        [{"Forward_Horizon_H4_Candles": 3, "Horizon_Reference_Utility_Class": "PRIMARY_REFERENCE_HORIZON"}]
    )
    summary = build_summary(candidates, store, pd.DataFrame(), granularity, horizon, ResearchReferenceStoreDesignConfig())
    result = ResearchReferenceStoreDesignResult(
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
        candidates=candidates,
        reference_store=store,
        granularity_review=granularity,
        horizon_review=horizon,
        summary=summary,
    )

    text = build_report_text(result)

    for section in [
        "Generated At",
        "Input Directories",
        "Source Inventory",
        "Research Reference Store",
        "Readiness Assessment",
        "Scope Statements",
    ]:
        assert section in text
    assert "This phase does not generate trading signals." in text
    assert "This phase does not generate operational recommendations." in text
    for term in FORBIDDEN_REPORT_TERMS:
        assert term not in text.lower()
