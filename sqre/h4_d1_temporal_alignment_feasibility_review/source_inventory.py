"""Source inventory for H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.loader import read_optional_csv
from sqre.h4_d1_temporal_alignment_feasibility_review.models import SourceInventoryRow


SourceSpec = tuple[str, str, Path]


def build_source_inventory(config: H4D1TemporalAlignmentFeasibilityConfig) -> list[SourceInventoryRow]:
    return [_source_inventory_row(name, source_type, path) for name, source_type, path in source_specs(config)]


def source_specs(config: H4D1TemporalAlignmentFeasibilityConfig) -> list[SourceSpec]:
    return [
        (
            "h4_transition_state_context_inventory",
            "H4_COMBINED_CONTEXT",
            config.h4_combined_context_dir / "h4_transition_state_context_inventory.csv",
        ),
        (
            "h4_transition_state_context_interpretation_matrix",
            "H4_COMBINED_CONTEXT",
            config.h4_combined_context_dir / "h4_transition_state_context_interpretation_matrix.csv",
        ),
        (
            "h4_combined_context_dispersion_review",
            "H4_COMBINED_CONTEXT",
            config.h4_combined_context_dir / "h4_combined_context_dispersion_review.csv",
        ),
        (
            "h4_combined_context_sensitivity_review",
            "H4_COMBINED_CONTEXT",
            config.h4_combined_context_dir / "h4_combined_context_sensitivity_review.csv",
        ),
        (
            "h4_state_transition_alignment_review",
            "H4_COMBINED_CONTEXT",
            config.h4_combined_context_dir / "h4_state_transition_alignment_review.csv",
        ),
        (
            "h4_transition_state_combined_context_summary",
            "H4_COMBINED_CONTEXT",
            config.h4_combined_context_dir / "h4_transition_state_combined_context_summary.csv",
        ),
        (
            "h4_d1_scenario_inventory",
            "H4_D1_STRUCTURAL_RESEARCH",
            config.h4_d1_structural_research_dir / "h4_d1_scenario_inventory.csv",
        ),
        (
            "h4_d1_timeframe_research_summary",
            "H4_D1_STRUCTURAL_RESEARCH",
            config.h4_d1_structural_research_dir / "h4_d1_timeframe_research_summary.csv",
        ),
        (
            "h4_d1_price_outcome_profiles",
            "H4_D1_STRUCTURAL_RESEARCH",
            config.h4_d1_structural_research_dir / "h4_d1_price_outcome_profiles.csv",
        ),
        (
            "h4_d1_state_research_profiles",
            "H4_D1_STRUCTURAL_RESEARCH",
            config.h4_d1_structural_research_dir / "h4_d1_state_research_profiles.csv",
        ),
        (
            "h4_d1_transition_research_profiles",
            "H4_D1_STRUCTURAL_RESEARCH",
            config.h4_d1_structural_research_dir / "h4_d1_transition_research_profiles.csv",
        ),
        (
            "h4_d1_validation_summary",
            "H4_D1_VALIDATION",
            config.h4_d1_validation_dir / "h4_d1_validation_summary.csv",
        ),
        (
            "d1_regime_research_summary",
            "D1_REGIME_NORMALIZED",
            config.d1_regime_normalized_dir / "d1_regime_research_summary.csv",
        ),
        (
            "d1_regime_scenario_inventory",
            "D1_REGIME_NORMALIZED",
            config.d1_regime_normalized_dir / "d1_regime_scenario_inventory.csv",
        ),
        (
            "d1_regime_condition_outcomes",
            "D1_REGIME_NORMALIZED",
            config.d1_regime_normalized_dir / "d1_regime_condition_outcomes.csv",
        ),
        (
            "d1_regime_state_outcome_profiles",
            "D1_REGIME_NORMALIZED",
            config.d1_regime_normalized_dir / "d1_regime_state_outcome_profiles.csv",
        ),
        (
            "d1_regime_transition_outcome_profiles",
            "D1_REGIME_NORMALIZED",
            config.d1_regime_normalized_dir / "d1_regime_transition_outcome_profiles.csv",
        ),
        (
            "d1_condition_quality_inventory",
            "D1_REGIME_OUTCOME",
            config.d1_regime_outcome_review_dir / "d1_condition_quality_inventory.csv",
        ),
        (
            "d1_regime_outcome_review_summary",
            "D1_REGIME_OUTCOME",
            config.d1_regime_outcome_review_dir / "d1_regime_outcome_review_summary.csv",
        ),
        (
            "d1_state_deep_dive_profile_inventory",
            "D1_STATE_DEEP_DIVE",
            config.d1_state_deep_dive_dir / "d1_state_deep_dive_profile_inventory.csv",
        ),
        (
            "d1_state_regime_breakdown",
            "D1_STATE_DEEP_DIVE",
            config.d1_state_deep_dive_dir / "d1_state_regime_breakdown.csv",
        ),
        (
            "d1_state_regime_comparison_matrix",
            "D1_STATE_DEEP_DIVE",
            config.d1_state_deep_dive_dir / "d1_state_regime_comparison_matrix.csv",
        ),
    ]


def _source_inventory_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    frame = read_optional_csv(path)
    if not path.exists():
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    if frame.empty:
        return SourceInventoryRow(source_name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(source_name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
