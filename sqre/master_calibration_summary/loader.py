"""Load validation summary CSV files for master calibration review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.master_calibration_summary.models import LoadedSummaryFrame, REQUIRED_COLUMNS


def load_summary_csv(path: Path | str) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Validation summary CSV not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    frame = _canonicalize_required_columns(frame, csv_path)
    frame["Source_File"] = str(csv_path)
    frame["Source_Row_Index"] = list(range(len(frame)))
    return frame


def load_summary_csvs(paths: list[Path | str], *, allow_missing_inputs: bool = False) -> LoadedSummaryFrame:
    requested = [str(Path(path)) for path in paths]
    found: list[str] = []
    missing: list[str] = []
    frames: list[pd.DataFrame] = []

    for path in paths:
        csv_path = Path(path)
        if not csv_path.exists():
            if not allow_missing_inputs:
                raise FileNotFoundError(f"Validation summary CSV not found: {csv_path}")
            missing.append(str(csv_path))
            continue

        frames.append(load_summary_csv(csv_path))
        found.append(str(csv_path))

    if frames:
        combined = pd.concat(frames, ignore_index=True, sort=False)
    else:
        combined = pd.DataFrame(columns=[*REQUIRED_COLUMNS, "Source_File", "Source_Row_Index"])

    return LoadedSummaryFrame(
        frame=combined,
        requested_files=requested,
        found_files=found,
        missing_files=missing,
        rows_loaded=len(combined),
    )


def resolve_column(columns: list[str], target: str) -> str | None:
    lookup = {_normalize(column): column for column in columns}
    return lookup.get(_normalize(target))


def _canonicalize_required_columns(frame: pd.DataFrame, source_path: Path) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    missing: list[str] = []
    columns = [str(column) for column in frame.columns]

    for required in REQUIRED_COLUMNS:
        actual = resolve_column(columns, required)
        if actual is None:
            missing.append(required)
        elif actual != required:
            rename_map[actual] = required

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required columns in {source_path}: {missing_text}")

    return frame.rename(columns=rename_map)


def _normalize(column: object) -> str:
    return "".join(character for character in str(column).strip().lower() if character.isalnum())
