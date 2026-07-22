"""Pipeline for H4 targeted partial expansion validation."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_targeted_partial_expansion_validation.baseline_loader import load_baseline_metrics
from sqre.h4_targeted_partial_expansion_validation.candidate_selector import load_partial_candidates
from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.models import H4TargetedPartialExpansionResult
from sqre.h4_targeted_partial_expansion_validation.partial_output_loader import (
    load_price_outcome_summary,
    load_structure_state_summary,
    load_transition_summary,
)
from sqre.h4_targeted_partial_expansion_validation.partial_sample_runner import run_partial_sample
from sqre.h4_targeted_partial_expansion_validation.partial_vs_baseline_review import (
    build_partial_vs_baseline_comparison,
)
from sqre.h4_targeted_partial_expansion_validation.reports import write_review_outputs
from sqre.h4_targeted_partial_expansion_validation.sample_adequacy_review import (
    build_review_summary,
    build_sample_adequacy_row,
)


def run_h4_targeted_partial_expansion_validation(
    config: H4TargetedPartialExpansionValidationConfig | None = None,
) -> H4TargetedPartialExpansionResult:
    active_config = config or H4TargetedPartialExpansionValidationConfig()
    candidates = load_partial_candidates(active_config)
    baseline = load_baseline_metrics(active_config.baseline_validation_dir, active_config.baseline_research_dir)

    run_summaries = []
    structure_state_summaries = []
    transition_summaries = []
    price_outcome_summaries = []
    comparisons = []
    adequacy_rows = []

    for candidate in candidates:
        run = run_partial_sample(candidate, active_config)
        run_summaries.append(run)
        structure_state = load_structure_state_summary(candidate, run, active_config)
        transition = load_transition_summary(candidate, run, active_config)
        price = load_price_outcome_summary(candidate, run, active_config)
        structure_state_summaries.append(structure_state)
        transition_summaries.append(transition)
        price_outcome_summaries.append(price)
        comparisons.append(build_partial_vs_baseline_comparison(candidate, structure_state, transition, price, baseline))
        adequacy_rows.append(build_sample_adequacy_row(candidate, run, structure_state))

    summary = build_review_summary("H4", candidates, run_summaries, adequacy_rows, baseline.scenario_count)
    result = H4TargetedPartialExpansionResult(
        feasibility_dir=active_config.feasibility_dir,
        baseline_validation_dir=active_config.baseline_validation_dir,
        baseline_research_dir=active_config.baseline_research_dir,
        output_dir=active_config.output_dir,
        research_output_dir=active_config.research_output_dir,
        report_path=active_config.report_path,
        candidates=candidates,
        run_summaries=run_summaries,
        structure_state_summaries=structure_state_summaries,
        transition_summaries=transition_summaries,
        price_outcome_summaries=price_outcome_summaries,
        baseline_comparisons=comparisons,
        sample_adequacy_rows=adequacy_rows,
        summary=summary,
    )
    return write_review_outputs(result)
