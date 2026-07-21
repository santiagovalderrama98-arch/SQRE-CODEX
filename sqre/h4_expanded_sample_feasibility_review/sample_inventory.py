"""Build H4 sample inventory from configs and known outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqre.h4_expanded_sample_feasibility_review.models import DefinedSampleRow


def extract_h4_samples_from_config(data: dict[str, Any], source_config: Path | str) -> list[DefinedSampleRow]:
    source = str(source_config)
    rows: list[DefinedSampleRow] = []
    for item in _entries(data):
        if str(item.get("timeframe", "")).upper() != "H4":
            continue
        scenario_id = str(item.get("sample_id") or item.get("scenario_id") or item.get("name") or "")
        symbol = str(item.get("symbol") or data.get("symbol") or "EURUSD")
        start = str(item.get("start") or item.get("start_date") or item.get("expected_start") or "")
        end = str(item.get("end") or item.get("end_date") or item.get("expected_end") or "")
        raw_hint = str(item.get("output_path") or item.get("ohlc_path") or "")
        status = "DEFINED" if scenario_id else "DEFINED_WITH_MISSING_ID"
        if not start or not end:
            status = "DEFINED_WITH_UNKNOWN_DATES"
        rows.append(
            DefinedSampleRow(
                scenario_id=scenario_id or _scenario_from_path(raw_hint),
                symbol=symbol,
                timeframe="H4",
                defined_start_date=start,
                defined_end_date=end,
                source_config=source,
                sample_definition_status=status,
                sample_definition_diagnostic=_definition_diagnostic(status),
                raw_file_hint=raw_hint,
            )
        )
    return rows


def merge_defined_samples(sample_groups: list[list[DefinedSampleRow]]) -> list[DefinedSampleRow]:
    merged: dict[str, DefinedSampleRow] = {}
    for group in sample_groups:
        for row in group:
            key = row.scenario_id or row.raw_file_hint or f"{row.source_config}:{row.defined_start_date}:{row.defined_end_date}"
            existing = merged.get(key)
            if existing is None or _score(row) > _score(existing):
                merged[key] = row
    return sorted(merged.values(), key=lambda row: row.scenario_id)


def _entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ("samples", "scenarios"):
        values = data.get(key, [])
        if isinstance(values, list):
            rows.extend(value for value in values if isinstance(value, dict))
    return rows


def _score(row: DefinedSampleRow) -> int:
    return sum(1 for value in (row.defined_start_date, row.defined_end_date, row.raw_file_hint) if value)


def _scenario_from_path(raw_hint: str) -> str:
    if not raw_hint:
        return ""
    stem = Path(raw_hint).stem.lower()
    return stem.replace("eurusd_h4_", "eurusd_h4_")


def _definition_diagnostic(status: str) -> str:
    return {
        "DEFINED": "H4 sample definition includes expected date boundaries",
        "DEFINED_WITH_MISSING_ID": "H4 sample definition is missing a scenario identifier",
        "DEFINED_WITH_UNKNOWN_DATES": "H4 sample definition has incomplete date boundaries",
    }.get(status, "H4 sample definition requires review")
