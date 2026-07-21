from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.feasibility_classifier import (
    build_feasibility_matrix,
    build_summary,
    constraint_class,
    feasibility_class,
)
from sqre.h4_expanded_sample_feasibility_review.models import (
    AvailabilityReviewRow,
    RawFileInventoryRow,
    ValidationCoverageRow,
)


def test_feasibility_class_uses_validation_and_availability():
    assert feasibility_class("AVAILABLE_FULL", "VALIDATED", 1.0) == "ALREADY_VALIDATED"
    assert feasibility_class("AVAILABLE_FULL", "NOT_VALIDATED", 1.0) == "FEASIBLE_FULL_SAMPLE"
    assert feasibility_class("AVAILABLE_PARTIAL", "NOT_VALIDATED", 0.5) == "FEASIBLE_PARTIAL_SAMPLE"
    assert feasibility_class("MISSING", "UNKNOWN_VALIDATION_STATUS", 0.0) == "MISSING_SAMPLE"


def test_constraint_class_names_missing_and_raw_file_constraints():
    assert constraint_class("FEASIBLE_FULL_SAMPLE", "AVAILABLE_FULL", "NOT_VALIDATED", "PRESENT") == (
        "NO_MAJOR_CONSTRAINT_IDENTIFIED"
    )
    assert constraint_class("UNKNOWN_FEASIBILITY", "UNKNOWN", "UNKNOWN_VALIDATION_STATUS", "DATE_COVERAGE_UNKNOWN") == (
        "RAW_FILE_CONSTRAINED"
    )
    assert constraint_class("MISSING_SAMPLE", "MISSING", "UNKNOWN_VALIDATION_STATUS", "MISSING") == (
        "SAMPLE_AVAILABILITY_CONSTRAINED"
    )


def test_build_feasibility_matrix_uses_configured_partial_threshold():
    availability = [
        AvailabilityReviewRow("scenario", "EURUSD", "H4", "", "", "AVAILABLE_PARTIAL", 0.6, "", "", "", "NO", "")
    ]
    validation = [ValidationCoverageRow("scenario", "EURUSD", "H4", "NOT_VALIDATED", 0, 0, 0, 0, "MISSING", "")]
    config = H4ExpandedSampleFeasibilityConfig(minimum_partial_coverage_ratio=0.7)

    rows = build_feasibility_matrix(availability, validation, config)

    assert rows[0].feasibility_class == "CONSTRAINED_PARTIAL_SAMPLE"


def test_build_summary_counts_rows_and_readiness():
    raw_files = [RawFileInventoryRow("x", "EURUSD_H4_period_1.csv", "NO", "EURUSD", "H4", 1, "", "", "UNKNOWN", "")]
    availability = [
        AvailabilityReviewRow("scenario", "EURUSD", "H4", "", "", "AVAILABLE_FULL", 1.0, "a", "b", "x", "NO", "")
    ]
    validation = [ValidationCoverageRow("scenario", "EURUSD", "H4", "NOT_VALIDATED", 0, 0, 0, 0, "MISSING", "")]
    rows = build_feasibility_matrix(availability, validation, H4ExpandedSampleFeasibilityConfig())

    summary = build_summary(1, raw_files, rows)

    assert summary.feasible_full_sample_count == 1
    assert summary.raw_h4_file_count == 1
    assert summary.h4_expansion_readiness_flag == "READY_FOR_TARGETED_H4_EXPANSION_VALIDATION"


def test_build_summary_prefers_real_constraints_over_no_major_constraint():
    availability = [
        AvailabilityReviewRow("validated", "EURUSD", "H4", "", "", "AVAILABLE_FULL", 1.0, "a", "b", "x", "NO", ""),
        AvailabilityReviewRow("missing", "EURUSD", "H4", "", "", "MISSING", 0.0, "", "", "", "NO", ""),
    ]
    validation = [
        ValidationCoverageRow("validated", "EURUSD", "H4", "VALIDATED", 1, 1, 1, 1, "PRESENT", ""),
        ValidationCoverageRow("missing", "EURUSD", "H4", "UNKNOWN_VALIDATION_STATUS", 0, 0, 0, 0, "MISSING", ""),
    ]
    rows = build_feasibility_matrix(availability, validation, H4ExpandedSampleFeasibilityConfig())

    summary = build_summary(2, [], rows)

    assert summary.dominant_constraint_class == "SAMPLE_AVAILABILITY_CONSTRAINED"
    assert summary.h4_expansion_readiness_flag == "REQUIRES_DATA_AVAILABILITY_RESOLUTION"
