from __future__ import annotations

from sqre.dashboard_stability_indicators.stability_indicator_legend_builder import build_stability_indicator_legend


def test_indicator_legend_contains_required_indicators():
    legend = build_stability_indicator_legend(True)

    assert {
        "STABLE_EVIDENCE",
        "PARTIAL_EVIDENCE",
        "STABILITY_WARNING",
        "DOCUMENTATION_ONLY",
        "FALLBACK_DEPENDENT",
        "DIRECTIONALLY_UNSTABLE",
        "HORIZON_PARTIAL",
        "GRANULARITY_PARTIAL",
        "SAMPLE_STABLE",
        "DISPERSION_STABLE",
    }.issubset(set(legend["Indicator_Key"]))
