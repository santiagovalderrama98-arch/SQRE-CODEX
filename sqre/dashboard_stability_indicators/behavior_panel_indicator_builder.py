"""Build dashboard behavior stability panel."""

from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.models import text_series


BEHAVIOR_PANEL_COLUMNS = [
    "Snapshot_ID",
    "Snapshot_Query_Count",
    "Snapshot_Result_Count",
    "Matched_Horizon_Count",
    "Primary_Matched_Horizon",
    "Primary_Match_Level",
    "Primary_Evidence_Class",
    "Observed_Direction_Class_Count",
    "Dominant_Observed_Direction_Count",
    "Dashboard_Stability_Indicator_Class",
    "Dashboard_Stability_Severity_Class",
    "Behavior_Stability_Diagnostic",
]


def build_behavior_stability_panel(reference_card_indicators: pd.DataFrame, behavior_panel: pd.DataFrame) -> pd.DataFrame:
    source = reference_card_indicators if not reference_card_indicators.empty else behavior_panel
    if source.empty:
        return pd.DataFrame(columns=BEHAVIOR_PANEL_COLUMNS)
    match_levels = text_series(source, ["Snapshot_Query_Match_Level", "Primary_Match_Level"])
    evidence = text_series(source, ["Snapshot_Evidence_Class", "Primary_Evidence_Class"])
    directions = text_series(source, ["Matched_Directional_Behavior_Class", "Observed_Direction_Class"])
    horizons = text_series(source, ["Requested_Forward_Horizon_H4_Candles", "Primary_Matched_Horizon"])
    indicator, severity = _aggregate_indicator(reference_card_indicators)
    return pd.DataFrame(
        [
            {
                "Snapshot_ID": _first(text_series(source, ["Snapshot_ID"], "SNAPSHOT_001")),
                "Snapshot_Query_Count": int(text_series(source, ["Snapshot_Query_ID"]).replace("", pd.NA).dropna().nunique()),
                "Snapshot_Result_Count": len(source),
                "Matched_Horizon_Count": int(horizons.replace("", pd.NA).dropna().nunique()),
                "Primary_Matched_Horizon": _mode(horizons),
                "Primary_Match_Level": _mode(match_levels),
                "Primary_Evidence_Class": _mode(evidence),
                "Observed_Direction_Class_Count": int(directions.replace("", pd.NA).dropna().nunique()),
                "Dominant_Observed_Direction_Count": int(directions.value_counts().iloc[0]) if not directions.empty else 0,
                "Dashboard_Stability_Indicator_Class": indicator,
                "Dashboard_Stability_Severity_Class": severity,
                "Behavior_Stability_Diagnostic": "Behavior panel is annotated with stability indicator context.",
            }
        ],
        columns=BEHAVIOR_PANEL_COLUMNS,
    )


def _aggregate_indicator(cards: pd.DataFrame) -> tuple[str, str]:
    if cards.empty:
        return "INPUT_MISSING", "INPUT_MISSING"
    if (cards["Dashboard_Stability_Severity_Class"] == "HIGH_STABILITY_WARNING").any():
        return "WARNING_EVIDENCE_INDICATOR", "HIGH_STABILITY_WARNING"
    if (cards["Dashboard_Stability_Severity_Class"] == "MODERATE_STABILITY_WARNING").any():
        return "PARTIAL_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING"
    return "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING"


def _first(values: pd.Series) -> str:
    clean = values.replace("", pd.NA).dropna()
    return str(clean.iloc[0]) if not clean.empty else ""


def _mode(values: pd.Series) -> str:
    clean = values.replace("", pd.NA).dropna()
    if clean.empty:
        return ""
    return str(clean.value_counts().index[0])
