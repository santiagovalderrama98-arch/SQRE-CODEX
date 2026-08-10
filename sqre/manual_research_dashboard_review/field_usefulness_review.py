"""Field usefulness review for manual dashboard panels."""

from __future__ import annotations

import pandas as pd

from sqre.manual_research_dashboard_review.panel_completeness_review import PANEL_FRAME_KEYS


FIELD_USEFULNESS_COLUMNS = [
    "Panel_Name",
    "Field_Name",
    "Field_Usefulness_Class",
    "Field_Present",
    "Field_Non_Null_Count",
    "Field_Usefulness_Diagnostic",
]

CORE_FIELDS = {
    "Snapshot_Mode",
    "Snapshot_Source",
    "Research_Reference_Count",
    "Snapshot_Query_Count",
    "Snapshot_Result_Count",
    "Snapshot_Reference_Coverage_Ratio",
    "Primary_Snapshot_Query_Match_Level",
    "Primary_Snapshot_Horizon",
    "Dashboard_Readiness_Class",
    "Dashboard_Readiness_Flag",
    "Matched_Context_Granularity",
    "Matched_Reference_Tier",
    "Matched_Outcome_Sample_Size",
    "Matched_Outcome_Dispersion_Pips",
    "Snapshot_Evidence_Class",
    "Snapshot_Query_Match_Level",
}


def build_field_usefulness_review(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    present_fields: set[str] = set()
    for panel_name, key in PANEL_FRAME_KEYS.items():
        frame = frames.get(key, pd.DataFrame())
        for field_name in frame.columns:
            present_fields.add(field_name)
            records.append(_field_record(panel_name, field_name, True, _non_null_count(frame, field_name)))
    for field_name in sorted(CORE_FIELDS - present_fields):
        records.append(_field_record("Dashboard Core Fields", field_name, False, 0))
    return pd.DataFrame(records, columns=FIELD_USEFULNESS_COLUMNS)


def _field_record(panel_name: str, field_name: str, present: bool, non_null_count: int) -> dict[str, object]:
    field_class = _classify_field(field_name, present)
    diagnostic = _diagnostic(field_name, field_class, present, non_null_count)
    return {
        "Panel_Name": panel_name,
        "Field_Name": field_name,
        "Field_Usefulness_Class": field_class,
        "Field_Present": present,
        "Field_Non_Null_Count": non_null_count,
        "Field_Usefulness_Diagnostic": diagnostic,
    }


def _classify_field(field_name: str, present: bool) -> str:
    if not present:
        return "INPUT_MISSING"
    if field_name in CORE_FIELDS:
        return "CORE_RESEARCH_FIELD"
    if any(token in field_name for token in ["Diagnostic", "Status", "Class", "Flag"]):
        return "DIAGNOSTIC_FIELD"
    if field_name.endswith("_ID") or field_name in {"Reference_Card_ID", "Result_Rank"}:
        return "REDUNDANT_OR_LOW_USE_FIELD"
    return "SUPPORTING_RESEARCH_FIELD"


def _diagnostic(field_name: str, field_class: str, present: bool, non_null_count: int) -> str:
    if not present:
        return f"{field_name} is a core field but is not visible in the dashboard outputs."
    return f"{field_name} classified as {field_class} with {non_null_count} populated values."


def _non_null_count(frame: pd.DataFrame, field_name: str) -> int:
    if field_name not in frame.columns:
        return 0
    return int(frame[field_name].notna().sum())
