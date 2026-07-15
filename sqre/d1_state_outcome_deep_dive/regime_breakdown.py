"""Build regime-level breakdown for selected D1 state profiles."""

from __future__ import annotations

from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.findings import regime_observation_diagnostic
from sqre.d1_state_outcome_deep_dive.models import RegimeBreakdownRow, RegimeOutcome, StateProfile


def build_regime_breakdown(
    selected_profiles: list[StateProfile],
    regime_outcomes: list[RegimeOutcome],
    config: D1StateOutcomeDeepDiveConfig,
) -> list[RegimeBreakdownRow]:
    rows: list[RegimeBreakdownRow] = []
    for profile in selected_profiles:
        for outcome in _matching_outcomes(profile, regime_outcomes):
            rows.append(
                RegimeBreakdownRow(
                    condition_label=profile.condition_label,
                    forward_window=profile.forward_window,
                    profile_type=profile.profile_type,
                    regime_id=outcome.regime_id,
                    regime_label=outcome.regime_label,
                    scenario_id=outcome.scenario_id,
                    sample_size=outcome.sample_size,
                    average_forward_close_return_pips=outcome.average_forward_close_return_pips,
                    median_forward_close_return_pips=outcome.median_forward_close_return_pips,
                    average_forward_range_pips=outcome.average_forward_range_pips,
                    average_favorable_displacement_pips=outcome.average_favorable_displacement_pips,
                    average_adverse_displacement_pips=outcome.average_adverse_displacement_pips,
                    average_outcome_magnitude_pips=outcome.average_outcome_magnitude_pips,
                    direction_alignment_rate=outcome.direction_alignment_rate,
                    sample_adequacy_flag=outcome.sample_adequacy_flag,
                    regime_observation_diagnostic=regime_observation_diagnostic(
                        profile.profile_type,
                        outcome.sample_size,
                        config,
                    ),
                )
            )
    return rows


def _matching_outcomes(profile: StateProfile, outcomes: list[RegimeOutcome]) -> list[RegimeOutcome]:
    return [
        outcome
        for outcome in outcomes
        if outcome.condition_type.strip().upper() == "STATE_CONDITION"
        and outcome.condition_label == profile.condition_label
        and outcome.forward_window == profile.forward_window
    ]
