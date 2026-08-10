"""Redundancy review for manual research dashboard fields."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from sqre.manual_research_dashboard_review.panel_completeness_review import PANEL_FRAME_KEYS


REDUNDANCY_REVIEW_COLUMNS = [
    "Panel_Name",
    "Field_Name",
    "Potential_Redundancy_Class",
    "Redundancy_Group",
    "Redundancy_Diagnostic",
]


def build_redundancy_review(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    field_counts = Counter(field for key in PANEL_FRAME_KEYS.values() for field in frames.get(key, pd.DataFrame()).columns)
    records = []
    for panel_name, key in PANEL_FRAME_KEYS.items():
        frame = frames.get(key, pd.DataFrame())
        for field_name in frame.columns:
            records.append(_record(panel_name, field_name, field_counts[field_name]))
    if not records:
        records.append(
            {
                "Panel_Name": "Dashboard Panels",
                "Field_Name": "INPUT_MISSING",
                "Potential_Redundancy_Class": "INPUT_MISSING",
                "Redundancy_Group": "INPUT_MISSING",
                "Redundancy_Diagnostic": "No dashboard panel fields were available for redundancy review.",
            }
        )
    return pd.DataFrame(records, columns=REDUNDANCY_REVIEW_COLUMNS)


def _record(panel_name: str, field_name: str, count: int) -> dict[str, object]:
    if "Diagnostic" in field_name and count > 1:
        redundancy_class = "DUPLICATIVE_DIAGNOSTIC_FIELD"
        group = "DIAGNOSTIC_FIELDS"
    elif count > 1:
        redundancy_class = "POSSIBLY_REDUNDANT"
        group = "REPEATED_FIELD"
    else:
        redundancy_class = "NOT_REDUNDANT"
        group = "UNIQUE_FIELD"
    return {
        "Panel_Name": panel_name,
        "Field_Name": field_name,
        "Potential_Redundancy_Class": redundancy_class,
        "Redundancy_Group": group,
        "Redundancy_Diagnostic": f"{field_name} appears in {count} reviewed panel(s).",
    }
