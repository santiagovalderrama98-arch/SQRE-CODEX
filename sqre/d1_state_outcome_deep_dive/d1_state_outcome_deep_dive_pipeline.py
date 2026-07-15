"""Pipeline for D1 research-ready state outcome deep dive."""

from __future__ import annotations

from pathlib import Path

from sqre.d1_state_outcome_deep_dive.comparative_review import build_regime_comparison_matrix
from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.loader import (
    load_regime_outcomes,
    load_regime_sensitive_profiles,
    load_research_ready_profiles,
)
from sqre.d1_state_outcome_deep_dive.models import D1StateOutcomeDeepDiveResult
from sqre.d1_state_outcome_deep_dive.outcome_statistics import build_outcome_statistics
from sqre.d1_state_outcome_deep_dive.profile_selector import select_state_profiles
from sqre.d1_state_outcome_deep_dive.regime_breakdown import build_regime_breakdown
from sqre.d1_state_outcome_deep_dive.reports import build_state_deep_dive_summary, write_deep_dive_outputs


def run_d1_state_outcome_deep_dive(
    outcome_review_dir: Path | str,
    regime_research_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: D1StateOutcomeDeepDiveConfig | None = None,
) -> D1StateOutcomeDeepDiveResult:
    active_config = config or D1StateOutcomeDeepDiveConfig()
    resolved_outcome_review_dir = Path(outcome_review_dir)
    resolved_regime_research_dir = Path(regime_research_dir)
    resolved_output_dir = Path(output_dir)
    resolved_report_path = Path(report_path)

    research_ready = load_research_ready_profiles(resolved_outcome_review_dir)
    regime_sensitive = load_regime_sensitive_profiles(resolved_outcome_review_dir)
    regime_outcomes = load_regime_outcomes(resolved_regime_research_dir)
    selected = select_state_profiles(research_ready, regime_sensitive, active_config)
    breakdown = build_regime_breakdown(selected, regime_outcomes, active_config)
    statistics = build_outcome_statistics(breakdown, active_config)
    comparisons = build_regime_comparison_matrix(breakdown, statistics, active_config)
    summaries = build_state_deep_dive_summary(statistics)
    result = D1StateOutcomeDeepDiveResult(
        outcome_review_dir=resolved_outcome_review_dir,
        regime_research_dir=resolved_regime_research_dir,
        output_dir=resolved_output_dir,
        report_path=resolved_report_path,
        research_ready_profiles_loaded=len(research_ready),
        regime_sensitive_profiles_loaded=len(regime_sensitive),
        regime_outcomes_loaded=len(regime_outcomes),
        selected_profiles=selected,
        regime_breakdown_rows=breakdown,
        outcome_statistics_rows=statistics,
        comparison_rows=comparisons,
        summary_rows=summaries,
    )
    return write_deep_dive_outputs(result)
