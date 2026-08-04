"""Source inventory for Research Reference Store Usage Review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.loader import ALIGNMENT_FILES, INTERPRETATION_FILES, REFERENCE_STORE_FILES
from sqre.research_reference_store_usage_review.models import SourceInventoryRow


def build_source_inventory(config: ResearchReferenceStoreUsageReviewConfig) -> list[SourceInventoryRow]:
    rows = []
    for source_name, filename in REFERENCE_STORE_FILES.items():
        rows.append(_inventory_row(source_name, "REQUIRED_INPUT", config.reference_store_dir / filename))
    for source_name, filename in INTERPRETATION_FILES.items():
        rows.append(_inventory_row(source_name, "OPTIONAL_DIAGNOSTIC_INPUT", config.interpretation_dir / filename))
    for source_name, filename in ALIGNMENT_FILES.items():
        rows.append(_inventory_row(source_name, "OPTIONAL_SCENARIO_INPUT", config.same_time_alignment_dir / filename))
    return rows


def _inventory_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "Source file is missing.")
    try:
        rows_loaded = len(pd.read_csv(path))
    except pd.errors.EmptyDataError:
        rows_loaded = 0
    status = "LOADED" if rows_loaded > 0 else "EMPTY"
    diagnostic = f"Loaded {rows_loaded} rows." if rows_loaded > 0 else "Source file has no data rows."
    return SourceInventoryRow(source_name, source_type, str(path), True, status, rows_loaded, diagnostic)
