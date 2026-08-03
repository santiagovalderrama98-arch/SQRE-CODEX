from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.findings import (
    build_summary,
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.h4_d1_contextual_transition_review.models import (
    H4D1ContextualInterpretationRow,
    ScenarioContextMapRow,
)


def test_findings_are_descriptive_and_non_operational():
    text = "\n".join(potential_follow_up_areas() + do_not_change_yet_lines() + limitation_lines()).lower()

    assert "no operational logic was added" in text
    assert "no data was downloaded" in text
    assert "partial sample was not silently merged" in text


def test_summary_readiness_uses_sample_adequacy_when_sample_review_dominates():
    rows = [
        _interpretation("CTX_1", "D1_CONTEXT_SAMPLE_CONSTRAINED", "REQUIRES_SAMPLE_ADEQUACY_REVIEW"),
        _interpretation("CTX_2", "D1_CONTEXT_SAMPLE_CONSTRAINED", "REQUIRES_SAMPLE_ADEQUACY_REVIEW"),
        _interpretation(
            "CTX_3",
            "D1_CONTEXT_REQUIRES_REGIME_INTERPRETATION",
            "REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION",
        ),
    ]

    summary = build_summary(rows, [_mapping(row.context_id) for row in rows], H4D1ContextualTransitionReviewConfig())

    assert summary.sample_constrained_count == 2
    assert summary.requires_sample_adequacy_review_count == 2
    assert summary.requires_scenario_and_regime_interpretation_count == 1
    assert summary.dominant_h4_d1_contextual_interpretation == "D1_CONTEXT_SAMPLE_CONSTRAINED"
    assert summary.h4_d1_contextual_readiness_flag == "H4_D1_REQUIRES_SAMPLE_ADEQUACY_REVIEW"
    assert "D1 sample adequacy review" in summary.recommended_follow_up
    assert "does not infer scenario/date alignment" in summary.h4_d1_contextual_diagnostic


def test_summary_readiness_preserves_scenario_regime_when_it_dominates():
    rows = [
        _interpretation(
            "CTX_1",
            "D1_CONTEXT_REQUIRES_REGIME_INTERPRETATION",
            "REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION",
        ),
        _interpretation(
            "CTX_2",
            "D1_CONTEXT_REQUIRES_REGIME_INTERPRETATION",
            "REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION",
        ),
        _interpretation("CTX_3", "D1_CONTEXT_SAMPLE_CONSTRAINED", "REQUIRES_SAMPLE_ADEQUACY_REVIEW"),
    ]

    summary = build_summary(rows, [_mapping(row.context_id) for row in rows], H4D1ContextualTransitionReviewConfig())

    assert summary.requires_scenario_and_regime_interpretation_count == 2
    assert summary.requires_sample_adequacy_review_count == 1
    assert summary.h4_d1_contextual_readiness_flag == "H4_D1_REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION"
    assert summary.recommended_follow_up == "D1 regime context deepening"


def test_dominant_sample_constrained_interpretation_maps_to_sample_readiness():
    rows = [_interpretation("CTX_1", "D1_CONTEXT_SAMPLE_CONSTRAINED", "REQUIRES_SAMPLE_ADEQUACY_REVIEW")]

    summary = build_summary(rows, [_mapping("CTX_1")], H4D1ContextualTransitionReviewConfig())

    assert summary.dominant_h4_d1_contextual_interpretation == "D1_CONTEXT_SAMPLE_CONSTRAINED"
    assert summary.h4_d1_contextual_readiness_flag == "H4_D1_REQUIRES_SAMPLE_ADEQUACY_REVIEW"


def _interpretation(
    context_id: str,
    interpretation: str,
    readiness: str,
    d1_regime_label: str = "REGIME_A",
) -> H4D1ContextualInterpretationRow:
    return H4D1ContextualInterpretationRow(
        context_id=context_id,
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
        h4_source_state="EXPANSION",
        h4_target_state="CONSOLIDATION",
        h4_transition_label="EXPANSION -> CONSOLIDATION",
        h4_forward_window="12",
        d1_regime_label=d1_regime_label,
        h4_d1_alignment_class="D1_CONTEXT_AVAILABLE",
        contextual_dispersion_class=interpretation,
        contextual_sensitivity_class="D1_CONTEXTUALIZES_H4_SCENARIO_SENSITIVITY",
        h4_d1_partial_use_class="PARTIAL_CONTEXT_NOT_AVAILABLE",
        h4_d1_contextual_interpretation_class=interpretation,
        h4_d1_contextual_readiness_flag=readiness,
        h4_d1_contextual_diagnostic="Synthetic diagnostic.",
        recommended_follow_up="Synthetic follow-up.",
    )


def _mapping(context_id: str, method: str = "CONDITION_PROFILE_MATCH") -> ScenarioContextMapRow:
    return ScenarioContextMapRow(
        scenario_context_id=context_id,
        symbol="EURUSD",
        h4_scenario_id="",
        d1_scenario_id="",
        d1_regime_label="REGIME_A",
        d1_context_label="EXPANSION -> CONSOLIDATION",
        mapping_method=method,
        mapping_confidence_class="CONDITION_PROFILE_MATCH",
        mapping_diagnostic="Mapped by condition label and forward window; no scenario/date alignment inferred.",
    )
