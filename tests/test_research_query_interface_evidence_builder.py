from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_evidence_builder import classify_evidence, classify_result_quality


def test_quality_and_evidence_classification():
    config = ResearchQueryInterfaceDesignConfig()

    assert (
        classify_result_quality("EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH", 25, 20.0, config)
        == "HIGH_QUALITY_RESEARCH_QUERY_RESULT"
    )
    assert classify_evidence("SUPPORTING_REFERENCE", 12, 20.0, config) == "SUPPORTING_RESEARCH_REFERENCE_EVIDENCE"

