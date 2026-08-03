"""Source inventory for timestamped H4/D1 state and regime generation."""

from __future__ import annotations

from pathlib import Path

from sqre.timestamped_h4_d1_state_regime_generation.loader import expected_input_paths, read_optional_csv
from sqre.timestamped_h4_d1_state_regime_generation.models import SourceInventoryRow


def build_source_inventory(synchronized_data_dir: Path) -> list[SourceInventoryRow]:
    rows: list[SourceInventoryRow] = []
    for name, path in expected_input_paths(synchronized_data_dir).items():
        rows.append(_source_row(name, "SYNCHRONIZED_INPUT", path))
    return rows


def _source_row(name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    frame = read_optional_csv(path)
    if frame.empty:
        return SourceInventoryRow(name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
