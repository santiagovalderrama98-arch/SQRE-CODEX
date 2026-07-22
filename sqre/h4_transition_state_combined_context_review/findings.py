"""Summary and report finding helpers."""

from __future__ import annotations

from collections import Counter

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.models import (
    CombinedContextInterpretationRow,
    H4TransitionStateCombinedContextSummary,
)


def build_summary(
    rows: list[CombinedContextInterpretationRow],
    config: H4TransitionStateCombinedContextReviewConfig,
) -> H4TransitionStateCombinedContextSummary:
    interpretation_counts = Counter(row.combined_context_interpretation_class for row in rows)
    readiness_counts = Counter(row.combined_context_readiness_flag for row in rows)
    dominant = _dominant(interpretation_counts)
    readiness = _h4_readiness(readiness_counts, interpretation_counts)
    return H4TransitionStateCombinedContextSummary(
        timeframe=config.timeframe,
        context_count=len(rows),
        aligned_scenario_sensitive_count=interpretation_counts["CONTEXT_REINFORCES_SCENARIO_LEVEL_INTERPRETATION"],
        mixed_diagnostics_count=sum(
            1 for row in rows if row.state_transition_alignment_class == "STATE_TRANSITION_MIXED_DIAGNOSTICS"
        ),
        combined_high_dispersion_count=sum(
            1 for row in rows if row.combined_dispersion_class == "COMBINED_HIGH_DISPERSION"
        ),
        combined_sample_constrained_count=sum(
            1 for row in rows if row.combined_dispersion_class == "COMBINED_SAMPLE_CONSTRAINED"
        ),
        combined_baseline_unavailable_count=sum(
            1 for row in rows if row.combined_dispersion_class == "COMBINED_BASELINE_UNAVAILABLE"
        ),
        combined_scenario_sensitive_count=sum(
            1 for row in rows if row.combined_sensitivity_class == "COMBINED_SCENARIO_SENSITIVE"
        ),
        descriptively_stable_count=interpretation_counts["CONTEXT_DESCRIPTIVELY_STABLE"],
        input_limited_count=interpretation_counts["CONTEXT_INPUT_LIMITED"],
        partial_context_limited_support_count=sum(
            1 for row in rows if row.partial_context_use_class == "PARTIAL_CONTEXT_LIMITED_SUPPORT"
        ),
        ready_for_context_reference_count=readiness_counts["READY_FOR_DESCRIPTIVE_CONTEXT_REFERENCE"],
        requires_scenario_level_interpretation_count=readiness_counts["REQUIRES_SCENARIO_LEVEL_INTERPRETATION"],
        requires_sample_adequacy_review_count=readiness_counts["REQUIRES_SAMPLE_ADEQUACY_REVIEW"],
        requires_input_completeness_review_count=readiness_counts["REQUIRES_INPUT_COMPLETENESS_REVIEW"],
        dominant_combined_context_interpretation=dominant,
        h4_transition_state_context_profile=_profile(dominant),
        h4_transition_state_context_readiness_flag=readiness,
        h4_transition_state_context_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_recommended_follow_up(readiness),
    )


def research_readiness_assessment(summary: H4TransitionStateCombinedContextSummary | None) -> list[str]:
    if summary is None:
        return ["No summary row was produced."]
    return [
        f"Context count: {summary.context_count}",
        f"Dominant combined context interpretation: {summary.dominant_combined_context_interpretation}",
        f"H4 transition/state context readiness flag: {summary.h4_transition_state_context_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4/D1 contextual transition review",
        "Research reference-store design",
        "Manual H4 baseline input completeness review",
        "Provider history coverage review",
        "H1 secondary context monitoring",
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
        "Combined context review is descriptive.",
        "Findings depend on local files currently present in the workspace.",
        "Missing baseline inputs limit interpretation.",
        "Partial sample coverage is incomplete.",
        "No provider comparison is produced.",
        "No production calibration decision is made.",
        "No operational decision is produced.",
    ]


def _dominant(counter: Counter[str]) -> str:
    if not counter:
        return "CONTEXT_INCONCLUSIVE"
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _h4_readiness(readiness_counts: Counter[str], interpretation_counts: Counter[str]) -> str:
    if readiness_counts["REQUIRES_INPUT_COMPLETENESS_REVIEW"]:
        return "H4_CONTEXT_REQUIRES_INPUT_COMPLETENESS_REVIEW"
    if readiness_counts["REQUIRES_SAMPLE_ADEQUACY_REVIEW"]:
        return "H4_CONTEXT_REQUIRES_SAMPLE_ADEQUACY_REVIEW"
    if readiness_counts["REQUIRES_SCENARIO_LEVEL_INTERPRETATION"]:
        return "H4_CONTEXT_REQUIRES_SCENARIO_LEVEL_INTERPRETATION"
    if readiness_counts["READY_FOR_DESCRIPTIVE_CONTEXT_REFERENCE"]:
        return "H4_CONTEXT_SUPPORTS_DESCRIPTIVE_REFERENCE"
    if interpretation_counts:
        return "H4_CONTEXT_INCONCLUSIVE"
    return "H4_CONTEXT_REQUIRES_INPUT_COMPLETENESS_REVIEW"


def _profile(dominant: str) -> str:
    return f"H4_{dominant}"


def _diagnostic(readiness: str) -> str:
    diagnostics = {
        "H4_CONTEXT_REQUIRES_SCENARIO_LEVEL_INTERPRETATION": "Combined context should remain scenario-level descriptive.",
        "H4_CONTEXT_REQUIRES_SAMPLE_ADEQUACY_REVIEW": "Combined context is limited by sample adequacy.",
        "H4_CONTEXT_REQUIRES_INPUT_COMPLETENESS_REVIEW": "Combined context is limited by missing input files.",
        "H4_CONTEXT_SUPPORTS_DESCRIPTIVE_REFERENCE": "Combined context supports descriptive reference use.",
        "H4_CONTEXT_INCONCLUSIVE": "Combined context does not support a stronger readiness class.",
    }
    return diagnostics[readiness]


def _recommended_follow_up(readiness: str) -> str:
    mapping = {
        "H4_CONTEXT_REQUIRES_SCENARIO_LEVEL_INTERPRETATION": "H4/D1 contextual transition review",
        "H4_CONTEXT_REQUIRES_SAMPLE_ADEQUACY_REVIEW": "Provider history coverage review",
        "H4_CONTEXT_REQUIRES_INPUT_COMPLETENESS_REVIEW": "Manual H4 baseline input completeness review",
        "H4_CONTEXT_SUPPORTS_DESCRIPTIVE_REFERENCE": "Research reference-store design",
        "H4_CONTEXT_INCONCLUSIVE": "H1 secondary context monitoring",
    }
    return mapping[readiness]
