"""Build dashboard stability warning summary."""

from __future__ import annotations

import pandas as pd


WARNING_SUMMARY_COLUMNS = [
    "Dashboard_Warning_Class",
    "Warning_Count",
    "Affected_Reference_Card_Count",
    "Affected_Query_Count",
    "Dashboard_Stability_Severity_Class",
    "Warning_Diagnostic",
]


def build_dashboard_warning_summary(reference_cards: pd.DataFrame, fallback_panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.extend(_card_warning_rows(reference_cards))
    rows.extend(_fallback_warning_rows(fallback_panel))
    if not rows:
        return pd.DataFrame(columns=WARNING_SUMMARY_COLUMNS)
    frame = pd.DataFrame(rows)
    grouped = []
    for warning_class, group in frame.groupby("Dashboard_Warning_Class"):
        severity = _highest_severity(group["Dashboard_Stability_Severity_Class"])
        grouped.append(
            {
                "Dashboard_Warning_Class": warning_class,
                "Warning_Count": len(group),
                "Affected_Reference_Card_Count": int(group["Reference_Card_ID"].replace("", pd.NA).dropna().nunique()),
                "Affected_Query_Count": int(group["Snapshot_Query_ID"].replace("", pd.NA).dropna().nunique()),
                "Dashboard_Stability_Severity_Class": severity,
                "Warning_Diagnostic": f"{warning_class} appears in {len(group)} dashboard indicator row(s).",
            }
        )
    return pd.DataFrame(grouped, columns=WARNING_SUMMARY_COLUMNS)


def _card_warning_rows(cards: pd.DataFrame) -> list[dict[str, str]]:
    rows = []
    if cards.empty:
        return rows
    for _, row in cards.iterrows():
        warning_class = _card_warning_class(row)
        rows.append(
            {
                "Dashboard_Warning_Class": warning_class,
                "Reference_Card_ID": str(row.get("Reference_Card_ID", "")),
                "Snapshot_Query_ID": str(row.get("Snapshot_Query_ID", "")),
                "Dashboard_Stability_Severity_Class": str(row.get("Dashboard_Stability_Severity_Class", "")),
            }
        )
    return rows


def _fallback_warning_rows(fallback: pd.DataFrame) -> list[dict[str, str]]:
    rows = []
    if fallback.empty:
        return rows
    for _, row in fallback.iterrows():
        rows.append(
            {
                "Dashboard_Warning_Class": str(row.get("Dashboard_Warning_Class", "DASHBOARD_WARNING_NONE")),
                "Reference_Card_ID": "",
                "Snapshot_Query_ID": str(row.get("Snapshot_Query_ID", "")),
                "Dashboard_Stability_Severity_Class": str(row.get("Dashboard_Stability_Severity_Class", "")),
            }
        )
    return rows


def _card_warning_class(row: pd.Series) -> str:
    primary = str(row.get("Primary_Stability_Warning", "")).upper()
    severity = str(row.get("Dashboard_Stability_Severity_Class", "")).upper()
    if "DIRECTIONALLY" in primary:
        return "DASHBOARD_WARNING_DIRECTIONAL_INSTABILITY"
    if "FALLBACK" in primary:
        return "DASHBOARD_WARNING_FALLBACK_DEPENDENCY"
    if "PARTIAL" in primary or severity == "MODERATE_STABILITY_WARNING":
        return "DASHBOARD_WARNING_PARTIAL_EVIDENCE"
    if severity == "HIGH_STABILITY_WARNING":
        return "DASHBOARD_WARNING_INPUT_LIMITED"
    return "DASHBOARD_WARNING_NONE"


def _highest_severity(values: pd.Series) -> str:
    labels = set(values.astype(str))
    if "HIGH_STABILITY_WARNING" in labels:
        return "HIGH_STABILITY_WARNING"
    if "MODERATE_STABILITY_WARNING" in labels:
        return "MODERATE_STABILITY_WARNING"
    if "LOW_STABILITY_WARNING" in labels:
        return "LOW_STABILITY_WARNING"
    return "INPUT_MISSING"
