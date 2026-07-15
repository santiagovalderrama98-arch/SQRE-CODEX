"""Pipeline for D1 regime-normalized research."""

from __future__ import annotations

from pathlib import Path

from sqre.d1_regime_normalized_research.config import D1RegimeResearchConfig, load_d1_regime_research_config
from sqre.d1_regime_normalized_research.findings import build_d1_regime_summary
from sqre.d1_regime_normalized_research.loader import load_d1_regime_scenario_data
from sqre.d1_regime_normalized_research.models import D1RegimeResearchResult
from sqre.d1_regime_normalized_research.outcome_profiles import (
    build_condition_outcomes,
    build_normalized_condition_profiles,
    state_condition_profiles,
    transition_condition_profiles,
)
from sqre.d1_regime_normalized_research.reports import (
    write_d1_regime_outputs,
    write_d1_regime_research_report,
)


def run_d1_regime_normalized_research(
    config_path: Path | str,
    validation_summary_path: Path | str,
    validation_output_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    overrides: D1RegimeResearchConfig | None = None,
) -> D1RegimeResearchResult:
    config = overrides or load_d1_regime_research_config(config_path)
    scenarios = load_d1_regime_scenario_data(validation_summary_path, validation_output_dir, config)
    condition_outcomes = build_condition_outcomes(scenarios, config)
    condition_profiles = build_normalized_condition_profiles(condition_outcomes, config)
    state_profiles = state_condition_profiles(condition_profiles)
    transition_profiles = transition_condition_profiles(condition_profiles)
    summary = build_d1_regime_summary(scenarios, condition_profiles, state_profiles, transition_profiles)
    result = D1RegimeResearchResult(
        config_path=str(config_path),
        input_validation_summary=str(validation_summary_path),
        validation_output_dir=str(validation_output_dir),
        output_dir=Path(output_dir),
        report_path=Path(report_path),
        scenarios_loaded=len(scenarios),
        regimes_loaded=len({scenario.inventory.regime_id for scenario in scenarios}),
        inventory_rows=[scenario.inventory for scenario in scenarios],
        condition_outcomes=condition_outcomes,
        condition_profiles=condition_profiles,
        state_profiles=state_profiles,
        transition_profiles=transition_profiles,
        summary=summary,
    )
    write_d1_regime_outputs(output_dir, result)
    write_d1_regime_research_report(report_path, result)
    return result
