"""Inspect local H4 raw and partial files without modifying them."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.models import RawFileInventoryRow


def inspect_h4_raw_files(raw_data_dir: Path | str, partial_data_dir: Path | str) -> list[RawFileInventoryRow]:
    rows: list[RawFileInventoryRow] = []
    for path in sorted(Path(raw_data_dir).glob("EURUSD_H4*.csv")):
        rows.append(inspect_raw_file(path, partial_file_flag="NO"))
    partial_root = Path(partial_data_dir)
    if partial_root.exists():
        for path in sorted(partial_root.glob("EURUSD_H4*.csv")):
            rows.append(inspect_raw_file(path, partial_file_flag="YES"))
    return rows


def inspect_raw_file(path: Path | str, partial_file_flag: str = "NO") -> RawFileInventoryRow:
    resolved = Path(path)
    symbol, timeframe = _parse_symbol_timeframe(resolved.name)
    try:
        frame = pd.read_csv(resolved)
    except Exception as exc:
        return RawFileInventoryRow(
            str(resolved),
            resolved.name,
            partial_file_flag,
            symbol,
            timeframe,
            0,
            "",
            "",
            "UNKNOWN",
            f"H4 raw file could not be read: {exc}",
        )
    if "Date" not in frame.columns:
        return RawFileInventoryRow(
            str(resolved),
            resolved.name,
            partial_file_flag,
            symbol,
            timeframe,
            len(frame),
            "",
            "",
            "UNKNOWN",
            "H4 raw file exists but Date coverage is unknown",
        )
    dates = pd.to_datetime(frame["Date"], errors="coerce").dropna()
    if dates.empty:
        return RawFileInventoryRow(
            str(resolved),
            resolved.name,
            partial_file_flag,
            symbol,
            timeframe,
            len(frame),
            "",
            "",
            "UNKNOWN",
            "H4 raw file Date values could not be parsed",
        )
    return RawFileInventoryRow(
        str(resolved),
        resolved.name,
        partial_file_flag,
        symbol,
        timeframe,
        len(frame),
        dates.min().date().isoformat(),
        dates.max().date().isoformat(),
        "KNOWN",
        "H4 raw file date coverage was inspected",
    )


def scenario_id_from_raw_file(row: RawFileInventoryRow) -> str:
    name = Path(row.file_name).stem.lower()
    if name.startswith("eurusd_h4"):
        return name.replace("eurusd_h4", "eurusd_h4")
    return name


def _parse_symbol_timeframe(file_name: str) -> tuple[str, str]:
    parts = Path(file_name).stem.split("_")
    symbol = parts[0] if parts else "EURUSD"
    timeframe = parts[1] if len(parts) > 1 else "H4"
    return symbol.upper(), timeframe.upper()
