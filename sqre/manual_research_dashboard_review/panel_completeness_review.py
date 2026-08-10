"""Panel completeness review for manual dashboard usability."""

from __future__ import annotations

import pandas as pd


PANEL_COMPLETENESS_COLUMNS = [
    "Panel_Name",
    "Expected_Minimum_Rows",
    "Actual_Rows",
    "Panel_Completeness_Class",
    "Missing_Required_Content",
    "Completeness_Diagnostic",
]

PANEL_FRAME_KEYS = {
    "Snapshot Panel": "prototype_snapshot_panel",
    "Reference Cards": "prototype_reference_cards",
    "Evidence Panel": "prototype_evidence_panel",
    "Behavior Panel": "prototype_behavior_panel",
    "Fallback Panel": "prototype_fallback_panel",
    "Diagnostic Panel": "prototype_diagnostic_panel",
    "Summary Panel": "prototype_summary",
}


def build_panel_completeness_review(frames: dict[str, pd.DataFrame], texts: dict[str, str]) -> pd.DataFrame:
    records = [_review_panel(panel, frames.get(key, pd.DataFrame())) for panel, key in PANEL_FRAME_KEYS.items()]
    html_rows = 1 if texts.get("prototype_html", "").strip() else 0
    records.append(_record("HTML Dashboard", 1, html_rows, "HTML dashboard content"))
    return pd.DataFrame(records, columns=PANEL_COMPLETENESS_COLUMNS)


def _review_panel(panel_name: str, frame: pd.DataFrame) -> dict[str, object]:
    return _record(panel_name, 1, len(frame), "panel rows")


def _record(panel_name: str, minimum_rows: int, actual_rows: int, content_label: str) -> dict[str, object]:
    if actual_rows >= minimum_rows:
        panel_class = "PANEL_COMPLETE"
        missing = False
        diagnostic = f"{panel_name} contains required {content_label}."
    elif actual_rows > 0:
        panel_class = "PANEL_PARTIAL"
        missing = True
        diagnostic = f"{panel_name} contains partial {content_label}."
    else:
        panel_class = "PANEL_EMPTY"
        missing = True
        diagnostic = f"{panel_name} has no available {content_label}."
    return {
        "Panel_Name": panel_name,
        "Expected_Minimum_Rows": minimum_rows,
        "Actual_Rows": actual_rows,
        "Panel_Completeness_Class": panel_class,
        "Missing_Required_Content": missing,
        "Completeness_Diagnostic": diagnostic,
    }
