"""Models for H4 expanded sample feasibility review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SourceInventoryRow:
    source_name: str
    source_type: str
    path: str
    exists: str
    load_status: str
    rows_loaded: int = 0
    h4_rows_loaded: int = 0
    diagnostic: str = ""


@dataclass(frozen=True)
class DefinedSampleRow:
    scenario_id: str
    symbol: str
    timeframe: str
    defined_start_date: str
    defined_end_date: str
    source_config: str
    sample_definition_status: str
    sample_definition_diagnostic: str
    raw_file_hint: str = ""


@dataclass(frozen=True)
class RawFileInventoryRow:
    file_path: str
    file_name: str
    partial_file_flag: str
    symbol: str
    timeframe: str
    row_count: int
    first_date: str
    last_date: str
    date_coverage_status: str
    raw_file_diagnostic: str


@dataclass(frozen=True)
class AvailabilityReviewRow:
    scenario_id: str
    symbol: str
    timeframe: str
    defined_start_date: str
    defined_end_date: str
    availability_status: str
    coverage_ratio: float
    actual_start_date: str
    actual_end_date: str
    raw_file_path: str
    partial_file_flag: str
    availability_diagnostic: str


@dataclass(frozen=True)
class ValidationCoverageRow:
    scenario_id: str
    symbol: str
    timeframe: str
    validation_status: str
    ohlc_rows: int
    structure_count: int
    state_count: int
    transition_count: int
    research_output_status: str
    validation_coverage_diagnostic: str


@dataclass(frozen=True)
class FeasibilityMatrixRow:
    scenario_id: str
    symbol: str
    timeframe: str
    defined_start_date: str
    defined_end_date: str
    availability_status: str
    validation_status: str
    coverage_ratio: float
    raw_file_status: str
    research_output_status: str
    feasibility_class: str
    constraint_class: str
    feasibility_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class FeasibleExpansionCandidate(FeasibilityMatrixRow):
    candidate_rationale: str = ""


@dataclass(frozen=True)
class ConstrainedOrMissingSample(FeasibilityMatrixRow):
    constraint_rationale: str = ""


@dataclass(frozen=True)
class H4ExpandedSampleFeasibilitySummary:
    timeframe: str
    defined_h4_sample_count: int
    already_validated_count: int
    feasible_full_sample_count: int
    feasible_partial_sample_count: int
    constrained_partial_sample_count: int
    missing_sample_count: int
    unknown_feasibility_count: int
    raw_h4_file_count: int
    partial_h4_file_count: int
    average_coverage_ratio: float
    minimum_coverage_ratio: float
    maximum_coverage_ratio: float
    dominant_constraint_class: str
    h4_expansion_feasibility_profile: str
    h4_expansion_readiness_flag: str
    h4_expansion_feasibility_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4ExpandedSampleFeasibilityResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    defined_samples: list[DefinedSampleRow] = field(default_factory=list)
    raw_files: list[RawFileInventoryRow] = field(default_factory=list)
    availability_rows: list[AvailabilityReviewRow] = field(default_factory=list)
    validation_rows: list[ValidationCoverageRow] = field(default_factory=list)
    feasibility_rows: list[FeasibilityMatrixRow] = field(default_factory=list)
    feasible_candidates: list[FeasibleExpansionCandidate] = field(default_factory=list)
    constrained_or_missing_samples: list[ConstrainedOrMissingSample] = field(default_factory=list)
    summary: H4ExpandedSampleFeasibilitySummary | None = None
