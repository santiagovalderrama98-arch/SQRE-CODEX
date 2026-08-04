"""Source inventory for Research Reference Store Design."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.loader import OPTIONAL_FILES, REQUIRED_FILES
from sqre.research_reference_store_design.models import SourceInventoryRow


def build_source_inventory(config: ResearchReferenceStoreDesignConfig) -> list[SourceInventoryRow]:
    rows = []
    for source_name, filename in REQUIRED_FILES.items():
        rows.append(_inventory_row(source_name, "REQUIRED_INPUT", config.interpretation_dir / filename))
    for source_name, filename in OPTIONAL_FILES.items():
        rows.append(_inventory_row(source_name, "OPTIONAL_DIAGNOSTIC_INPUT", config.forward_outcome_dir / filename))
    return rows


def _inventory_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    exists = path.exists()
    rows_loaded = 0
    if not exists:
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "Source file is missing.")
    try:
        rows_loaded = len(pd.read_csv(path))
    except pd.errors.EmptyDataError:
        rows_loaded = 0
    status = "LOADED" if rows_loaded > 0 else "EMPTY"
    diagnostic = f"Loaded {rows_loaded} rows." if rows_loaded > 0 else "Source file has no data rows."
    return SourceInventoryRow(source_name, source_type, str(path), exists, status, rows_loaded, diagnostic)
