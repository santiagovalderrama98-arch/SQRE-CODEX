"""Source inventory for reference stability documentation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.loader import (
    OPTIONAL_DASHBOARD_INPUTS,
    OPTIONAL_DASHBOARD_TEXTS,
    OPTIONAL_MANUAL_DASHBOARD_INPUTS,
    OPTIONAL_MANUAL_DASHBOARD_TEXTS,
    REQUIRED_STABILITY_VALIDATION_INPUTS,
    REQUIRED_STABILITY_VALIDATION_TEXTS,
)
from sqre.reference_stability_documentation.models import ReferenceStabilityDocumentationSourceRow


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]


def build_source_inventory(
    config: ReferenceStabilityDocumentationConfig,
) -> list[ReferenceStabilityDocumentationSourceRow]:
    rows: list[ReferenceStabilityDocumentationSourceRow] = []
    rows.extend(_csv_rows(config.stability_validation_dir, REQUIRED_STABILITY_VALIDATION_INPUTS, "REQUIRED_STABILITY_VALIDATION_INPUT"))
    rows.extend(_text_rows(config.stability_validation_dir, REQUIRED_STABILITY_VALIDATION_TEXTS, "REQUIRED_STABILITY_VALIDATION_INPUT"))
    rows.extend(_csv_rows(config.dashboard_dir, OPTIONAL_DASHBOARD_INPUTS, "OPTIONAL_DASHBOARD_INPUT"))
    rows.extend(_text_rows(config.dashboard_dir, OPTIONAL_DASHBOARD_TEXTS, "OPTIONAL_DASHBOARD_INPUT"))
    rows.extend(_csv_rows(config.manual_dashboard_review_dir, OPTIONAL_MANUAL_DASHBOARD_INPUTS, "OPTIONAL_MANUAL_DASHBOARD_INPUT"))
    rows.extend(_text_rows(config.manual_dashboard_review_dir, OPTIONAL_MANUAL_DASHBOARD_TEXTS, "OPTIONAL_MANUAL_DASHBOARD_INPUT"))
    return rows


def has_missing_required_inputs(rows: list[ReferenceStabilityDocumentationSourceRow]) -> bool:
    return any(
        row.source_type == "REQUIRED_STABILITY_VALIDATION_INPUT"
        and row.load_status in {"REQUIRED_INPUT_MISSING", "INPUT_MISSING", "EMPTY_INPUT"}
        for row in rows
    )


def _csv_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[ReferenceStabilityDocumentationSourceRow]:
    return [_csv_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _text_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[ReferenceStabilityDocumentationSourceRow]:
    return [_text_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _csv_row(source_name: str, source_type: str, path: Path) -> ReferenceStabilityDocumentationSourceRow:
    required = source_type == "REQUIRED_STABILITY_VALIDATION_INPUT"
    if not path.exists():
        status = "REQUIRED_INPUT_MISSING" if required else "OPTIONAL_INPUT_MISSING"
        return ReferenceStabilityDocumentationSourceRow(source_name, source_type, str(path), False, status, 0, f"{path.name} is missing.")
    try:
        rows_loaded = len(pd.read_csv(path))
    except pd.errors.EmptyDataError:
        return ReferenceStabilityDocumentationSourceRow(source_name, source_type, str(path), True, "EMPTY_INPUT", 0, f"{path.name} is empty.")
    status = "LOADED" if rows_loaded > 0 else "EMPTY_INPUT"
    diagnostic = f"{path.name} loaded." if rows_loaded else f"{path.name} has no data rows."
    return ReferenceStabilityDocumentationSourceRow(source_name, source_type, str(path), True, status, rows_loaded, diagnostic)


def _text_row(source_name: str, source_type: str, path: Path) -> ReferenceStabilityDocumentationSourceRow:
    required = source_type == "REQUIRED_STABILITY_VALIDATION_INPUT"
    if not path.exists():
        status = "REQUIRED_INPUT_MISSING" if required else "OPTIONAL_INPUT_MISSING"
        return ReferenceStabilityDocumentationSourceRow(source_name, source_type, str(path), False, status, 0, f"{path.name} is missing.")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return ReferenceStabilityDocumentationSourceRow(source_name, source_type, str(path), True, "EMPTY_INPUT", 0, f"{path.name} is empty.")
    return ReferenceStabilityDocumentationSourceRow(source_name, source_type, str(path), True, "LOADED", len(text.splitlines()), f"{path.name} loaded.")
