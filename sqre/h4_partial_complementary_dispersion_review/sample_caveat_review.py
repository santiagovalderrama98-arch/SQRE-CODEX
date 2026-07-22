"""Partial sample caveat review."""

from __future__ import annotations

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    PartialSampleCaveatRow,
    PartialSampleReviewRow,
)


def build_sample_caveat_review(
    sample: PartialSampleReviewRow,
    config: H4PartialComplementaryDispersionReviewConfig,
) -> PartialSampleCaveatRow:
    caveat_class = classify_sample_caveat(sample)
    return PartialSampleCaveatRow(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        coverage_ratio=sample.coverage_ratio,
        baseline_scenario_count=config.baseline_scenario_count,
        partial_sample_caveat_class=caveat_class,
        partial_sample_caveat_diagnostic=_diagnostic(caveat_class),
    )


def classify_sample_caveat(sample: PartialSampleReviewRow) -> str:
    if sample.partial_sample_status == "PARTIAL_UNAVAILABLE":
        return "PARTIAL_SAMPLE_UNAVAILABLE"
    if sample.coverage_ratio >= 0.50 and sample.sample_adequacy_class == "PARTIAL_SAMPLE_RESEARCH_USABLE":
        return "PARTIAL_SAMPLE_ACCEPTABLE_FOR_COMPLEMENTARY_REVIEW"
    if 0.50 <= sample.coverage_ratio < 0.70:
        return "PARTIAL_SAMPLE_LIMITED_INTERPRETATION_REQUIRED"
    if sample.coverage_ratio < 0.50:
        return "PARTIAL_SAMPLE_NOT_COMPARABLE_TO_FULL_BASELINE"
    return "PARTIAL_SAMPLE_LIMITED_INTERPRETATION_REQUIRED"


def _diagnostic(caveat_class: str) -> str:
    diagnostics = {
        "PARTIAL_SAMPLE_ACCEPTABLE_FOR_COMPLEMENTARY_REVIEW": "Partial sample can support complementary descriptive review.",
        "PARTIAL_SAMPLE_LIMITED_INTERPRETATION_REQUIRED": "Partial sample requires limited interpretation.",
        "PARTIAL_SAMPLE_NOT_COMPARABLE_TO_FULL_BASELINE": "Partial sample is not comparable to the full baseline.",
        "PARTIAL_SAMPLE_UNAVAILABLE": "Partial sample was unavailable for caveat review.",
    }
    return diagnostics[caveat_class]
