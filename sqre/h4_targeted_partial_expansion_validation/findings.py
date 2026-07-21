"""Descriptive finding text for H4 targeted partial expansion validation."""

from __future__ import annotations

from sqre.h4_targeted_partial_expansion_validation.models import H4TargetedPartialExpansionSummary


def research_readiness_assessment(summary: H4TargetedPartialExpansionSummary | None) -> list[str]:
    if summary is None:
        return ["No partial H4 candidate was available for review."]
    if summary.h4_partial_expansion_readiness_flag == "PARTIAL_SAMPLE_READY_FOR_COMPLEMENTARY_REVIEW":
        return ["Partial H4 sample completed targeted validation and may support complementary review."]
    if summary.h4_partial_expansion_readiness_flag == "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW":
        return ["Partial H4 sample is usable only as a limited complementary sample."]
    if summary.h4_partial_expansion_readiness_flag == "PARTIAL_SAMPLE_NOT_USABLE":
        return ["Partial H4 sample does not provide enough evidence for complementary review."]
    return ["Partial H4 sample is unavailable in the current workspace."]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4 partial sample complementary dispersion review",
        "H4 transition and state combined context review after partial sample interpretation",
        "Manual H4 data availability review",
        "Provider history coverage review",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "Do not merge the partial sample silently into the full H4 baseline.",
        "Do not change production defaults from this diagnostic output.",
        "Do not change thresholds from this diagnostic output.",
        "Do not add runtime action logic from this diagnostic output.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Partial sample comparison is descriptive and does not make production calibration decisions.",
        "Partial sample coverage may reduce interpretive strength.",
        "Baseline files can be absent in a local workspace; missing optional files are handled safely.",
    ]
