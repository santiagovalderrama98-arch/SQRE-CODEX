"""Summary and descriptive finding helpers."""

from __future__ import annotations

from collections import Counter

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.models import (
    H4D1ContextualInterpretationRow,
    H4D1ContextualTransitionSummary,
    ScenarioContextMapRow,
)


def build_summary(
    rows: list[H4D1ContextualInterpretationRow],
    mappings: list[ScenarioContextMapRow],
    config: H4D1ContextualTransitionReviewConfig,
) -> H4D1ContextualTransitionSummary:
    interpretations = Counter(row.h4_d1_contextual_interpretation_class for row in rows)
    readiness = Counter(row.h4_d1_contextual_readiness_flag for row in rows)
    dispersion = Counter(row.contextual_dispersion_class for row in rows)
    sensitivity = Counter(row.contextual_sensitivity_class for row in rows)
    mapped_count = sum(1 for row in mappings if row.mapping_method != "UNMAPPED")
    dominant = _dominant(interpretations)
    flag = _summary_readiness(readiness)
    return H4D1ContextualTransitionSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        context_count=len(rows),
        mapped_context_count=mapped_count,
        unmapped_context_count=len(mappings) - mapped_count,
        d1_regime_count=len({row.d1_regime_label for row in rows if row.d1_regime_label != "D1_CONTEXT_UNMAPPED"}),
        d1_context_reinforces_h4_dispersion_count=dispersion["D1_CONTEXT_REINFORCES_H4_DISPERSION"],
        d1_context_segments_h4_dispersion_count=dispersion["D1_CONTEXT_SEGMENTS_H4_DISPERSION"],
        d1_context_does_not_reduce_h4_dispersion_count=dispersion["D1_CONTEXT_DOES_NOT_REDUCE_H4_DISPERSION"],
        d1_reinforces_h4_scenario_sensitivity_count=sensitivity["D1_REINFORCES_H4_SCENARIO_SENSITIVITY"],
        d1_contextualizes_h4_scenario_sensitivity_count=sensitivity["D1_CONTEXTUALIZES_H4_SCENARIO_SENSITIVITY"],
        input_limited_count=readiness["REQUIRES_INPUT_COMPLETENESS_REVIEW"],
        sample_constrained_count=readiness["REQUIRES_SAMPLE_ADEQUACY_REVIEW"],
        ready_for_contextual_reference_count=readiness["READY_FOR_CONTEXTUAL_DESCRIPTIVE_REFERENCE"],
        requires_scenario_and_regime_interpretation_count=readiness["REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION"],
        requires_sample_adequacy_review_count=readiness["REQUIRES_SAMPLE_ADEQUACY_REVIEW"],
        requires_input_completeness_review_count=readiness["REQUIRES_INPUT_COMPLETENESS_REVIEW"],
        dominant_h4_d1_contextual_interpretation=dominant,
        h4_d1_contextual_profile=f"H4_D1_{dominant}",
        h4_d1_contextual_readiness_flag=flag,
        h4_d1_contextual_diagnostic=_diagnostic(flag),
        recommended_follow_up=_follow_up(flag),
    )


def descriptive_findings(summary: H4D1ContextualTransitionSummary | None) -> list[str]:
    if summary is None:
        return ["No summary row was produced."]
    return [
        f"Context count: {summary.context_count}",
        f"Mapped context count: {summary.mapped_context_count}",
        f"Unmapped context count: {summary.unmapped_context_count}",
        f"Dominant H4/D1 contextual interpretation: {summary.dominant_h4_d1_contextual_interpretation}",
        f"H4/D1 contextual readiness flag: {summary.h4_d1_contextual_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "Research reference-store design",
        "H4/D1 scenario mapping completeness review",
        "D1 regime context deepening",
        "H1 secondary context monitoring",
        "Manual provider history coverage review",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No data was downloaded.",
        "Partial sample was not silently merged into the full H4 baseline.",
    ]


def limitation_lines() -> list[str]:
    return [
        "H4/D1 contextual review is descriptive.",
        "Findings depend on local files currently present in the workspace.",
        "Scenario/regime mapping may be limited by available identifiers.",
        "Partial sample coverage is incomplete.",
        "No provider comparison is produced.",
        "No production calibration decision is made.",
        "No operational decision is produced.",
    ]


def _dominant(counter: Counter[str]) -> str:
    if not counter:
        return "D1_CONTEXT_INCONCLUSIVE"
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _summary_readiness(readiness: Counter[str]) -> str:
    if readiness["REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION"]:
        return "H4_D1_REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION"
    if readiness["REQUIRES_SAMPLE_ADEQUACY_REVIEW"]:
        return "H4_D1_REQUIRES_SAMPLE_ADEQUACY_REVIEW"
    if readiness["REQUIRES_INPUT_COMPLETENESS_REVIEW"]:
        return "H4_D1_REQUIRES_INPUT_COMPLETENESS_REVIEW"
    if readiness["READY_FOR_CONTEXTUAL_DESCRIPTIVE_REFERENCE"]:
        return "H4_D1_SUPPORTS_CONTEXTUAL_DESCRIPTIVE_REFERENCE"
    return "H4_D1_CONTEXT_INCONCLUSIVE"


def _diagnostic(flag: str) -> str:
    diagnostics = {
        "H4_D1_REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION": "H4/D1 context remains scenario and regime-level descriptive.",
        "H4_D1_REQUIRES_SAMPLE_ADEQUACY_REVIEW": "H4/D1 context requires sample adequacy review.",
        "H4_D1_REQUIRES_INPUT_COMPLETENESS_REVIEW": "H4/D1 context requires input completeness review.",
        "H4_D1_SUPPORTS_CONTEXTUAL_DESCRIPTIVE_REFERENCE": "H4/D1 context supports descriptive reference use.",
        "H4_D1_CONTEXT_INCONCLUSIVE": "H4/D1 context remains inconclusive.",
    }
    return diagnostics[flag]


def _follow_up(flag: str) -> str:
    mapping = {
        "H4_D1_REQUIRES_SCENARIO_AND_REGIME_LEVEL_INTERPRETATION": "D1 regime context deepening",
        "H4_D1_REQUIRES_SAMPLE_ADEQUACY_REVIEW": "Manual provider history coverage review",
        "H4_D1_REQUIRES_INPUT_COMPLETENESS_REVIEW": "H4/D1 scenario mapping completeness review",
        "H4_D1_SUPPORTS_CONTEXTUAL_DESCRIPTIVE_REFERENCE": "Research reference-store design",
        "H4_D1_CONTEXT_INCONCLUSIVE": "H1 secondary context monitoring",
    }
    return mapping[flag]
