"""Pipeline for D1 regime outcome dispersion and sample adequacy review."""

from __future__ import annotations

from pathlib import Path

from sqre.d1_regime_outcome_review.classification import (
    classify_condition_profiles,
    limited_coverage_profiles,
    low_sample_profiles,
    regime_sensitive_profiles,
    research_ready_profiles,
)
from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.loader import load_condition_profiles
from sqre.d1_regime_outcome_review.models import D1RegimeOutcomeReviewResult
from sqre.d1_regime_outcome_review.reports import write_review_outputs
from sqre.d1_regime_outcome_review.summaries import (
    build_condition_label_summaries,
    build_d1_review_summary,
    build_dispersion_summaries,
    build_sample_adequacy_summaries,
)


def run_d1_regime_outcome_review(
    input_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: D1RegimeOutcomeReviewConfig | None = None,
) -> D1RegimeOutcomeReviewResult:
    active_config = config or D1RegimeOutcomeReviewConfig()
    resolved_input_dir = Path(input_dir)
    resolved_output_dir = Path(output_dir)
    resolved_report_path = Path(report_path)

    profiles = load_condition_profiles(resolved_input_dir)
    inventory_rows = classify_condition_profiles(profiles, active_config)
    result = D1RegimeOutcomeReviewResult(
        input_dir=resolved_input_dir,
        output_dir=resolved_output_dir,
        report_path=resolved_report_path,
        profiles_loaded=len(profiles),
        inventory_rows=inventory_rows,
        research_ready_profiles=research_ready_profiles(inventory_rows),
        regime_sensitive_profiles=regime_sensitive_profiles(inventory_rows),
        low_sample_profiles=low_sample_profiles(inventory_rows),
        limited_coverage_profiles=limited_coverage_profiles(inventory_rows),
        state_summaries=build_condition_label_summaries(inventory_rows, "STATE"),
        transition_summaries=build_condition_label_summaries(inventory_rows, "TRANSITION"),
        dispersion_summaries=build_dispersion_summaries(inventory_rows),
        sample_adequacy_summaries=build_sample_adequacy_summaries(inventory_rows),
        review_summary=build_d1_review_summary(inventory_rows, active_config),
    )
    return write_review_outputs(result)
