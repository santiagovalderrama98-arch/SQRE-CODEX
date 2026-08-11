"""Build fallback stability panel."""

from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.models import numeric_series, text_series


FALLBACK_PANEL_COLUMNS = [
    "Snapshot_Query_ID",
    "Fallback_Attempt_Order",
    "Attempted_Match_Level",
    "Candidate_Reference_Count",
    "Selected_Result_Count",
    "Fallback_Attempt_Status",
    "Dashboard_Warning_Class",
    "Dashboard_Stability_Indicator_Class",
    "Dashboard_Stability_Severity_Class",
    "Fallback_Stability_Diagnostic",
]


def build_fallback_stability_panel(config: DashboardStabilityIndicatorsConfig, fallback_panel: pd.DataFrame) -> pd.DataFrame:
    if fallback_panel.empty:
        return pd.DataFrame(columns=FALLBACK_PANEL_COLUMNS)
    frame = fallback_panel.head(config.maximum_fallback_rows)
    query = text_series(frame, ["Snapshot_Query_ID", "Research_Query_ID"])
    order = numeric_series(frame, ["Fallback_Attempt_Order", "Attempt_Order"])
    match = text_series(frame, ["Attempted_Match_Level", "Snapshot_Query_Match_Level", "Research_Query_Match_Level"])
    candidate = numeric_series(frame, ["Candidate_Reference_Count"])
    selected = numeric_series(frame, ["Selected_Result_Count", "Result_Count"])
    status = text_series(frame, ["Fallback_Attempt_Status", "Attempt_Status"], "FALLBACK_ATTEMPT_RECORDED")
    rows = []
    for index in frame.index:
        warning, indicator, severity = _warning(match.loc[index], status.loc[index], selected.loc[index])
        rows.append(
            {
                "Snapshot_Query_ID": query.loc[index],
                "Fallback_Attempt_Order": int(order.loc[index]),
                "Attempted_Match_Level": match.loc[index],
                "Candidate_Reference_Count": int(candidate.loc[index]),
                "Selected_Result_Count": int(selected.loc[index]),
                "Fallback_Attempt_Status": status.loc[index],
                "Dashboard_Warning_Class": warning,
                "Dashboard_Stability_Indicator_Class": indicator,
                "Dashboard_Stability_Severity_Class": severity,
                "Fallback_Stability_Diagnostic": f"Fallback row {query.loc[index]} mapped to {warning}.",
            }
        )
    return pd.DataFrame(rows, columns=FALLBACK_PANEL_COLUMNS)


def _warning(match_level: str, status: str, selected_count: float) -> tuple[str, str, str]:
    text = f"{match_level} {status}".upper()
    if "FALLBACK" in text or "BROADER" in text:
        return "DASHBOARD_WARNING_FALLBACK_DEPENDENCY", "WARNING_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING"
    if selected_count == 0:
        return "DASHBOARD_WARNING_INPUT_LIMITED", "DOCUMENTATION_ONLY_INDICATOR", "HIGH_STABILITY_WARNING"
    return "DASHBOARD_WARNING_NONE", "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING"
