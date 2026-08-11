"""Source inventory for dashboard stability indicators."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.loader import (
    OPTIONAL_MANUAL_REVIEW_INPUTS,
    OPTIONAL_MANUAL_REVIEW_TEXTS,
    REQUIRED_DASHBOARD_INPUTS,
    REQUIRED_DASHBOARD_TEXTS,
    REQUIRED_DOCUMENTATION_INPUTS,
    REQUIRED_DOCUMENTATION_TEXTS,
    REQUIRED_VALIDATION_INPUTS,
)
from sqre.dashboard_stability_indicators.models import DashboardStabilitySourceRow


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]


def build_source_inventory(config: DashboardStabilityIndicatorsConfig) -> list[DashboardStabilitySourceRow]:
    rows: list[DashboardStabilitySourceRow] = []
    rows.extend(_csv_rows(config.stability_documentation_dir, REQUIRED_DOCUMENTATION_INPUTS, "REQUIRED_DOCUMENTATION_INPUT"))
    rows.extend(_text_rows(config.stability_documentation_dir, REQUIRED_DOCUMENTATION_TEXTS, "REQUIRED_DOCUMENTATION_INPUT"))
    rows.extend(_csv_rows(config.stability_validation_dir, REQUIRED_VALIDATION_INPUTS, "REQUIRED_VALIDATION_INPUT"))
    rows.extend(_csv_rows(config.dashboard_dir, REQUIRED_DASHBOARD_INPUTS, "REQUIRED_DASHBOARD_INPUT"))
    rows.extend(_text_rows(config.dashboard_dir, REQUIRED_DASHBOARD_TEXTS, "REQUIRED_DASHBOARD_INPUT"))
    rows.extend(_csv_rows(config.manual_dashboard_review_dir, OPTIONAL_MANUAL_REVIEW_INPUTS, "OPTIONAL_MANUAL_REVIEW_INPUT"))
    rows.extend(_text_rows(config.manual_dashboard_review_dir, OPTIONAL_MANUAL_REVIEW_TEXTS, "OPTIONAL_MANUAL_REVIEW_INPUT"))
    return rows


def has_missing_required_inputs(rows: list[DashboardStabilitySourceRow]) -> bool:
    return any(
        row.source_type.startswith("REQUIRED_")
        and row.load_status in {"REQUIRED_INPUT_MISSING", "INPUT_MISSING", "EMPTY_INPUT"}
        for row in rows
    )


def _csv_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[DashboardStabilitySourceRow]:
    return [_csv_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _text_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[DashboardStabilitySourceRow]:
    return [_text_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _csv_row(source_name: str, source_type: str, path: Path) -> DashboardStabilitySourceRow:
    required = source_type.startswith("REQUIRED_")
    if not path.exists():
        status = "REQUIRED_INPUT_MISSING" if required else "OPTIONAL_INPUT_MISSING"
        return DashboardStabilitySourceRow(source_name, source_type, str(path), False, status, 0, f"{path.name} is missing.")
    try:
        rows_loaded = len(pd.read_csv(path))
    except pd.errors.EmptyDataError:
        return DashboardStabilitySourceRow(source_name, source_type, str(path), True, "EMPTY_INPUT", 0, f"{path.name} is empty.")
    status = "LOADED" if rows_loaded > 0 else "EMPTY_INPUT"
    diagnostic = f"{path.name} loaded." if rows_loaded else f"{path.name} has no data rows."
    return DashboardStabilitySourceRow(source_name, source_type, str(path), True, status, rows_loaded, diagnostic)


def _text_row(source_name: str, source_type: str, path: Path) -> DashboardStabilitySourceRow:
    required = source_type.startswith("REQUIRED_")
    if not path.exists():
        status = "REQUIRED_INPUT_MISSING" if required else "OPTIONAL_INPUT_MISSING"
        return DashboardStabilitySourceRow(source_name, source_type, str(path), False, status, 0, f"{path.name} is missing.")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return DashboardStabilitySourceRow(source_name, source_type, str(path), True, "EMPTY_INPUT", 0, f"{path.name} is empty.")
    return DashboardStabilitySourceRow(source_name, source_type, str(path), True, "LOADED", len(text.splitlines()), f"{path.name} loaded.")
