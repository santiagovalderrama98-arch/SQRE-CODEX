"""Feasibility classification for H4 expanded sample review."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict

from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.findings import (
    constraint_diagnostic,
    feasibility_diagnostic,
    summary_diagnostic,
    summary_follow_up,
)
from sqre.h4_expanded_sample_feasibility_review.models import (
    AvailabilityReviewRow,
    ConstrainedOrMissingSample,
    FeasibilityMatrixRow,
    FeasibleExpansionCandidate,
    H4ExpandedSampleFeasibilitySummary,
    RawFileInventoryRow,
    ValidationCoverageRow,
)


def build_feasibility_matrix(
    availability_rows: list[AvailabilityReviewRow],
    validation_rows: list[ValidationCoverageRow],
    config: H4ExpandedSampleFeasibilityConfig,
) -> list[FeasibilityMatrixRow]:
    validation_by_id = {row.scenario_id: row for row in validation_rows}
    rows: list[FeasibilityMatrixRow] = []
    for row in availability_rows:
        validation = validation_by_id.get(row.scenario_id)
        validation_status = validation.validation_status if validation else "UNKNOWN_VALIDATION_STATUS"
        research_status = validation.research_output_status if validation else "MISSING"
        raw_file_status = _raw_file_status(row)
        feasibility = feasibility_class(
            row.availability_status,
            validation_status,
            row.coverage_ratio,
            partial_threshold=config.minimum_partial_coverage_ratio,
        )
        constraint = constraint_class(feasibility, row.availability_status, validation_status, raw_file_status)
        rows.append(
            FeasibilityMatrixRow(
                scenario_id=row.scenario_id,
                symbol=row.symbol,
                timeframe=row.timeframe,
                defined_start_date=row.defined_start_date,
                defined_end_date=row.defined_end_date,
                availability_status=row.availability_status,
                validation_status=validation_status,
                coverage_ratio=row.coverage_ratio,
                raw_file_status=raw_file_status,
                research_output_status=research_status,
                feasibility_class=feasibility,
                constraint_class=constraint,
                feasibility_diagnostic=feasibility_diagnostic(feasibility),
                recommended_follow_up=constraint_diagnostic(constraint),
            )
        )
    return rows


def feasibility_class(
    availability_status: str,
    validation_status: str,
    coverage_ratio: float,
    partial_threshold: float = 0.50,
) -> str:
    if validation_status == "VALIDATED":
        return "ALREADY_VALIDATED"
    if availability_status == "AVAILABLE_FULL":
        return "FEASIBLE_FULL_SAMPLE"
    if availability_status == "AVAILABLE_PARTIAL" and coverage_ratio >= partial_threshold:
        return "FEASIBLE_PARTIAL_SAMPLE"
    if availability_status == "AVAILABLE_PARTIAL":
        return "CONSTRAINED_PARTIAL_SAMPLE"
    if availability_status == "MISSING":
        return "MISSING_SAMPLE"
    return "UNKNOWN_FEASIBILITY"


def constraint_class(
    feasibility: str,
    availability_status: str,
    validation_status: str,
    raw_file_status: str,
) -> str:
    if feasibility in {"ALREADY_VALIDATED", "FEASIBLE_FULL_SAMPLE"}:
        return "NO_MAJOR_CONSTRAINT_IDENTIFIED"
    if raw_file_status == "DATE_COVERAGE_UNKNOWN":
        return "RAW_FILE_CONSTRAINED"
    if availability_status in {"AVAILABLE_FULL", "AVAILABLE_PARTIAL"} and validation_status != "VALIDATED":
        return "VALIDATION_OUTPUT_CONSTRAINED"
    if feasibility in {"CONSTRAINED_PARTIAL_SAMPLE", "MISSING_SAMPLE"}:
        return "SAMPLE_AVAILABILITY_CONSTRAINED"
    return "UNKNOWN_CONSTRAINT"


def build_feasible_candidates(rows: list[FeasibilityMatrixRow]) -> list[FeasibleExpansionCandidate]:
    return [
        FeasibleExpansionCandidate(
            **asdict(row),
            candidate_rationale="H4 sample has descriptive availability evidence for targeted validation review.",
        )
        for row in rows
        if row.feasibility_class in {"FEASIBLE_FULL_SAMPLE", "FEASIBLE_PARTIAL_SAMPLE"}
    ]


def build_constrained_or_missing_samples(rows: list[FeasibilityMatrixRow]) -> list[ConstrainedOrMissingSample]:
    return [
        ConstrainedOrMissingSample(
            **asdict(row),
            constraint_rationale=row.recommended_follow_up,
        )
        for row in rows
        if row.feasibility_class in {"CONSTRAINED_PARTIAL_SAMPLE", "MISSING_SAMPLE", "UNKNOWN_FEASIBILITY"}
    ]


def build_summary(
    defined_count: int,
    raw_files: list[RawFileInventoryRow],
    rows: list[FeasibilityMatrixRow],
) -> H4ExpandedSampleFeasibilitySummary:
    already = _count(rows, "ALREADY_VALIDATED")
    full = _count(rows, "FEASIBLE_FULL_SAMPLE")
    partial = _count(rows, "FEASIBLE_PARTIAL_SAMPLE")
    constrained = _count(rows, "CONSTRAINED_PARTIAL_SAMPLE")
    missing = _count(rows, "MISSING_SAMPLE")
    unknown = _count(rows, "UNKNOWN_FEASIBILITY")
    coverage = [row.coverage_ratio for row in rows]
    dominant_constraint = _dominant_constraint([row.constraint_class for row in rows])
    profile = _profile(already, full, partial, constrained, missing, unknown)
    readiness = _readiness(full, partial, dominant_constraint, unknown)
    return H4ExpandedSampleFeasibilitySummary(
        timeframe="H4",
        defined_h4_sample_count=defined_count,
        already_validated_count=already,
        feasible_full_sample_count=full,
        feasible_partial_sample_count=partial,
        constrained_partial_sample_count=constrained,
        missing_sample_count=missing,
        unknown_feasibility_count=unknown,
        raw_h4_file_count=sum(1 for row in raw_files if row.partial_file_flag == "NO"),
        partial_h4_file_count=sum(1 for row in raw_files if row.partial_file_flag == "YES"),
        average_coverage_ratio=sum(coverage) / len(coverage) if coverage else 0.0,
        minimum_coverage_ratio=min(coverage) if coverage else 0.0,
        maximum_coverage_ratio=max(coverage) if coverage else 0.0,
        dominant_constraint_class=dominant_constraint,
        h4_expansion_feasibility_profile=profile,
        h4_expansion_readiness_flag=readiness,
        h4_expansion_feasibility_diagnostic=summary_diagnostic(profile, dominant_constraint),
        recommended_follow_up=summary_follow_up(readiness),
    )


def _raw_file_status(row: AvailabilityReviewRow) -> str:
    if not row.raw_file_path:
        return "MISSING"
    if not row.actual_start_date or not row.actual_end_date:
        return "DATE_COVERAGE_UNKNOWN"
    return "PRESENT"


def _count(rows: list[FeasibilityMatrixRow], value: str) -> int:
    return sum(1 for row in rows if row.feasibility_class == value)


def _dominant_constraint(classes: list[str]) -> str:
    clean = [item for item in classes if item]
    if not clean:
        return "UNKNOWN_CONSTRAINT"
    constrained = [item for item in clean if item != "NO_MAJOR_CONSTRAINT_IDENTIFIED"]
    if constrained:
        clean = constrained
    counts = Counter(clean)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _profile(already: int, full: int, partial: int, constrained: int, missing: int, unknown: int) -> str:
    if full + partial > 0:
        return "EXPANSION_POSSIBLE"
    if constrained + missing > 0 and full + partial == 0:
        return "EXPANSION_CONSTRAINED"
    if already > 0 and constrained + missing + unknown + full + partial == 0:
        return "ALREADY_VALIDATED_ONLY"
    return "UNKNOWN_EXPANSION_PROFILE"


def _readiness(full: int, partial: int, dominant_constraint: str, unknown: int) -> str:
    if full > 0 or partial > 0:
        return "READY_FOR_TARGETED_H4_EXPANSION_VALIDATION"
    if dominant_constraint == "PROVIDER_HISTORY_CONSTRAINED":
        return "REQUIRES_PROVIDER_HISTORY_REVIEW"
    if dominant_constraint in {"SAMPLE_AVAILABILITY_CONSTRAINED", "RAW_FILE_CONSTRAINED"}:
        return "REQUIRES_DATA_AVAILABILITY_RESOLUTION"
    if unknown > 0:
        return "REQUIRES_MANUAL_SAMPLE_REVIEW"
    return "NO_EXPANSION_CANDIDATES_IDENTIFIED"
