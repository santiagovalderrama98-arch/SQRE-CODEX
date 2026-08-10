from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.stability_interpretation_builder import build_stability_interpretation_guide


def test_interpretation_builder_documents_stable_partial_constrained_and_unstable_evidence():
    scorecard = pd.DataFrame(
        [
            {"Stability_Dimension": "Reference Population", "Dominant_Stability_Class": "REFERENCE_POPULATION_AVAILABLE"},
            {"Stability_Dimension": "Horizon Stability", "Dominant_Stability_Class": "PARTIAL_HORIZON_STABILITY"},
            {"Stability_Dimension": "Granularity Stability", "Dominant_Stability_Class": "FRAGMENTED_GRANULARITY_CONTEXT"},
            {"Stability_Dimension": "Directional Consistency", "Dominant_Stability_Class": "DIRECTIONAL_BEHAVIOR_UNSTABLE"},
        ]
    )

    guide = build_stability_interpretation_guide(scorecard)

    assert "DOCUMENTED_STABLE_EVIDENCE" in set(guide["Documentation_Class"])
    assert "DOCUMENTED_PARTIAL_EVIDENCE" in set(guide["Documentation_Class"])
    assert "DOCUMENTED_CONSTRAINED_EVIDENCE" in set(guide["Documentation_Class"])
    assert "DOCUMENTED_UNSTABLE_EVIDENCE" in set(guide["Documentation_Class"])
