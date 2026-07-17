"""Build scenario-level breakdown for selected H4 transition profiles."""

from __future__ import annotations

from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.findings import scenario_observation_diagnostic
from sqre.h4_transition_outcome_deep_dive.models import H4TransitionProfile, ScenarioBreakdownRow, ScenarioOutcome


def build_scenario_breakdown(
    selected_profiles: list[H4TransitionProfile],
    scenario_outcomes: list[ScenarioOutcome],
    config: H4TransitionOutcomeDeepDiveConfig,
) -> list[ScenarioBreakdownRow]:
    rows: list[ScenarioBreakdownRow] = []
    for profile in selected_profiles:
        for outcome in _matching_outcomes(profile, scenario_outcomes):
            rows.append(
                ScenarioBreakdownRow(
                    condition_label=profile.condition_label,
                    source_state=profile.source_state,
                    target_state=profile.target_state,
                    transition_family=profile.transition_family,
                    forward_window=profile.forward_window,
                    profile_type=profile.profile_type,
                    scenario_id=outcome.scenario_id,
                    timeframe=outcome.timeframe,
                    sample_size=outcome.sample_size,
                    average_forward_close_return_pips=outcome.average_forward_close_return_pips,
                    median_forward_close_return_pips=outcome.median_forward_close_return_pips,
                    average_forward_range_pips=outcome.average_forward_range_pips,
                    average_favorable_displacement_pips=outcome.average_favorable_displacement_pips,
                    average_adverse_displacement_pips=outcome.average_adverse_displacement_pips,
                    average_outcome_magnitude_pips=outcome.average_outcome_magnitude_pips,
                    direction_alignment_rate=outcome.direction_alignment_rate,
                    sample_adequacy_flag=outcome.sample_adequacy_flag,
                    scenario_observation_diagnostic=scenario_observation_diagnostic(
                        profile.profile_type,
                        outcome.sample_size,
                        config,
                    ),
                )
            )
    return rows


def _matching_outcomes(profile: H4TransitionProfile, outcomes: list[ScenarioOutcome]) -> list[ScenarioOutcome]:
    return [
        outcome
        for outcome in outcomes
        if outcome.timeframe.strip().upper() == "H4"
        and outcome.condition_type.strip().upper() == "TRANSITION_CONDITION"
        and outcome.condition_label == profile.condition_label
        and outcome.forward_window == profile.forward_window
    ]
