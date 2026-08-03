"""Source inventory for H4/D1 same-time alignment."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_same_time_alignment_table.loader import expected_input_paths, read_optional_csv
from sqre.h4_d1_same_time_alignment_table.models import SourceInventoryRow


def build_source_inventory(timestamped_state_regime_dir: Path, synchronized_data_dir: Path) -> list[SourceInventoryRow]:
    rows: list[SourceInventoryRow] = []
    for name, path in expected_input_paths(timestamped_state_regime_dir, synchronized_data_dir).items():
        source_type = "TIMESTAMPED_STATE_REGIME_OUTPUT" if name.startswith("timestamped") else "SYNCHRONIZED_INPUT"
        rows.append(_source_row(name, source_type, path))
    return rows


def _source_row(name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    frame = read_optional_csv(path)
    if frame.empty:
        return SourceInventoryRow(name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
