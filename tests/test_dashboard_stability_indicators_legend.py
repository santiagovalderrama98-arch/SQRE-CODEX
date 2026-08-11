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


def test_indicator_legend_text_has_clean_spacing():
    legend = build_stability_indicator_legend(True)
    text = " ".join(legend.astype(str).stack().tolist()).lower()

    assert "evidencestability" not in text
    assert "oroperational" not in text
    assert "andquality" not in text
    assert "evidence has acceptable sample" in text
