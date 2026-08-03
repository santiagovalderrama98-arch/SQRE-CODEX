"""Source inventory for H4 timestamped state/transition output generation."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.loader import (
    SCENARIO_ALIASES,
    SOURCE_STATE_ALIASES,
    STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TIMESTAMP_ALIASES,
    TRANSITION_ALIASES,
    joined,
    read_optional_csv,
    resolve_columns,
)
from sqre.h4_timestamped_state_transition_outputs.models import SourceInventoryRow
from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import TIMESTAMPED_FILE_NAMES


SourceSpec = tuple[str, str, Path]


def source_specs(config: H4TimestampedStateTransitionConfig) -> list[SourceSpec]:
    specs = [
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
    specs.extend(_recursive_specs(config.h4_d1_validation_dir, "H4_TIMESTAMPED_VALIDATION_DISCOVERY"))
    specs.extend(_recursive_specs(config.h4_d1_structural_research_dir, "H4_TIMESTAMPED_RESEARCH_DISCOVERY"))
    return specs


def build_source_inventory(config: H4TimestampedStateTransitionConfig) -> list[SourceInventoryRow]:
    return [_source_inventory_row(name, source_type, path) for name, source_type, path in source_specs(config)]


def _recursive_specs(root: Path, source_type: str) -> list[SourceSpec]:
    if not root.exists():
        return []
    names = {name.lower() for name in TIMESTAMPED_FILE_NAMES}
    specs: list[SourceSpec] = []
    for path in sorted(root.rglob("*.csv")):
        if path.name.lower() not in names:
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
    state_columns = resolve_columns(frame, SOURCE_STATE_ALIASES + TARGET_STATE_ALIASES + STATE_ALIASES)
    transition_columns = resolve_columns(frame, TRANSITION_ALIASES)
    status = "EMPTY" if frame.empty else "LOADED"
    source_kind = _source_kind(source_type, path, state_columns)
    diagnostic = "Source file has no data rows." if frame.empty else "Source file loaded."
    return SourceInventoryRow(
        source_name,
        source_kind,
        str(path),
        True,
        status,
        len(frame),
        joined(timestamp_columns),
        joined(scenario_columns),
        joined(state_columns),
        joined(transition_columns),
        diagnostic,
    )


def _source_kind(source_type: str, path: Path, state_columns: list[str]) -> str:
    if "TIMESTAMPED" not in source_type:
        return source_type
    lowered = path.name.lower()
    source_names = {item.lower() for item in SOURCE_STATE_ALIASES}
    target_names = {item.lower() for item in TARGET_STATE_ALIASES}
    has_pair = any(col.lower() in source_names for col in state_columns) and any(
        col.lower() in target_names for col in state_columns
    )
    if "transition" in lowered or has_pair:
        return "H4_TIMESTAMPED_TRANSITION_SOURCE"
    return "H4_TIMESTAMPED_STATE_SOURCE"
