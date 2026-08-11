from __future__ import annotations

from sqre.reference_stability_documentation.follow_up_documentation_builder import build_follow_up_plan


def test_follow_up_builder_produces_dashboard_stability_indicators_as_high_priority():
    follow_up = build_follow_up_plan(True)

    row = follow_up[follow_up["Follow_Up_Category"] == "DASHBOARD_STABILITY_INDICATORS"].iloc[0]
    assert row["Follow_Up_Priority"] == "HIGH"
