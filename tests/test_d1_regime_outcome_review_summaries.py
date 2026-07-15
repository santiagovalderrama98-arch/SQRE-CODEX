from sqre.d1_regime_outcome_review.classification import classify_condition_profiles
from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.models import ConditionProfileInput
from sqre.d1_regime_outcome_review.summaries import (
    build_condition_label_summaries,
    build_d1_review_summary,
    build_dispersion_summaries,
    build_sample_adequacy_summaries,
)


def _profile(condition_type: str, label: str, sample: int, regimes: int, range_cv: float) -> ConditionProfileInput:
    return ConditionProfileInput(
        condition_type=condition_type,
        condition_label=label,
        forward_window=20,
        regime_count=regimes,
        regimes_present="A|B|C|D",
        scenario_count=4,
        total_sample_size=sample,
        average_sample_size_per_regime=sample / max(regimes, 1),
        average_forward_range_pips=20.0,
        average_outcome_magnitude_pips=7.0,
        average_direction_alignment_rate=0.55,
        forward_range_cv=range_cv,
        outcome_magnitude_cv=0.12,
        direction_alignment_cv=0.1,
        regime_sensitivity_flag="",
    )


def test_build_condition_label_and_type_summaries():
    config = D1RegimeOutcomeReviewConfig()
    rows = classify_condition_profiles(
        [
            _profile("STATE", "EXPANSION", 80, 4, 0.10),
            _profile("STATE", "EXPANSION", 10, 4, 0.10),
            _profile("TRANSITION", "A_TO_B", 80, 4, 0.50),
        ],
        config,
    )

    state_summaries = build_condition_label_summaries(rows, "STATE")
    transition_summaries = build_condition_label_summaries(rows, "TRANSITION")
    dispersion_summaries = build_dispersion_summaries(rows)
    sample_summaries = build_sample_adequacy_summaries(rows)
    review_summary = build_d1_review_summary(rows, config)

    assert state_summaries[0].profile_count == 2
    assert transition_summaries[0].regime_sensitive_profile_count == 1
    assert sum(row.high_dispersion_profile_count for row in dispersion_summaries) == 1
    assert sample_summaries[0].scope == "TOTAL"
    assert review_summary.input_profile_count == 3
    assert review_summary.high_dispersion_profile_count == 1
