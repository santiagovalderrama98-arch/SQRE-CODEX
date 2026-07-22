"""Load optional H4 baseline dispersion outputs."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.loader import (
    first_row,
    int_value,
    read_optional_csv,
    source_status,
    text_value,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    BaselineDispersionSnapshot,
    SourceInventoryRow,
)


EXPECTED_PARTIAL_FILES = [
    "h4_partial_candidate_inventory.csv",
    "h4_partial_validation_run_summary.csv",
    "h4_partial_structure_state_summary.csv",
    "h4_partial_transition_summary.csv",
    "h4_partial_price_outcome_summary.csv",
    "h4_partial_vs_baseline_comparison.csv",
    "h4_partial_sample_adequacy_review.csv",
    "h4_targeted_partial_expansion_validation_summary.csv",
]


def build_source_inventory(
    config: H4PartialComplementaryDispersionReviewConfig,
) -> list[SourceInventoryRow]:
    rows = []
    for filename in EXPECTED_PARTIAL_FILES:
        rows.append(_source_row(filename, "PARTIAL_VALIDATION", config.partial_validation_dir / filename))
    rows.extend(
        [
            _source_row(
                "h4_scenario_dispersion_review_summary.csv",
                "OPTIONAL_STATE_BASELINE",
                config.h4_state_dispersion_dir / "h4_scenario_dispersion_review_summary.csv",
            ),
            _source_row(
                "h4_scenario_sensitive_review_summary.csv",
                "OPTIONAL_STATE_SENSITIVE_BASELINE",
                config.h4_state_sensitive_dir / "h4_scenario_sensitive_review_summary.csv",
            ),
            _source_row(
                "h4_transition_scenario_dispersion_review_summary.csv",
                "OPTIONAL_TRANSITION_BASELINE",
                config.h4_transition_dispersion_dir / "h4_transition_scenario_dispersion_review_summary.csv",
            ),
            _source_row(
                "h4_transition_scenario_sensitive_review_summary.csv",
                "OPTIONAL_TRANSITION_SENSITIVE_BASELINE",
                config.h4_transition_sensitive_dir / "h4_transition_scenario_sensitive_review_summary.csv",
            ),
            _source_row(
                "h4_transition_outcome_deep_dive_summary.csv",
                "OPTIONAL_TRANSITION_DEEP_DIVE_BASELINE",
                config.h4_transition_deep_dive_dir / "h4_transition_outcome_deep_dive_summary.csv",
            ),
        ]
    )
    return rows


def load_baseline_dispersion_snapshot(
    config: H4PartialComplementaryDispersionReviewConfig,
) -> BaselineDispersionSnapshot:
    state_summary = _summary_row(config.h4_state_dispersion_dir)
    state_sensitive = _summary_row(config.h4_state_sensitive_dir)
    transition_summary = _summary_row(config.h4_transition_dispersion_dir)
    transition_sensitive = _summary_row(config.h4_transition_sensitive_dir)

    state_profile = _text(
        state_summary,
        [
            "H4_Scenario_Dispersion_Profile",
            "H4_State_Dispersion_Profile",
            "Scenario_Dispersion_Profile",
            "State_Dispersion_Profile",
        ],
    )
    state_flag = _text(
        state_summary,
        [
            "H4_Review_Readiness_Flag",
            "H4_Scenario_Dispersion_Readiness_Flag",
            "H4_State_Readiness_Flag",
            "Readiness_Flag",
        ],
    )
    transition_profile = _text(
        transition_summary,
        [
            "H4_Transition_Scenario_Dispersion_Profile",
            "H4_Transition_Dispersion_Profile",
            "Transition_Dispersion_Profile",
        ],
    )
    transition_flag = _text(
        transition_summary,
        [
            "H4_Review_Readiness_Flag",
            "H4_Transition_Scenario_Dispersion_Readiness_Flag",
            "H4_Transition_Readiness_Flag",
            "Readiness_Flag",
        ],
    )
    sensitive_profile = _text(
        transition_sensitive,
        [
            "H4_Transition_Scenario_Sensitive_Profile",
            "H4_Scenario_Sensitive_Profile",
            "Scenario_Sensitive_Profile",
        ],
    ) or _text(
        state_sensitive,
        [
            "H4_Scenario_Sensitive_Profile",
            "H4_State_Scenario_Sensitive_Profile",
            "Scenario_Sensitive_Profile",
        ],
    )
    high_count = _int(
        transition_sensitive,
        ["High_Sensitivity_Profile_Count", "High_Deviation_Profile_Count"],
    ) or _int(state_sensitive, ["High_Sensitivity_Profile_Count", "High_Deviation_Profile_Count"])
    near_count = _int(
        transition_sensitive,
        ["Near_Aggregation_Candidate_Count", "Near_Candidate_Count"],
    ) or _int(state_sensitive, ["Near_Aggregation_Candidate_Count", "Near_Candidate_Count"])
    return BaselineDispersionSnapshot(
        state_dispersion_profile=state_profile or "BASELINE_UNAVAILABLE",
        state_readiness_flag=state_flag or "BASELINE_UNAVAILABLE",
        transition_dispersion_profile=transition_profile or "BASELINE_UNAVAILABLE",
        transition_readiness_flag=transition_flag or "BASELINE_UNAVAILABLE",
        scenario_sensitive_profile=sensitive_profile or "BASELINE_UNAVAILABLE",
        high_sensitivity_profile_count=high_count,
        near_aggregation_candidate_count=near_count,
    )


def _source_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    frame = read_optional_csv(path)
    status, rows_loaded, diagnostic = source_status(source_name, source_type, path, frame)
    return SourceInventoryRow(
        source_name=source_name,
        source_type=source_type,
        path=str(path),
        exists=path.exists(),
        load_status=status,
        rows_loaded=rows_loaded,
        diagnostic=diagnostic,
    )


def _summary_row(directory: Path):
    for path in sorted(directory.glob("*summary.csv")):
        frame = read_optional_csv(path)
        row = first_row(frame)
        if row is not None:
            return row
    return None


def _text(row, aliases: list[str]) -> str:
    if row is None:
        return ""
    return text_value(row, aliases, "")


def _int(row, aliases: list[str]) -> int:
    if row is None:
        return 0
    return int_value(row, aliases, 0)
