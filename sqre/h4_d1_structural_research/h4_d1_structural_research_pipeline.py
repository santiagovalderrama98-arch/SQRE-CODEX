"""Pipeline for H4/D1 structural research."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.findings import build_h4_d1_findings, build_timeframe_summaries
from sqre.h4_d1_structural_research.loader import load_h4_d1_scenario_data
from sqre.h4_d1_structural_research.models import H4D1StructuralResearchResult
from sqre.h4_d1_structural_research.price_outcome_profiles import build_price_outcome_profiles
from sqre.h4_d1_structural_research.reports import write_h4_d1_outputs, write_h4_d1_research_report
from sqre.h4_d1_structural_research.sequence_profiles import build_sequence_research_profiles
from sqre.h4_d1_structural_research.state_profiles import build_state_research_profiles
from sqre.h4_d1_structural_research.transition_profiles import build_transition_research_profiles


def run_h4_d1_structural_research(
    *,
    validation_summary: Path | str,
    validation_output_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: H4D1StructuralResearchConfig | None = None,
) -> H4D1StructuralResearchResult:
    active_config = config or H4D1StructuralResearchConfig()
    scenarios = load_h4_d1_scenario_data(validation_summary, validation_output_dir)
    inventory_rows = [scenario.inventory for scenario in scenarios]
    state_profiles = build_state_research_profiles(scenarios, active_config)
    transition_profiles = build_transition_research_profiles(scenarios, active_config)
    price_profiles = build_price_outcome_profiles(scenarios, active_config)
    sequence_profiles = build_sequence_research_profiles(scenarios, active_config)
    timeframe_summaries = build_timeframe_summaries(
        inventory_rows,
        state_profiles,
        transition_profiles,
        price_profiles,
        sequence_profiles,
        active_config,
    )
    findings = build_h4_d1_findings(timeframe_summaries)
    result = H4D1StructuralResearchResult(
        input_validation_summary=str(validation_summary),
        validation_output_dir=str(validation_output_dir),
        scenarios_loaded=len(scenarios),
        output_dir=Path(output_dir),
        report_path=Path(report_path),
        inventory_rows=inventory_rows,
        state_profiles=state_profiles,
        transition_profiles=transition_profiles,
        price_outcome_profiles=price_profiles,
        sequence_profiles=sequence_profiles,
        timeframe_summaries=timeframe_summaries,
        findings=findings,
    )
    write_h4_d1_outputs(output_dir, result)
    write_h4_d1_research_report(report_path, result)
    return result
