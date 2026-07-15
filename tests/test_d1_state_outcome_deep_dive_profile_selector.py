from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.models import StateProfile
from sqre.d1_state_outcome_deep_dive.profile_selector import select_state_profiles


def test_selector_includes_only_state_condition_research_ready_profiles():
    selected = select_state_profiles(
        [
            StateProfile("STATE_CONDITION", "DIRECTIONAL_EXPANSION", 3, "RESEARCH_READY"),
            StateProfile("TRANSITION_CONDITION", "A_TO_B", 3, "RESEARCH_READY"),
        ],
        [],
        D1StateOutcomeDeepDiveConfig(),
    )

    assert len(selected) == 1
    assert selected[0].condition_label == "DIRECTIONAL_EXPANSION"


def test_selector_includes_only_configured_sensitive_observation_when_enabled():
    selected = select_state_profiles(
        [],
        [
            StateProfile("STATE_CONDITION", "DIRECTIONAL_DISPLACEMENT", 3, "REGIME_SENSITIVE_OBSERVATION"),
            StateProfile("STATE_CONDITION", "DIRECTIONAL_EXPANSION", 3, "REGIME_SENSITIVE_OBSERVATION"),
            StateProfile("STATE_CONDITION", "DIRECTIONAL_DISPLACEMENT", 6, "REGIME_SENSITIVE_OBSERVATION"),
        ],
        D1StateOutcomeDeepDiveConfig(include_regime_sensitive_observations=True),
    )

    assert len(selected) == 1
    assert selected[0].condition_label == "DIRECTIONAL_DISPLACEMENT"
    assert selected[0].forward_window == 3


def test_selector_excludes_sensitive_observation_when_disabled():
    selected = select_state_profiles(
        [],
        [StateProfile("STATE_CONDITION", "DIRECTIONAL_DISPLACEMENT", 3, "REGIME_SENSITIVE_OBSERVATION")],
        D1StateOutcomeDeepDiveConfig(include_regime_sensitive_observations=False),
    )

    assert selected == []
