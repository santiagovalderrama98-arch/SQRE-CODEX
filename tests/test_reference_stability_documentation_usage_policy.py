from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.evidence_usage_policy_builder import build_evidence_usage_policy


def test_usage_policy_distinguishes_safe_warning_and_documentation_only_use():
    summary = pd.DataFrame(
        {
            "Core_Reference_Count": [3],
            "Supporting_Reference_Count": [2],
            "Stable_Sample_Group_Count": [4],
            "Stable_Dispersion_Group_Count": [4],
            "Partial_Horizon_Count": [1],
            "Partial_Granularity_Count": [1],
            "Fallback_Dependent_Match_Level_Count": [1],
            "Dashboard_Reference_Card_Count": [2],
        }
    )

    policy = build_evidence_usage_policy(summary)

    assert "SAFE_FOR_MANUAL_RESEARCH_REVIEW" in set(policy["Evidence_Usage_Policy_Class"])
    assert "USE_WITH_STABILITY_WARNINGS" in set(policy["Evidence_Usage_Policy_Class"])
    assert "DOCUMENTATION_ONLY" in set(policy["Evidence_Usage_Policy_Class"])
