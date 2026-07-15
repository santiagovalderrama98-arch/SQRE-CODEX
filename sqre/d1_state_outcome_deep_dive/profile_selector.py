"""Profile selection for D1 state outcome deep dive."""

from __future__ import annotations

from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.models import StateProfile


def select_state_profiles(
    research_ready_profiles: list[StateProfile],
    regime_sensitive_profiles: list[StateProfile],
    config: D1StateOutcomeDeepDiveConfig,
) -> list[StateProfile]:
    selected = [profile for profile in research_ready_profiles if _is_state_condition(profile)]
    if config.include_regime_sensitive_observations:
        selected.extend(profile for profile in regime_sensitive_profiles if _is_selected_sensitive_observation(profile))
    return sorted(selected, key=lambda item: (item.condition_label, item.forward_window, item.profile_type))


def _is_state_condition(profile: StateProfile) -> bool:
    return profile.condition_type.strip().upper() == "STATE_CONDITION"


def _is_selected_sensitive_observation(profile: StateProfile) -> bool:
    return (
        _is_state_condition(profile)
        and profile.condition_label.strip().upper() == "DIRECTIONAL_DISPLACEMENT"
        and profile.forward_window == 3
    )
