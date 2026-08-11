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
    query_statuses = build_query_fallback_statuses(frame)
    query = text_series(frame, ["Snapshot_Query_ID", "Research_Query_ID"])
    order = numeric_series(frame, ["Fallback_Attempt_Order", "Attempt_Order"])
    match = text_series(frame, ["Attempted_Match_Level", "Snapshot_Query_Match_Level", "Research_Query_Match_Level"])
    candidate = numeric_series(frame, ["Candidate_Reference_Count"])
    selected = numeric_series(frame, ["Selected_Result_Count", "Result_Count"])
    status = text_series(frame, ["Fallback_Attempt_Status", "Attempt_Status"], "FALLBACK_ATTEMPT_RECORDED")
    rows = []
    for index in frame.index:
        query_status = query_statuses.get(query.loc[index], "NO_USABLE_REFERENCE_FOUND")
        warning, indicator, severity, diagnostic = _warning(query_status)
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
                "Fallback_Stability_Diagnostic": diagnostic,
            }
        )
    return pd.DataFrame(rows, columns=FALLBACK_PANEL_COLUMNS)


def build_query_fallback_statuses(fallback_panel: pd.DataFrame) -> dict[str, str]:
    """Classify fallback behavior at Snapshot_Query_ID level."""

    if fallback_panel.empty:
        return {}
    query = text_series(fallback_panel, ["Snapshot_Query_ID", "Research_Query_ID"])
    match = text_series(fallback_panel, ["Attempted_Match_Level", "Snapshot_Query_Match_Level", "Research_Query_Match_Level"])
    selected = numeric_series(fallback_panel, ["Selected_Result_Count", "Result_Count"])
    status = text_series(fallback_panel, ["Fallback_Attempt_Status", "Attempt_Status"], "")
    normalized = pd.DataFrame(
        {
            "query": query,
            "match": match,
            "selected": selected,
            "status": status,
        }
    )
    statuses: dict[str, str] = {}
    for query_id, group in normalized.groupby("query", dropna=False):
        statuses[str(query_id)] = _query_status(group)
    return statuses


def _query_status(group: pd.DataFrame) -> str:
    exact_matches = group[group["match"].astype(str).str.upper().map(_is_exact_match_level)]
    if not exact_matches.empty and any(
        _is_match_found(row["status"], row["selected"]) for _, row in exact_matches.iterrows()
    ):
        return "EXACT_MATCH_AVAILABLE"
    later_matches = group[~group["match"].astype(str).str.upper().map(_is_exact_match_level)]
    if not later_matches.empty and any(
        _is_match_found(row["status"], row["selected"]) for _, row in later_matches.iterrows()
    ):
        return "FALLBACK_MATCH_USED"
    return "NO_USABLE_REFERENCE_FOUND"


def _is_exact_match_level(value: str) -> bool:
    text = str(value).upper()
    return text == "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH" or (
        "EXACT" in text and "STATE_REGIME" in text
    )


def _is_match_found(status: str, selected_count: float) -> bool:
    text = str(status).upper()
    if text in {"MATCH_FOUND", "FALLBACK_SELECTED", "SELECTED"}:
        return True
    if "NO_MATCH" in text or "INPUT_MISSING" in text:
        return False
    return selected_count > 0


def _warning(query_status: str) -> tuple[str, str, str, str]:
    if query_status == "EXACT_MATCH_AVAILABLE":
        return (
            "DASHBOARD_WARNING_NONE",
            "STABLE_EVIDENCE_INDICATOR",
            "LOW_STABILITY_WARNING",
            "Exact context match available.",
        )
    if query_status == "FALLBACK_MATCH_USED":
        return (
            "DASHBOARD_WARNING_FALLBACK_DEPENDENCY",
            "WARNING_EVIDENCE_INDICATOR",
            "MODERATE_STABILITY_WARNING",
            "Exact context unavailable; broader fallback context used.",
        )
    return (
        "DASHBOARD_WARNING_INPUT_LIMITED",
        "DOCUMENTATION_ONLY_INDICATOR",
        "HIGH_STABILITY_WARNING",
        "No usable reference found after fallback attempts.",
    )
