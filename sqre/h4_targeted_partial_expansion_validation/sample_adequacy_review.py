"""Sample adequacy review for targeted H4 partial validation."""

from __future__ import annotations

from sqre.h4_targeted_partial_expansion_validation.models import (
    H4TargetedPartialExpansionSummary,
    PartialCandidate,
    PartialSampleAdequacyRow,
    PartialStructureStateSummary,
    PartialValidationRunSummary,
)


def build_sample_adequacy_row(
    candidate: PartialCandidate,
    run: PartialValidationRunSummary,
    structure_state: PartialStructureStateSummary | None = None,
) -> PartialSampleAdequacyRow:
    structure_count = structure_state.structure_count if structure_state else run.structure_count
    state_count = run.state_count
    transition_count = run.transition_count
    condition_count = run.condition_profile_count
    adequacy_class = classify_sample_adequacy(
        candidate.raw_file_status,
        candidate.coverage_ratio,
        run.ohlc_rows,
        structure_count,
        state_count,
        transition_count,
    )
    return PartialSampleAdequacyRow(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        coverage_ratio=candidate.coverage_ratio,
        ohlc_rows=run.ohlc_rows,
        structure_count=structure_count,
        state_count=state_count,
        transition_count=transition_count,
        condition_profile_count=condition_count,
        sample_adequacy_class=adequacy_class,
        sample_adequacy_diagnostic=diagnostic_for_adequacy(adequacy_class),
        recommended_follow_up=follow_up_for_adequacy(adequacy_class),
    )


def classify_sample_adequacy(
    raw_file_status: str,
    coverage_ratio: float,
    ohlc_rows: int,
    structure_count: int,
    state_count: int,
    transition_count: int,
) -> str:
    if raw_file_status != "FOUND":
        return "PARTIAL_SAMPLE_UNAVAILABLE"
    if coverage_ratio >= 0.50 and ohlc_rows > 0 and structure_count >= 20 and state_count >= 20 and transition_count >= 10:
        return "PARTIAL_SAMPLE_RESEARCH_USABLE"
    if coverage_ratio >= 0.30 and ohlc_rows > 0 and structure_count >= 10:
        return "PARTIAL_SAMPLE_LIMITED"
    return "PARTIAL_SAMPLE_INSUFFICIENT"


def build_review_summary(
    timeframe: str,
    candidates: list[PartialCandidate],
    runs: list[PartialValidationRunSummary],
    adequacy_rows: list[PartialSampleAdequacyRow],
    baseline_scenario_count: int,
) -> H4TargetedPartialExpansionSummary:
    completed = sum(1 for row in runs if row.run_status == "COMPLETED")
    failed = sum(1 for row in runs if row.run_status == "FAILED")
    usable = sum(1 for row in adequacy_rows if row.sample_adequacy_class == "PARTIAL_SAMPLE_RESEARCH_USABLE")
    limited = sum(1 for row in adequacy_rows if row.sample_adequacy_class == "PARTIAL_SAMPLE_LIMITED")
    insufficient = sum(1 for row in adequacy_rows if row.sample_adequacy_class == "PARTIAL_SAMPLE_INSUFFICIENT")
    unavailable = sum(1 for row in adequacy_rows if row.sample_adequacy_class == "PARTIAL_SAMPLE_UNAVAILABLE")
    coverage_values = [row.coverage_ratio for row in candidates]
    profile = expansion_profile(completed, usable, limited, len(candidates))
    readiness = readiness_flag(completed, usable, limited, insufficient, unavailable, len(candidates))
    return H4TargetedPartialExpansionSummary(
        timeframe=timeframe,
        candidate_count=len(candidates),
        validated_partial_candidate_count=completed,
        failed_candidate_count=failed,
        partial_sample_count=len(candidates),
        baseline_scenario_count=baseline_scenario_count,
        average_coverage_ratio=round(sum(coverage_values) / len(coverage_values), 4) if coverage_values else 0.0,
        partial_research_usable_count=usable,
        partial_limited_count=limited,
        partial_insufficient_count=insufficient,
        partial_unavailable_count=unavailable,
        h4_partial_expansion_profile=profile,
        h4_partial_expansion_readiness_flag=readiness,
        h4_partial_expansion_diagnostic=diagnostic_for_profile(profile),
        recommended_follow_up=summary_follow_up(readiness),
    )


def expansion_profile(completed: int, usable: int, limited: int, candidate_count: int) -> str:
    if completed > 0 and usable > 0:
        return "PARTIAL_EXPANSION_VALIDATED"
    if completed > 0 and limited > 0:
        return "PARTIAL_EXPANSION_LIMITED"
    if candidate_count == 0:
        return "PARTIAL_EXPANSION_UNAVAILABLE"
    return "UNKNOWN_PARTIAL_EXPANSION_PROFILE"


def readiness_flag(
    completed: int,
    usable: int,
    limited: int,
    insufficient: int,
    unavailable: int,
    candidate_count: int,
) -> str:
    if completed > 0 and usable > 0:
        return "PARTIAL_SAMPLE_READY_FOR_COMPLEMENTARY_REVIEW"
    if completed > 0 and limited > 0:
        return "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW"
    if insufficient > 0 or unavailable > 0:
        return "PARTIAL_SAMPLE_NOT_USABLE"
    if candidate_count == 0:
        return "NO_PARTIAL_CANDIDATES_AVAILABLE"
    return "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW"


def diagnostic_for_adequacy(adequacy_class: str) -> str:
    return {
        "PARTIAL_SAMPLE_RESEARCH_USABLE": "Partial H4 sample is usable for complementary descriptive review.",
        "PARTIAL_SAMPLE_LIMITED": "Partial H4 sample is usable only as a limited complementary sample.",
        "PARTIAL_SAMPLE_INSUFFICIENT": "Partial H4 sample does not provide enough evidence for complementary review.",
        "PARTIAL_SAMPLE_UNAVAILABLE": "Partial H4 sample is unavailable in the current workspace.",
    }.get(adequacy_class, "Partial H4 sample requires manual review.")


def follow_up_for_adequacy(adequacy_class: str) -> str:
    return {
        "PARTIAL_SAMPLE_RESEARCH_USABLE": "H4 partial sample complementary dispersion review",
        "PARTIAL_SAMPLE_LIMITED": "Manual H4 data availability review",
        "PARTIAL_SAMPLE_INSUFFICIENT": "Provider history coverage review",
        "PARTIAL_SAMPLE_UNAVAILABLE": "Manual H4 data availability review",
    }.get(adequacy_class, "Manual H4 data availability review")


def diagnostic_for_profile(profile: str) -> str:
    return {
        "PARTIAL_EXPANSION_VALIDATED": "At least one partial H4 candidate completed targeted validation.",
        "PARTIAL_EXPANSION_LIMITED": "Partial H4 candidate completed validation with limited sample adequacy.",
        "PARTIAL_EXPANSION_UNAVAILABLE": "No partial H4 candidate can be validated from local files.",
    }.get(profile, "Partial H4 validation status remains uncertain.")


def summary_follow_up(readiness: str) -> str:
    return {
        "PARTIAL_SAMPLE_READY_FOR_COMPLEMENTARY_REVIEW": "H4 partial sample complementary dispersion review",
        "PARTIAL_SAMPLE_REQUIRES_MANUAL_REVIEW": "Manual H4 data availability review",
        "PARTIAL_SAMPLE_NOT_USABLE": "Provider history coverage review",
        "NO_PARTIAL_CANDIDATES_AVAILABLE": "Manual H4 data availability review",
    }.get(readiness, "Manual H4 data availability review")
