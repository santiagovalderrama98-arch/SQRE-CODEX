"""Safe loaders for H4 expanded sample feasibility review."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.models import SourceInventoryRow


def load_csv_source(path: Path | str, source_name: str, source_type: str) -> tuple[pd.DataFrame, SourceInventoryRow]:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame(), SourceInventoryRow(
            source_name,
            source_type,
            str(resolved),
            "NO",
            "missing_optional",
            diagnostic="Optional source was not present.",
        )
    try:
        frame = pd.read_csv(resolved)
    except Exception as exc:
        return pd.DataFrame(), SourceInventoryRow(
            source_name,
            source_type,
            str(resolved),
            "YES",
            "read_error",
            diagnostic=f"Source could not be read: {exc}",
        )
    h4_rows = _h4_rows(frame)
    status = "present_empty" if frame.empty else "present_loaded"
    return frame, SourceInventoryRow(
        source_name,
        source_type,
        str(resolved),
        "YES",
        status,
        rows_loaded=len(frame),
        h4_rows_loaded=h4_rows,
        diagnostic="Source loaded." if not frame.empty else "Source exists but contains no data rows.",
    )


def load_yaml_source(path: Path | str, source_name: str) -> tuple[dict[str, Any], SourceInventoryRow]:
    resolved = Path(path)
    if not resolved.exists():
        return {}, SourceInventoryRow(
            source_name,
            "yaml_config",
            str(resolved),
            "NO",
            "missing_optional",
            diagnostic="Optional config was not present.",
        )
    try:
        data = _load_yaml(resolved)
    except Exception as exc:
        return {}, SourceInventoryRow(
            source_name,
            "yaml_config",
            str(resolved),
            "YES",
            "read_error",
            diagnostic=f"Config could not be read: {exc}",
        )
    rows = _config_entries(data)
    h4_rows = sum(1 for row in rows if str(row.get("timeframe", "")).upper() == "H4")
    return data, SourceInventoryRow(
        source_name,
        "yaml_config",
        str(resolved),
        "YES",
        "present_loaded" if rows else "present_empty",
        rows_loaded=len(rows),
        h4_rows_loaded=h4_rows,
        diagnostic="Config loaded." if rows else "Config exists but contains no sample rows.",
    )


def value(row: pd.Series, *columns: str, default: Any = "") -> Any:
    for column in columns:
        actual = _resolve_index(row, column)
        if actual is None:
            continue
        item = row[actual]
        if pd.isna(item):
            return default
        return item
    return default


def text_value(row: pd.Series, *columns: str, default: str = "") -> str:
    item = value(row, *columns, default=default)
    return default if item is None else str(item)


def number_value(row: pd.Series, *columns: str, default: float = 0.0) -> float:
    item = value(row, *columns, default=default)
    try:
        return float(item)
    except (TypeError, ValueError):
        return default


def integer_value(row: pd.Series, *columns: str, default: int = 0) -> int:
    return int(number_value(row, *columns, default=float(default)))


def _load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}
    except ImportError:
        return _fallback_yaml_parse(text)


def _fallback_yaml_parse(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list: str | None = None
    current_item: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw_line.startswith(" ") and stripped.endswith(":"):
            current_list = stripped[:-1]
            data[current_list] = []
            current_item = None
            continue
        if stripped.startswith("- "):
            if current_list is None:
                continue
            current_item = {}
            data.setdefault(current_list, []).append(current_item)
            stripped = stripped[2:]
        if ":" in stripped:
            key, value_text = stripped.split(":", 1)
            parsed = _parse_scalar(value_text.strip())
            if current_item is not None:
                current_item[key.strip()] = parsed
            else:
                data[key.strip()] = parsed
    return data


def _parse_scalar(value_text: str) -> Any:
    clean = value_text.strip().strip("'\"")
    if clean.startswith("[") and clean.endswith("]"):
        return [item.strip().strip("'\"") for item in clean[1:-1].split(",") if item.strip()]
    return clean


def _config_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for key in ("samples", "scenarios"):
        value_list = data.get(key, [])
        if isinstance(value_list, list):
            entries.extend(item for item in value_list if isinstance(item, dict))
    return entries


def _h4_rows(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    lookup = {_normalize(column): column for column in frame.columns}
    timeframe_column = lookup.get("timeframe")
    if timeframe_column is None:
        return 0
    return int((frame[timeframe_column].astype(str).str.upper() == "H4").sum())


def _resolve_index(row: pd.Series, target: str) -> str | None:
    lookup = {_normalize(column): str(column) for column in row.index}
    return lookup.get(_normalize(target))


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
