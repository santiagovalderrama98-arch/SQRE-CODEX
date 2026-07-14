"""Deduplication rules for master historical calibration summaries."""

from __future__ import annotations

import pandas as pd

from sqre.master_calibration_summary.loader import resolve_column
from sqre.master_calibration_summary.models import DedupeResult, DuplicateScenarioDetail


def dedupe_summary_frame(frame: pd.DataFrame, *, dedupe_key: str = "Scenario_ID", dedupe_policy: str = "last") -> DedupeResult:
    if dedupe_policy not in {"first", "last", "error"}:
        raise ValueError("dedupe_policy must be one of: first, last, error")

    key_column = resolve_column([str(column) for column in frame.columns], dedupe_key)
    if key_column is None:
        raise ValueError(f"Dedupe key not found: {dedupe_key}")

    working = frame.copy()
    if working.empty:
        return DedupeResult(frame=_add_dedupe_columns(working, key_column, dedupe_policy), rows_loaded=0, rows_retained=0)

    counts = working.groupby(key_column, dropna=False)[key_column].transform("size")
    working["Duplicate_Count_For_Scenario"] = counts.astype(int)
    working["Was_Duplicate"] = working["Duplicate_Count_For_Scenario"] > 1
    working["Dedupe_Policy"] = dedupe_policy

    duplicate_ids = [str(value) for value in working.loc[working["Was_Duplicate"], key_column].drop_duplicates().tolist()]
    if duplicate_ids and dedupe_policy == "error":
        raise ValueError(f"Duplicate Scenario_ID values found: {', '.join(duplicate_ids)}")

    keep = "first" if dedupe_policy == "first" else "last"
    retained = working.drop_duplicates(subset=[key_column], keep=keep).reset_index(drop=True)
    details = _duplicate_details(working, retained, key_column, duplicate_ids)

    return DedupeResult(
        frame=retained,
        rows_loaded=len(working),
        rows_retained=len(retained),
        duplicate_scenario_ids=duplicate_ids,
        duplicate_details=details,
    )


def _add_dedupe_columns(frame: pd.DataFrame, key_column: str, dedupe_policy: str) -> pd.DataFrame:
    output = frame.copy()
    if "Duplicate_Count_For_Scenario" not in output:
        output["Duplicate_Count_For_Scenario"] = pd.Series(dtype="int64")
    if "Was_Duplicate" not in output:
        output["Was_Duplicate"] = pd.Series(dtype="bool")
    if "Dedupe_Policy" not in output:
        output["Dedupe_Policy"] = dedupe_policy
    if key_column not in output:
        output[key_column] = pd.Series(dtype="object")
    return output


def _duplicate_details(
    working: pd.DataFrame,
    retained: pd.DataFrame,
    key_column: str,
    duplicate_ids: list[str],
) -> list[DuplicateScenarioDetail]:
    details: list[DuplicateScenarioDetail] = []
    retained_by_id = {str(row[key_column]): row for _, row in retained.iterrows()}

    for scenario_id in duplicate_ids:
        group = working[working[key_column].astype(str) == scenario_id]
        retained_row = retained_by_id[scenario_id]
        details.append(
            DuplicateScenarioDetail(
                scenario_id=scenario_id,
                duplicate_count=int(group["Duplicate_Count_For_Scenario"].iloc[0]),
                retained_source_file=str(retained_row.get("Source_File", "")),
                retained_source_row_index=int(retained_row.get("Source_Row_Index", 0)),
                source_files=[str(value) for value in group.get("Source_File", pd.Series(dtype="object")).tolist()],
            )
        )

    return details
