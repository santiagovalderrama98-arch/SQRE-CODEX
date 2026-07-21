"""Descriptive findings for H4 expanded sample feasibility review."""

from __future__ import annotations


def feasibility_diagnostic(feasibility_class: str) -> str:
    return {
        "ALREADY_VALIDATED": "H4 sample already has validation/research evidence",
        "FEASIBLE_FULL_SAMPLE": "H4 sample appears available for targeted validation review",
        "FEASIBLE_PARTIAL_SAMPLE": "H4 sample appears partially available and may support targeted partial validation review",
        "CONSTRAINED_PARTIAL_SAMPLE": "H4 sample is partially available but constrained for full-period validation",
        "MISSING_SAMPLE": "H4 sample is missing or unavailable in current local data",
        "UNKNOWN_FEASIBILITY": "H4 sample feasibility cannot be determined from available diagnostics",
    }.get(feasibility_class, "H4 sample feasibility requires review")


def constraint_diagnostic(constraint_class: str) -> str:
    return {
        "NO_MAJOR_CONSTRAINT_IDENTIFIED": "No major sample feasibility constraint identified",
        "SAMPLE_AVAILABILITY_CONSTRAINED": "H4 sample expansion is constrained by available sample coverage",
        "PROVIDER_HISTORY_CONSTRAINED": "H4 sample expansion appears constrained by historical provider coverage",
        "VALIDATION_OUTPUT_CONSTRAINED": "H4 sample appears available but lacks validation output evidence",
        "RAW_FILE_CONSTRAINED": "H4 raw file exists but cannot provide reliable date coverage",
        "UNKNOWN_CONSTRAINT": "H4 expansion constraint cannot be determined from available diagnostics",
    }.get(constraint_class, "H4 expansion constraint requires review")


def summary_diagnostic(feasibility_profile: str, dominant_constraint: str) -> str:
    if feasibility_profile == "EXPANSION_POSSIBLE":
        return "H4 has candidates for targeted expanded validation review"
    if dominant_constraint == "PROVIDER_HISTORY_CONSTRAINED":
        return "H4 expansion appears constrained by available historical provider coverage"
    if feasibility_profile == "ALREADY_VALIDATED_ONLY":
        return "H4 currently has no additional expansion candidates beyond validated samples"
    return "H4 expanded sample feasibility requires manual data availability review"


def summary_follow_up(readiness_flag: str) -> str:
    return {
        "READY_FOR_TARGETED_H4_EXPANSION_VALIDATION": "Prepare targeted H4 expansion validation only after confirming local sample availability.",
        "REQUIRES_DATA_AVAILABILITY_RESOLUTION": "Resolve local H4 sample availability diagnostics before additional validation.",
        "REQUIRES_PROVIDER_HISTORY_REVIEW": "Review historical provider coverage before additional H4 sample planning.",
        "REQUIRES_MANUAL_SAMPLE_REVIEW": "Review H4 sample definitions and local files manually.",
        "NO_EXPANSION_CANDIDATES_IDENTIFIED": "Continue research with currently validated H4 samples.",
    }.get(readiness_flag, "Continue descriptive H4 sample feasibility review.")
