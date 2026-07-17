"""Select scenario-sensitive H4 state profiles for main review."""

from __future__ import annotations

from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.models import ScenarioSensitiveProfileInput


def select_review_profiles(
    profiles: list[ScenarioSensitiveProfileInput],
    config: H4ScenarioSensitiveStateReviewConfig,
) -> list[ScenarioSensitiveProfileInput]:
    focus = {state.upper() for state in config.focus_states}
    selected = [
        row
        for row in profiles
        if row.condition_label.upper() in focus
        and row.profile_type != "SAMPLE_CONSTRAINED_OBSERVATION"
        and _is_scenario_sensitive(row)
    ]
    return sorted(selected, key=lambda row: (row.condition_label, row.forward_window))


def _is_scenario_sensitive(row: ScenarioSensitiveProfileInput) -> bool:
    return (
        row.profile_research_readiness_class == "SCENARIO_SENSITIVE_REVIEW"
        or row.profile_dispersion_class == "HIGH_DISPERSION"
        or row.high_deviation_scenario_count > 0
        or row.dominant_deviation_class == "HIGH_DEVIATION"
    )
