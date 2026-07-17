"""Pipeline for H4 transition outcome deep dive."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_transition_outcome_deep_dive.comparative_review import build_scenario_comparison_matrix
from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.loader import load_price_outcome_profiles, load_scenario_outcomes
from sqre.h4_transition_outcome_deep_dive.models import H4TransitionOutcomeDeepDiveResult
from sqre.h4_transition_outcome_deep_dive.outcome_statistics import build_outcome_statistics
from sqre.h4_transition_outcome_deep_dive.profile_selector import select_h4_transition_profiles
from sqre.h4_transition_outcome_deep_dive.reports import (
    build_transition_deep_dive_summary,
    build_transition_family_summary,
    write_deep_dive_outputs,
)
from sqre.h4_transition_outcome_deep_dive.scenario_breakdown import build_scenario_breakdown


def run_h4_transition_outcome_deep_dive(
    h4_d1_research_dir: Path | str,
    validation_output_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: H4TransitionOutcomeDeepDiveConfig | None = None,
) -> H4TransitionOutcomeDeepDiveResult:
    active_config = config or H4TransitionOutcomeDeepDiveConfig()
    resolved_h4_d1_research_dir = Path(h4_d1_research_dir)
    resolved_validation_output_dir = Path(validation_output_dir)
    resolved_output_dir = Path(output_dir)
    resolved_report_path = Path(report_path)

    price_profiles = load_price_outcome_profiles(resolved_h4_d1_research_dir)
    scenario_outcomes = load_scenario_outcomes(resolved_validation_output_dir)
    selected = select_h4_transition_profiles(price_profiles, active_config)
    breakdown = build_scenario_breakdown(selected, scenario_outcomes, active_config)
    statistics = build_outcome_statistics(breakdown, active_config)
    comparisons = build_scenario_comparison_matrix(breakdown, statistics, active_config)
    family_summaries = build_transition_family_summary(statistics)
    summaries = build_transition_deep_dive_summary(statistics)
    result = H4TransitionOutcomeDeepDiveResult(
        h4_d1_research_dir=resolved_h4_d1_research_dir,
        validation_output_dir=resolved_validation_output_dir,
        output_dir=resolved_output_dir,
        report_path=resolved_report_path,
        price_profiles_loaded=len(price_profiles),
        scenario_outcomes_loaded=len(scenario_outcomes),
        selected_profiles=selected,
        scenario_breakdown_rows=breakdown,
        outcome_statistics_rows=statistics,
        comparison_rows=comparisons,
        family_summary_rows=family_summaries,
        summary_rows=summaries,
    )
    return write_deep_dive_outputs(result)
