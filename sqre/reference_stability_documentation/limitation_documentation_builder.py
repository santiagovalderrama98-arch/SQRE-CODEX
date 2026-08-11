"""Build reference stability limitations documentation."""

from __future__ import annotations

import pandas as pd


LIMITATION_COLUMNS = [
    "Limitation_Category",
    "Limitation_Text",
    "Why_It_Matters",
    "How_To_Display_To_User",
    "Follow_Up_Action",
    "Limitation_Diagnostic",
]

LIMITATION_CATEGORIES = [
    "Partial Historical Coverage",
    "Partial Horizon Stability",
    "Partial Granularity Stability",
    "Directional Instability",
    "Fallback Dependency",
    "Dashboard Snapshot Dependency",
    "No Live Data",
    "No Predictive Claim",
    "No Operational Decision",
]


def build_limitations_documentation() -> pd.DataFrame:
    return pd.DataFrame([_row(category) for category in LIMITATION_CATEGORIES], columns=LIMITATION_COLUMNS)


def _row(category: str) -> dict[str, object]:
    texts = {
        "Partial Historical Coverage": "Historical coverage may be partial due to local provider limits.",
        "Partial Horizon Stability": "Partial horizon stability means evidence should be compared across horizons cautiously.",
        "Partial Granularity Stability": "Partial granularity stability means overly specific contexts may fragment the evidence.",
        "Directional Instability": "Directional instability means directional behavior should not be over-interpreted.",
        "Fallback Dependency": "Fallback-dependent matches should be displayed with clear evidence warnings.",
        "Dashboard Snapshot Dependency": "Dashboard reference cards depend on the latest available snapshot.",
        "No Live Data": "The dashboard is not live market data unless explicitly connected in a later phase.",
        "No Predictive Claim": "Stable sample size and stable dispersion do not imply predictive edge.",
        "No Operational Decision": "Documentation findings are descriptive research guidance only.",
    }
    return {
        "Limitation_Category": category,
        "Limitation_Text": texts[category],
        "Why_It_Matters": "It prevents descriptive research evidence from being over-interpreted.",
        "How_To_Display_To_User": "Show as visible research-only caution text near affected evidence.",
        "Follow_Up_Action": _follow_up(category),
        "Limitation_Diagnostic": f"{category} limitation documented.",
    }


def _follow_up(category: str) -> str:
    if category == "Partial Historical Coverage":
        return "Expanded H4 historical data coverage"
    if category == "Directional Instability":
        return "Directional consistency review"
    if category == "Fallback Dependency":
        return "Fallback dependency review"
    if category == "No Live Data":
        return "Live data snapshot integration design"
    return "Documentation refinement"
