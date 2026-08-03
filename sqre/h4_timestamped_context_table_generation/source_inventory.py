"""Source inventory for H4 timestamped context table generation."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.loader import (
    SCENARIO_ALIASES,
    SINGLE_STATE_ALIASES,
    SOURCE_STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TIMESTAMP_ALIASES,
    TRANSITION_ALIASES,
    joined,
    read_optional_csv,
    resolve_columns,
)
from sqre.h4_timestamped_context_table_generation.models import SourceInventoryRow
from sqre.h4_timestamped_context_table_generation.timestamped_source_discovery import TIMESTAMPED_FILE_NAMES


SourceSpec = tuple[str, str, Path]


def source_specs(config: H4TimestampedContextTableGenerationConfig) -> list[SourceSpec]:
    specs = [
        (
            "h4_transition_state_context_inventory",
            "H4_AGGREGATE_CONTEXT",
            config.h4_combined_context_dir / "h4_transition_state_context_inventory.csv",
        ),
        (
            "h4_transition_state_context_interpretation_matrix",
            "H4_AGGREGATE_CONTEXT",
            config.h4_combined_context_dir / "h4_transition_state_context_interpretation_matrix.csv",
        ),
        (
            "h4_combined_context_dispersion_review",
            "H4_AGGREGATE_CONTEXT",
            config.h4_combined_context_dir / "h4_combined_context_dispersion_review.csv",
        ),
        (
            "h4_combined_context_sensitivity_review",
            "H4_AGGREGATE_CONTEXT",
            config.h4_combined_context_dir / "h4_combined_context_sensitivity_review.csv",
        ),
        (
            "h4_state_transition_alignment_review",
            "H4_AGGREGATE_CONTEXT",
            config.h4_combined_context_dir / "h4_state_transition_alignment_review.csv",
        ),
        (
            "h4_transition_state_combined_context_summary",
            "H4_AGGREGATE_CONTEXT",
            config.h4_combined_context_dir / "h4_transition_state_combined_context_summary.csv",
        ),
        (
            "h4_d1_validation_summary",
            "H4_VALIDATION",
            config.h4_d1_validation_dir / "h4_d1_validation_summary.csv",
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
    ]
    specs.extend(_recursive_timestamped_specs(config.h4_d1_validation_dir, "H4_TIMESTAMPED_VALIDATION_DISCOVERY"))
    specs.extend(_recursive_timestamped_specs(config.h4_d1_structural_research_dir, "H4_TIMESTAMPED_RESEARCH_DISCOVERY"))
    return specs


def build_source_inventory(config: H4TimestampedContextTableGenerationConfig) -> list[SourceInventoryRow]:
    return [_source_inventory_row(name, source_type, path) for name, source_type, path in source_specs(config)]


def _recursive_timestamped_specs(root: Path, source_type: str) -> list[SourceSpec]:
    if not root.exists():
        return []
    specs: list[SourceSpec] = []
    candidates = {name.lower() for name in TIMESTAMPED_FILE_NAMES}
    for path in sorted(root.rglob("*.csv")):
        if path.name.lower() not in candidates:
            continue
        source_name = path.stem
        try:
            source_name = str(path.relative_to(root)).replace("/", "__").removesuffix(".csv")
        except ValueError:
            pass
        specs.append((source_name, source_type, path))
    return specs


def _source_inventory_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    frame = read_optional_csv(path)
    if not path.exists():
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "", "", "", "", "Source file was not found.")
    timestamp_columns = resolve_columns(frame, TIMESTAMP_ALIASES)
    scenario_columns = resolve_columns(frame, SCENARIO_ALIASES)
    state_columns = resolve_columns(frame, SOURCE_STATE_ALIASES + TARGET_STATE_ALIASES + SINGLE_STATE_ALIASES)
    transition_columns = resolve_columns(frame, TRANSITION_ALIASES)
    if frame.empty:
        status, rows, diagnostic = "EMPTY", 0, "Source file has no data rows."
    else:
        status, rows, diagnostic = "LOADED", len(frame), "Source file loaded."
    resolved_source_type = _timestamped_source_type(source_type, path, state_columns)
    return SourceInventoryRow(
        source_name,
        resolved_source_type,
        str(path),
        True,
        status,
        rows,
        joined(timestamp_columns),
        joined(scenario_columns),
        joined(state_columns),
        joined(transition_columns),
        diagnostic,
    )


def _timestamped_source_type(source_type: str, path: Path, state_columns: list[str]) -> str:
    if "TIMESTAMPED" not in source_type:
        return source_type
    name = path.name.lower()
    has_state_pair = any(column in state_columns for column in resolve_state_pair_columns(state_columns))
    if "transition" in name or has_state_pair:
        return "H4_TIMESTAMPED_TRANSITION_SOURCE"
    return "H4_TIMESTAMPED_STATE_SOURCE"


def resolve_state_pair_columns(state_columns: list[str]) -> list[str]:
    source_names = {name.lower() for name in SOURCE_STATE_ALIASES}
    target_names = {name.lower() for name in TARGET_STATE_ALIASES}
    has_source = any(column.lower() in source_names for column in state_columns)
    has_target = any(column.lower() in target_names for column in state_columns)
    return state_columns if has_source and has_target else []
