"""Pipeline for H4 partial sample complementary dispersion review."""

from __future__ import annotations

from sqre.h4_partial_complementary_dispersion_review.baseline_dispersion_loader import (
    build_source_inventory,
    load_baseline_dispersion_snapshot,
)
from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.findings import build_summary
from sqre.h4_partial_complementary_dispersion_review.models import (
    H4PartialComplementaryDispersionReviewResult,
)
from sqre.h4_partial_complementary_dispersion_review.partial_baseline_interpretation import (
    build_partial_baseline_interpretation,
)
from sqre.h4_partial_complementary_dispersion_review.partial_sample_loader import (
    load_partial_sample_review,
    load_partial_structure_state_snapshot,
    load_partial_transition_snapshot,
)
from sqre.h4_partial_complementary_dispersion_review.reports import write_review_outputs
from sqre.h4_partial_complementary_dispersion_review.sample_caveat_review import build_sample_caveat_review
from sqre.h4_partial_complementary_dispersion_review.sensitivity_complement_review import (
    build_sensitivity_complement_review,
)
from sqre.h4_partial_complementary_dispersion_review.state_complement_review import build_state_complement_review
from sqre.h4_partial_complementary_dispersion_review.transition_complement_review import (
    build_transition_complement_review,
)


def run_h4_partial_complementary_dispersion_review(
    config: H4PartialComplementaryDispersionReviewConfig | None = None,
) -> H4PartialComplementaryDispersionReviewResult:
    active_config = config or H4PartialComplementaryDispersionReviewConfig()
    source_inventory = build_source_inventory(active_config)
    baseline = load_baseline_dispersion_snapshot(active_config)
    samples = load_partial_sample_review(active_config)
    structure_state = load_partial_structure_state_snapshot(active_config)
    transition_snapshot = load_partial_transition_snapshot(active_config)

    state_reviews = []
    transition_reviews = []
    sensitivity_reviews = []
    interpretation_rows = []
    caveat_rows = []

    for sample in samples:
        state_review = build_state_complement_review(sample, structure_state, baseline)
        transition_review = build_transition_complement_review(sample, transition_snapshot, baseline)
        sensitivity_review = build_sensitivity_complement_review(sample, baseline, active_config)
        interpretation = build_partial_baseline_interpretation(
            sample,
            state_review,
            transition_review,
            sensitivity_review,
            active_config,
        )
        caveat = build_sample_caveat_review(sample, active_config)
        state_reviews.append(state_review)
        transition_reviews.append(transition_review)
        sensitivity_reviews.append(sensitivity_review)
        interpretation_rows.append(interpretation)
        caveat_rows.append(caveat)

    summary = build_summary(samples, interpretation_rows, active_config)
    result = H4PartialComplementaryDispersionReviewResult(
        partial_validation_dir=active_config.partial_validation_dir,
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        partial_samples=samples,
        state_reviews=state_reviews,
        transition_reviews=transition_reviews,
        sensitivity_reviews=sensitivity_reviews,
        interpretation_rows=interpretation_rows,
        caveat_rows=caveat_rows,
        summary=summary,
    )
    return write_review_outputs(result)
