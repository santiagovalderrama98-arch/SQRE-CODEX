"""Panel readability review for the manual dashboard phase."""

from __future__ import annotations

import pandas as pd

from sqre.manual_research_dashboard_review.panel_completeness_review import PANEL_FRAME_KEYS


PANEL_READABILITY_COLUMNS = [
    "Panel_Name",
    "Field_Count",
    "Row_Count",
    "Readability_Class",
    "Readability_Issue_Count",
    "Readability_Diagnostic",
]


def build_panel_readability_review(frames: dict[str, pd.DataFrame], texts: dict[str, str]) -> pd.DataFrame:
    records = [_review_frame(panel, frames.get(key, pd.DataFrame())) for panel, key in PANEL_FRAME_KEYS.items()]
    html = texts.get("prototype_html", "")
    html_issues = int("Research-only" not in html and "research-only" not in html) + int("Limitations" not in html)
    records.append(
        {
            "Panel_Name": "HTML Dashboard",
            "Field_Count": 1,
            "Row_Count": 1 if html.strip() else 0,
            "Readability_Class": _classify(1, 1 if html.strip() else 0, html_issues),
            "Readability_Issue_Count": html_issues if html.strip() else 1,
            "Readability_Diagnostic": "HTML includes explicit research context."
            if html_issues == 0 and html.strip()
            else "HTML dashboard is missing readability or limitation context.",
        }
    )
    return pd.DataFrame(records, columns=PANEL_READABILITY_COLUMNS)


def _review_frame(panel_name: str, frame: pd.DataFrame) -> dict[str, object]:
    field_count = len(frame.columns)
    row_count = len(frame)
    issues = 0
    if row_count == 0:
        issues += 1
    if field_count > 24:
        issues += 2
    elif field_count > 16:
        issues += 1
    if row_count > 25:
        issues += 1
    readability = _classify(field_count, row_count, issues)
    diagnostic = _diagnostic(panel_name, field_count, row_count, issues)
    return {
        "Panel_Name": panel_name,
        "Field_Count": field_count,
        "Row_Count": row_count,
        "Readability_Class": readability,
        "Readability_Issue_Count": issues,
        "Readability_Diagnostic": diagnostic,
    }


def _classify(field_count: int, row_count: int, issue_count: int) -> str:
    if row_count == 0 and field_count == 0:
        return "INPUT_MISSING"
    if issue_count >= 2:
        return "LOW_READABILITY"
    if issue_count == 1:
        return "MODERATE_READABILITY"
    return "HIGH_READABILITY"


def _diagnostic(panel_name: str, field_count: int, row_count: int, issue_count: int) -> str:
    if row_count == 0:
        return f"{panel_name} has no rows for manual review."
    if field_count > 24:
        return f"{panel_name} has many fields and may need field reduction."
    if issue_count:
        return f"{panel_name} has moderate readability constraints."
    return f"{panel_name} is readable for repeated manual research review."
