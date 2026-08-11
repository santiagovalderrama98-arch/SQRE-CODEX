"""Build stability indicators for dashboard reference cards."""

from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.models import numeric_series, text_series


REFERENCE_CARD_COLUMNS = [
    "Reference_Card_ID",
    "Snapshot_Query_ID",
    "Requested_Forward_Horizon_H4_Candles",
    "Matched_Research_Reference_ID",
    "Matched_Outcome_Profile_ID",
    "Matched_Context_Granularity",
    "Matched_Reference_Tier",
    "Matched_Outcome_Sample_Size",
    "Matched_Outcome_Dispersion_Pips",
    "Matched_Directional_Behavior_Class",
    "Matched_Horizon_Stability_Class",
    "Snapshot_Query_Match_Level",
    "Snapshot_Evidence_Class",
    "Reference_Card_Stability_Class",
    "Dashboard_Stability_Indicator_Class",
    "Dashboard_Stability_Severity_Class",
    "Primary_Stability_Warning",
    "Secondary_Stability_Warning",
    "Indicator_Diagnostic",
]


def build_reference_card_indicators(config: DashboardStabilityIndicatorsConfig, reference_cards: pd.DataFrame) -> pd.DataFrame:
    if not config.include_reference_card_indicators or reference_cards.empty:
        return pd.DataFrame(columns=REFERENCE_CARD_COLUMNS)
    cards = reference_cards.head(config.maximum_reference_cards).copy()
    rows = []
    for index, row in cards.iterrows():
        values = _extract(cards, index)
        klass, indicator, severity, primary, secondary = _classify_card(values)
        values.update(
            {
                "Reference_Card_Stability_Class": klass,
                "Dashboard_Stability_Indicator_Class": indicator,
                "Dashboard_Stability_Severity_Class": severity,
                "Primary_Stability_Warning": primary,
                "Secondary_Stability_Warning": secondary,
                "Indicator_Diagnostic": f"{values['Reference_Card_ID']} mapped to {klass}.",
            }
        )
        rows.append(values)
    return pd.DataFrame(rows, columns=REFERENCE_CARD_COLUMNS)


def _extract(frame: pd.DataFrame, index: int) -> dict[str, object]:
    row = frame.loc[index]
    return {
        "Reference_Card_ID": _text(row, "Reference_Card_ID", f"CARD_{index + 1:03d}"),
        "Snapshot_Query_ID": _text(row, "Snapshot_Query_ID"),
        "Requested_Forward_Horizon_H4_Candles": _number(row, "Requested_Forward_Horizon_H4_Candles"),
        "Matched_Research_Reference_ID": _text(row, "Matched_Research_Reference_ID"),
        "Matched_Outcome_Profile_ID": _text(row, "Matched_Outcome_Profile_ID"),
        "Matched_Context_Granularity": _text(row, "Matched_Context_Granularity"),
        "Matched_Reference_Tier": _text(row, "Matched_Reference_Tier"),
        "Matched_Outcome_Sample_Size": _number(row, "Matched_Outcome_Sample_Size"),
        "Matched_Outcome_Dispersion_Pips": _number(row, "Matched_Outcome_Dispersion_Pips"),
        "Matched_Directional_Behavior_Class": _text(row, "Matched_Directional_Behavior_Class"),
        "Matched_Horizon_Stability_Class": _text(row, "Matched_Horizon_Stability_Class"),
        "Snapshot_Query_Match_Level": _text(row, "Snapshot_Query_Match_Level"),
        "Snapshot_Evidence_Class": _text(row, "Snapshot_Evidence_Class"),
    }


def _classify_card(values: dict[str, object]) -> tuple[str, str, str, str, str]:
    match = str(values["Snapshot_Query_Match_Level"]).upper()
    direction = str(values["Matched_Directional_Behavior_Class"]).upper()
    horizon = str(values["Matched_Horizon_Stability_Class"]).upper()
    evidence = str(values["Snapshot_Evidence_Class"]).upper()
    granularity = str(values["Matched_Context_Granularity"]).upper()
    fallback = "FALLBACK" in match or "BROADER" in match
    unstable_direction = "UNSTABLE" in direction or "MIXED" in direction
    partial_horizon = "PARTIAL" in horizon
    partial_granularity = "PARTIAL" in granularity or "FRAGMENTED" in granularity
    if unstable_direction:
        return (
            "REFERENCE_CARD_WARNING_REQUIRED",
            "WARNING_EVIDENCE_INDICATOR",
            "HIGH_STABILITY_WARNING",
            "Directionally unstable reference evidence.",
            "Review only as descriptive historical context.",
        )
    if fallback:
        return (
            "REFERENCE_CARD_WARNING_REQUIRED",
            "WARNING_EVIDENCE_INDICATOR",
            "MODERATE_STABILITY_WARNING",
            "Fallback-dependent reference match.",
            "Broader matching reduces context specificity.",
        )
    if partial_horizon or partial_granularity or "PARTIAL" in evidence:
        return (
            "REFERENCE_CARD_PARTIAL_FOR_REVIEW",
            "PARTIAL_EVIDENCE_INDICATOR",
            "MODERATE_STABILITY_WARNING",
            "Partial stability evidence.",
            "Display with stability warning.",
        )
    if "DOCUMENTATION" in evidence:
        return (
            "REFERENCE_CARD_DOCUMENTATION_ONLY",
            "DOCUMENTATION_ONLY_INDICATOR",
            "HIGH_STABILITY_WARNING",
            "Documentation-only evidence.",
            "Input or stability review is required.",
        )
    return (
        "REFERENCE_CARD_STABLE_FOR_REVIEW",
        "STABLE_EVIDENCE_INDICATOR",
        "LOW_STABILITY_WARNING",
        "Stable reference evidence.",
        "Research-only evidence quality indicator.",
    )


def _text(row: pd.Series, column: str, default: str = "") -> str:
    value = row.get(column, default)
    return default if pd.isna(value) else str(value).strip()


def _number(row: pd.Series, column: str) -> float:
    return float(pd.to_numeric(pd.Series([row.get(column, 0)]), errors="coerce").fillna(0).iloc[0])
