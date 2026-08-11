from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.stability_indicator_mapper import build_stability_indicator_map


def test_indicator_mapper_maps_stable_partial_and_unstable_evidence():
    frame = pd.DataFrame(
        {
            "Stability_Dimension": ["Stable", "Partial", "Unstable"],
            "Observed_Stability_Class": ["A", "B", "C"],
            "Documentation_Class": [
                "DOCUMENTED_STABLE_EVIDENCE",
                "DOCUMENTED_PARTIAL_EVIDENCE",
                "DOCUMENTED_UNSTABLE_EVIDENCE",
            ],
            "Evidence_Usage_Policy_Class": ["SAFE", "WARNING", "DOCUMENTATION"],
        }
    )

    mapped = build_stability_indicator_map(frame)

    assert "STABLE_EVIDENCE_INDICATOR" in set(mapped["Dashboard_Stability_Indicator_Class"])
    assert "PARTIAL_EVIDENCE_INDICATOR" in set(mapped["Dashboard_Stability_Indicator_Class"])
    assert "WARNING_EVIDENCE_INDICATOR" in set(mapped["Dashboard_Stability_Indicator_Class"])
