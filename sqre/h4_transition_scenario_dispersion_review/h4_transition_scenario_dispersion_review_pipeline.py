"""Pipeline for H4 transition scenario dispersion review."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from sqre.h4_transition_scenario_dispersion_review.classification import h4_aggregation_readiness_flag
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig
from sqre.h4_transition_scenario_dispersion_review.findings import h4_summary_diagnostic, h4_summary_follow_up
from sqre.h4_transition_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
    optional_file_status,
)
from sqre.h4_transition_scenario_dispersion_review.models import (
    AggregationCandidateProfile,
    H4TransitionScenarioDispersionReviewResult,
    H4TransitionScenarioDispersionReviewSummary,
    ProfileDispersionDiagnostic,
    SampleConstrainedProfile,
    ScenarioSensitiveProfile,
)
from sqre.h4_transition_scenario_dispersion_review.reports import write_review_outputs
from sqre.h4_transition_scenario_dispersion_review.transition_scenario_contribution import build_scenario_contributions
from sqre.h4_transition_scenario_dispersion_review.transition_family_dispersion import (
    build_transition_family_dispersion_summary,
    mean,
)
from sqre.h4_transition_scenario_dispersion_review.transition_profile_dispersion import build_profile_dispersion_diagnostics
from sqre.h4_transition_scenario_dispersion_review.transition_state_dispersion import (
    build_source_state_dispersion_summary,
    build_target_state_dispersion_summary,
)
from sqre.h4_transition_scenario_dispersion_review.transition_window_dispersion import (
    build_transition_window_dispersion_summary,
)


def run_h4_transition_scenario_dispersion_review(
    input_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: H4TransitionScenarioDispersionReviewConfig | None = None,
) -> H4TransitionScenarioDispersionReviewResult:
    active_config = config or H4TransitionScenarioDispersionReviewConfig()
    resolved_input_dir = Path(input_dir)
    resolved_output_dir = Path(output_dir)
    resolved_report_path = Path(report_path)

    profiles = load_profile_inventory(resolved_input_dir)
    statistics = load_outcome_statistics(resolved_input_dir)
    comparisons = load_scenario_comparisons(resolved_input_dir)
    diagnostics = build_profile_dispersion_diagnostics(profiles, statistics, comparisons, active_config)
    scenario_contributions = build_scenario_contributions(comparisons, active_config)
    family_summaries = build_transition_family_dispersion_summary(diagnostics)
    source_state_summaries = build_source_state_dispersion_summary(diagnostics)
    target_state_summaries = build_target_state_dispersion_summary(diagnostics)
    window_summaries = build_transition_window_dispersion_summary(diagnostics)
    aggregation_candidates = _aggregation_candidates(diagnostics)
    scenario_sensitive = _scenario_sensitive_profiles(diagnostics)
    sample_constrained = _sample_constrained_profiles(diagnostics, active_config)
    summary = _build_summary(
        diagnostics=diagnostics,
        scenario_contributions=scenario_contributions,
        aggregation_candidates=len(aggregation_candidates),
        scenario_sensitive=len(scenario_sensitive),
        sample_constrained=len(sample_constrained),
    )
    missing_optional_files = [
        name for name, present in optional_file_status(resolved_input_dir).items() if not present
    ]
    result = H4TransitionScenarioDispersionReviewResult(
        input_dir=resolved_input_dir,
        output_dir=resolved_output_dir,
        report_path=resolved_report_path,
        profiles_loaded=len(profiles) if profiles else len(statistics),
        statistics_loaded=len(statistics),
        comparison_rows_loaded=len(comparisons),
        profile_diagnostics=diagnostics,
        scenario_contributions=scenario_contributions,
        family_summaries=family_summaries,
        source_state_summaries=source_state_summaries,
        target_state_summaries=target_state_summaries,
        window_summaries=window_summaries,
        aggregation_candidates=aggregation_candidates,
        scenario_sensitive_profiles=scenario_sensitive,
        sample_constrained_profiles=sample_constrained,
        review_summary=summary,
        missing_optional_files=missing_optional_files,
    )
    return write_review_outputs(result)


def _aggregation_candidates(rows: list[ProfileDispersionDiagnostic]) -> list[AggregationCandidateProfile]:
    selected = [
        row
        for row in rows
        if row.profile_type == "RESEARCH_READY"
        and row.profile_dispersion_class in {"STABLE_DESCRIPTIVE", "MODERATE_DISPERSION"}
        and row.high_deviation_scenario_count <= 1
    ]
    return [
        AggregationCandidateProfile(
            **asdict(row),
            aggregation_candidate_rationale="Profile meets descriptive aggregation candidate criteria.",
        )
        for row in selected
    ]


def _scenario_sensitive_profiles(rows: list[ProfileDispersionDiagnostic]) -> list[ScenarioSensitiveProfile]:
    selected = [
        row
        for row in rows
        if row.profile_dispersion_class == "HIGH_DISPERSION"
        or row.high_deviation_scenario_count >= 2
        or row.dominant_deviation_class == "HIGH_DEVIATION"
        or row.profile_type == "SCENARIO_SENSITIVE_OBSERVATION"
    ]
    return [
        ScenarioSensitiveProfile(
            **asdict(row),
            scenario_sensitivity_rationale="Profile meets scenario-sensitive review criteria.",
        )
        for row in selected
    ]


def _sample_constrained_profiles(
    rows: list[ProfileDispersionDiagnostic],
    config: H4TransitionScenarioDispersionReviewConfig,
) -> list[SampleConstrainedProfile]:
    selected = [
        row
        for row in rows
        if row.profile_type == "SAMPLE_CONSTRAINED_OBSERVATION"
        or row.total_sample_size < config.minimum_total_sample_size
        or row.scenario_count < config.minimum_scenario_count
    ]
    return [
        SampleConstrainedProfile(
            **asdict(row),
            sample_review_rationale="Profile meets sample adequacy review criteria.",
        )
        for row in selected
    ]


def _build_summary(
    diagnostics: list[ProfileDispersionDiagnostic],
    scenario_contributions: list,
    aggregation_candidates: int,
    scenario_sensitive: int,
    sample_constrained: int,
) -> H4TransitionScenarioDispersionReviewSummary:
    research_ready = sum(1 for row in diagnostics if row.profile_type == "RESEARCH_READY")
    high = sum(1 for row in diagnostics if row.profile_dispersion_class == "HIGH_DISPERSION")
    moderate = sum(1 for row in diagnostics if row.profile_dispersion_class == "MODERATE_DISPERSION")
    stable = sum(1 for row in diagnostics if row.profile_dispersion_class == "STABLE_DESCRIPTIVE")
    high_contribution = sum(1 for row in scenario_contributions if row.scenario_contribution_class == "HIGH_CONTRIBUTION")
    moderate_contribution = sum(1 for row in scenario_contributions if row.scenario_contribution_class == "MODERATE_CONTRIBUTION")
    low_contribution = sum(1 for row in scenario_contributions if row.scenario_contribution_class == "LOW_CONTRIBUTION")
    readiness = h4_aggregation_readiness_flag(aggregation_candidates, scenario_sensitive, research_ready)
    return H4TransitionScenarioDispersionReviewSummary(
        timeframe="H4",
        input_profile_count=len(diagnostics),
        research_ready_profile_count=research_ready,
        scenario_sensitive_profile_count=scenario_sensitive,
        sample_constrained_profile_count=sample_constrained,
        aggregation_candidate_profile_count=aggregation_candidates,
        high_dispersion_profile_count=high,
        moderate_dispersion_profile_count=moderate,
        stable_profile_count=stable,
        scenario_count=len(scenario_contributions),
        high_contribution_scenario_count=high_contribution,
        moderate_contribution_scenario_count=moderate_contribution,
        low_contribution_scenario_count=low_contribution,
        average_forward_range_cv=mean([row.forward_range_cv for row in diagnostics]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in diagnostics]),
        average_direction_alignment_dispersion=mean([row.direction_alignment_dispersion for row in diagnostics]),
        h4_transition_dispersion_profile=_dominant_dispersion_label(high, moderate, stable),
        h4_transition_aggregation_readiness_flag=readiness,
        h4_transition_scenario_dispersion_diagnostic=h4_summary_diagnostic(
            aggregation_candidates,
            scenario_sensitive,
            sample_constrained,
        ),
        recommended_follow_up=h4_summary_follow_up(scenario_sensitive, sample_constrained),
    )


def _dominant_dispersion_label(high: int, moderate: int, stable: int) -> str:
    if high >= moderate and high >= stable:
        return "HIGH_DISPERSION_PROFILE"
    if moderate >= stable:
        return "MODERATE_DISPERSION_PROFILE"
    return "STABLE_DESCRIPTIVE_PROFILE"
