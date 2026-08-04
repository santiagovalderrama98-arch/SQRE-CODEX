from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.outcome_profile_builder import classify_outcome_sample_adequacy


def test_sample_adequacy_classifies_ready_and_insufficient_samples():
    config = H4D1AlignedForwardOutcomeResearchConfig(
        minimum_outcome_sample_size=4,
        minimum_context_outcome_sample_size=2,
    )

    assert classify_outcome_sample_adequacy(4, "H4_TRANSITION_ONLY", config) == "OUTCOME_RESEARCH_READY_SAMPLE"
    assert classify_outcome_sample_adequacy(0, "H4_TRANSITION_PLUS_D1_REGIME", config) == "INSUFFICIENT_OUTCOME_SAMPLE"
