"""Findings and summary helpers for H4 partial complementary review."""

from __future__ import annotations

from collections import Counter

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    H4PartialComplementaryDispersionSummary,
    PartialBaselineInterpretationRow,
    PartialSampleReviewRow,
)


def build_summary(
    samples: list[PartialSampleReviewRow],
    interpretations: list[PartialBaselineInterpretationRow],
    config: H4PartialComplementaryDispersionReviewConfig,
) -> H4PartialComplementaryDispersionSummary:
    classes = [row.partial_baseline_interpretation_class for row in interpretations]
    counts = Counter(classes)
    support_count = counts["COMPLEMENTARY_EVIDENCE_SUPPORTS_PRIOR_H4_FINDINGS"]
    limited_count = counts["COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED"]
    divergent_count = counts["COMPLEMENTARY_EVIDENCE_DIVERGES_FROM_BASELINE"]
    inconclusive_count = counts["COMPLEMENTARY_EVIDENCE_INCONCLUSIVE"]
    unavailable_count = counts["COMPLEMENTARY_EVIDENCE_UNAVAILABLE"]
    readiness = _readiness_flag(support_count, limited_count, divergent_count, inconclusive_count)
    dominant = _dominant(classes)
    return H4PartialComplementaryDispersionSummary(
        timeframe="H4",
        candidate_count=len(samples),
        reviewed_partial_sample_count=len(interpretations),
        complementary_support_count=support_count,
        consistent_but_limited_count=limited_count,
        divergent_count=divergent_count,
        inconclusive_count=inconclusive_count,
        unavailable_count=unavailable_count,
        baseline_scenario_count=config.baseline_scenario_count,
        average_coverage_ratio=round(_average([sample.coverage_ratio for sample in samples]), 4),
        average_condition_profile_count=round(
            _average([float(sample.condition_profile_count) for sample in samples]),
            4,
        ),
        dominant_partial_baseline_interpretation=dominant,
        h4_partial_complementary_profile=_profile(readiness),
        h4_partial_complementary_readiness_flag=readiness,
        h4_partial_complementary_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_follow_up(readiness),
    )


def research_readiness_assessment(summary: H4PartialComplementaryDispersionSummary | None) -> list[str]:
    if summary is None:
        return ["No summary was generated."]
    return [
        f"Readiness flag: {summary.h4_partial_complementary_readiness_flag}",
        f"Dominant interpretation: {summary.dominant_partial_baseline_interpretation}",
        summary.h4_partial_complementary_diagnostic,
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4 transition/state combined context review after partial sample interpretation",
        "H4/D1 contextual transition review",
        "Manual H4 data availability review",
        "Provider history coverage review",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No data was downloaded.",
        "Partial sample was not silently merged into the full H4 baseline.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Partial sample coverage is incomplete.",
        "Findings depend on local files currently present in the workspace.",
        "Partial sample findings are descriptive.",
        "No provider comparison is produced.",
        "No production calibration decision is made.",
        "No operational decision is produced.",
    ]


def _readiness_flag(support: int, limited: int, divergent: int, inconclusive: int) -> str:
    if support > 0:
        return "PARTIAL_SAMPLE_SUPPORTS_COMPLEMENTARY_H4_REVIEW"
    if limited > 0 and divergent == 0:
        return "PARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION"
    if divergent > 0 or inconclusive > 0:
        return "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW"
    return "PARTIAL_SAMPLE_NOT_USABLE_FOR_COMPLEMENTARY_REVIEW"


def _profile(readiness: str) -> str:
    profiles = {
        "PARTIAL_SAMPLE_SUPPORTS_COMPLEMENTARY_H4_REVIEW": "PARTIAL_COMPLEMENT_SUPPORTIVE",
        "PARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION": "PARTIAL_COMPLEMENT_LIMITED",
        "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW": "PARTIAL_COMPLEMENT_MANUAL_REVIEW",
    }
    return profiles.get(readiness, "PARTIAL_COMPLEMENT_NOT_USABLE")


def _diagnostic(readiness: str) -> str:
    diagnostics = {
        "PARTIAL_SAMPLE_SUPPORTS_COMPLEMENTARY_H4_REVIEW": "Partial sample supports complementary H4 descriptive review.",
        "PARTIAL_SAMPLE_REQUIRES_LIMITED_INTERPRETATION": "Partial sample can be reviewed with explicit coverage caveat.",
        "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW": "Partial sample requires manual review before later research use.",
    }
    return diagnostics.get(readiness, "Partial sample was not usable for complementary review.")


def _follow_up(readiness: str) -> str:
    if readiness == "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW":
        return "Manual H4 data availability review."
    if readiness == "PARTIAL_SAMPLE_NOT_USABLE_FOR_COMPLEMENTARY_REVIEW":
        return "Provider history coverage review."
    return "H4 transition/state combined context review after partial sample interpretation."


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _dominant(values: list[str]) -> str:
    if not values:
        return "COMPLEMENTARY_EVIDENCE_UNAVAILABLE"
    return Counter(values).most_common(1)[0][0]
