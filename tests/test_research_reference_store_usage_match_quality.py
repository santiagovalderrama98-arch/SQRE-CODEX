from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.match_quality_classifier import (
    classify_evidence_quality,
    classify_match_quality,
)


def test_match_quality_classifies_high_quality_exact_match():
    config = ResearchReferenceStoreUsageReviewConfig()

    quality = classify_match_quality("EXACT_D1_STATE_REGIME_CONTEXT_MATCH", 25, 20.0, config)

    assert quality == "HIGH_QUALITY_REFERENCE_MATCH"


def test_match_quality_classifies_no_match():
    config = ResearchReferenceStoreUsageReviewConfig()

    assert classify_match_quality("NO_REFERENCE_MATCH", 0, 0.0, config) == "NO_USABLE_REFERENCE_MATCH"


def test_evidence_quality_uses_core_thresholds():
    config = ResearchReferenceStoreUsageReviewConfig()

    assert classify_evidence_quality("SUPPORTING_REFERENCE", 25, 20.0, config) == "CORE_REFERENCE_EVIDENCE"
