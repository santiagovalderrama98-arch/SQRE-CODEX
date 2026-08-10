"""Source inventory for reference stability validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.loader import (
    OPTIONAL_DASHBOARD_INPUTS,
    OPTIONAL_MANUAL_REVIEW_INPUTS,
    OPTIONAL_SNAPSHOT_INPUTS,
    REQUIRED_QUERY_INTERFACE_INPUTS,
    REQUIRED_REFERENCE_STORE_INPUTS,
)
from sqre.reference_stability_validation.models import ReferenceStabilitySourceInventoryRow


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]


def build_source_inventory(config: ReferenceStabilityValidationConfig) -> list[ReferenceStabilitySourceInventoryRow]:
    rows: list[ReferenceStabilitySourceInventoryRow] = []
    rows.extend(_csv_rows(config.reference_store_dir, REQUIRED_REFERENCE_STORE_INPUTS, "REQUIRED_REFERENCE_STORE_INPUT"))
    rows.extend(_csv_rows(config.query_interface_dir, REQUIRED_QUERY_INTERFACE_INPUTS, "REQUIRED_QUERY_INTERFACE_INPUT"))
    rows.extend(_csv_rows(config.snapshot_research_dir, OPTIONAL_SNAPSHOT_INPUTS, "OPTIONAL_SNAPSHOT_RESEARCH_INPUT"))
    rows.extend(_csv_rows(config.dashboard_dir, OPTIONAL_DASHBOARD_INPUTS, "OPTIONAL_DASHBOARD_INPUT"))
    rows.extend(_csv_rows(config.manual_dashboard_review_dir, OPTIONAL_MANUAL_REVIEW_INPUTS, "OPTIONAL_MANUAL_REVIEW_INPUT"))
    return rows


def has_missing_required_inputs(rows: list[ReferenceStabilitySourceInventoryRow]) -> bool:
    return any(
        row.source_type in {"REQUIRED_REFERENCE_STORE_INPUT", "REQUIRED_QUERY_INTERFACE_INPUT"}
        and row.load_status in {"REQUIRED_INPUT_MISSING", "INPUT_MISSING"}
        for row in rows
    )


def _csv_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[ReferenceStabilitySourceInventoryRow]:
    return [_csv_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _csv_row(source_name: str, source_type: str, path: Path) -> ReferenceStabilitySourceInventoryRow:
    required = source_type in {"REQUIRED_REFERENCE_STORE_INPUT", "REQUIRED_QUERY_INTERFACE_INPUT"}
    if not path.exists():
        status = "REQUIRED_INPUT_MISSING" if required else "OPTIONAL_INPUT_MISSING"
        return ReferenceStabilitySourceInventoryRow(
            source_name,
            source_type,
            str(path),
            False,
            status,
            0,
            f"{path.name} is missing.",
        )
    try:
        rows_loaded = len(pd.read_csv(path))
    except pd.errors.EmptyDataError:
        return ReferenceStabilitySourceInventoryRow(
            source_name,
            source_type,
            str(path),
            True,
            "EMPTY_INPUT",
            0,
            f"{path.name} is empty.",
        )
    status = "LOADED" if rows_loaded > 0 else "EMPTY_INPUT"
    diagnostic = f"{path.name} loaded." if rows_loaded else f"{path.name} has no data rows."
    return ReferenceStabilitySourceInventoryRow(source_name, source_type, str(path), True, status, rows_loaded, diagnostic)
