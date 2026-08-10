"""Build reference stability follow-up documentation."""

from __future__ import annotations

import pandas as pd


FOLLOW_UP_COLUMNS = [
    "Follow_Up_ID",
    "Follow_Up_Category",
    "Follow_Up_Priority",
    "Follow_Up_Title",
    "Follow_Up_Rationale",
    "Expected_Next_Phase",
    "Follow_Up_Diagnostic",
]

FOLLOW_UP_ROWS = [
    ("FUP_001", "DASHBOARD_STABILITY_INDICATORS", "HIGH", "Dashboard stability indicators"),
    ("FUP_002", "EXPANDED_HISTORICAL_COVERAGE", "HIGH", "Expanded H4 historical data coverage"),
    ("FUP_003", "MULTI_PAIR_REPLICATION", "MEDIUM", "Multi-pair reference stability replication"),
    ("FUP_004", "DIRECTIONAL_CONSISTENCY_REVIEW", "MEDIUM", "Directional consistency review"),
    ("FUP_005", "FALLBACK_DEPENDENCY_REVIEW", "MEDIUM", "Fallback dependency review"),
    ("FUP_006", "LIVE_DATA_INTEGRATION_DESIGN", "LOW", "Live data snapshot integration design"),
    ("FUP_007", "DOCUMENTATION_REFINEMENT", "LOW", "Documentation refinement"),
]


def build_follow_up_plan(include: bool) -> pd.DataFrame:
    if not include:
        return pd.DataFrame(columns=FOLLOW_UP_COLUMNS)
    return pd.DataFrame([_row(*values) for values in FOLLOW_UP_ROWS], columns=FOLLOW_UP_COLUMNS)


def _row(follow_up_id: str, category: str, priority: str, title: str) -> dict[str, str]:
    return {
        "Follow_Up_ID": follow_up_id,
        "Follow_Up_Category": category,
        "Follow_Up_Priority": priority,
        "Follow_Up_Title": title,
        "Follow_Up_Rationale": _rationale(category),
        "Expected_Next_Phase": title,
        "Follow_Up_Diagnostic": f"{category} documented as {priority} priority.",
    }


def _rationale(category: str) -> str:
    return {
        "DASHBOARD_STABILITY_INDICATORS": "Expose stability classes clearly before dashboard interpretation expands.",
        "EXPANDED_HISTORICAL_COVERAGE": "Reduce partial horizon constraints by extending H4 evidence.",
        "MULTI_PAIR_REPLICATION": "Check whether reference stability patterns replicate beyond EURUSD.",
        "DIRECTIONAL_CONSISTENCY_REVIEW": "Review direction labels without treating them as instructions.",
        "FALLBACK_DEPENDENCY_REVIEW": "Clarify which dashboard references depend on broader matching.",
        "LIVE_DATA_INTEGRATION_DESIGN": "Design future live snapshot plumbing separately from research docs.",
        "DOCUMENTATION_REFINEMENT": "Improve wording as new stability outputs mature.",
    }[category]
