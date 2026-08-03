from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.feasibility_classifier import build_summary
from sqre.h4_d1_temporal_alignment_feasibility_review.models import (
    AlignmentCandidateReviewRow,
    SourceInventoryRow,
    TemporalKeyInventoryRow,
)


def test_summary_produces_condition_level_only_not_temporal_alignment():
    sources = [
        SourceInventoryRow("h4", "H4_COMBINED_CONTEXT", "h4.csv", True, "LOADED", 1, "loaded"),
        SourceInventoryRow("d1", "D1_REGIME_OUTCOME", "d1.csv", True, "LOADED", 1, "loaded"),
    ]
    keys = [_key("h4", "H4_COMBINED_CONTEXT"), _key("d1", "D1_REGIME_OUTCOME")]
    candidates = [
        AlignmentCandidateReviewRow(
            "CAND_000001",
            "h4",
            "d1",
            "CONDITION_ONLY_KEYS_AVAILABLE",
            "CONDITION_ONLY_KEYS_AVAILABLE",
            "CONDITION_ONLY_MATCH_NOT_TEMPORAL",
            "CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT",
            "NO_TEMPORAL_ALIGNMENT_CONFIDENCE",
            "condition-only",
        )
    ]

    summary = build_summary(sources, keys, candidates, H4D1TemporalAlignmentFeasibilityConfig())

    assert summary.dominant_alignment_feasibility_class == "CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT"
    assert summary.temporal_alignment_readiness_flag == "CONDITION_LEVEL_ONLY_NOT_TEMPORAL_ALIGNMENT"
    assert summary.recommended_follow_up == "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE"


def _key(name: str, source_type: str) -> TemporalKeyInventoryRow:
    return TemporalKeyInventoryRow(
        name,
        source_type,
        f"{name}.csv",
        1,
        "",
        "",
        "",
        "",
        "",
        "Condition_Label|Forward_Window",
        "",
        "CONDITION_ONLY_KEYS_AVAILABLE",
        "condition only",
    )
