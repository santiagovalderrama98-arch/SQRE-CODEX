from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.models import RegimeOutcome, StateProfile
from sqre.d1_state_outcome_deep_dive.regime_breakdown import build_regime_breakdown


def test_regime_breakdown_joins_selected_profiles_to_outcomes():
    rows = build_regime_breakdown(
        [StateProfile("STATE_CONDITION", "DIRECTIONAL_EXPANSION", 3, "RESEARCH_READY")],
        [
            RegimeOutcome("STATE_CONDITION", "DIRECTIONAL_EXPANSION", 3, "R1", "Regime 1", "S1", sample_size=30),
            RegimeOutcome("STATE_CONDITION", "DIRECTIONAL_DISPLACEMENT", 3, "R2", "Regime 2", "S2", sample_size=30),
        ],
        D1StateOutcomeDeepDiveConfig(),
    )

    assert len(rows) == 1
    assert rows[0].regime_id == "R1"
    assert rows[0].regime_observation_diagnostic == "Regime observation supports descriptive state outcome review"


def test_regime_breakdown_flags_limited_sample_before_sensitive_observation():
    rows = build_regime_breakdown(
        [StateProfile("STATE_CONDITION", "DIRECTIONAL_DISPLACEMENT", 3, "REGIME_SENSITIVE_OBSERVATION")],
        [RegimeOutcome("STATE_CONDITION", "DIRECTIONAL_DISPLACEMENT", 3, "R1", "Regime 1", "S1", sample_size=10)],
        D1StateOutcomeDeepDiveConfig(minimum_total_sample_size=20),
    )

    assert rows[0].regime_observation_diagnostic == "Regime observation has limited sample size"
