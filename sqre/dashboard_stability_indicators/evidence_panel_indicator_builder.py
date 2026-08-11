"""Build dashboard evidence stability panel."""

from __future__ import annotations

import pandas as pd

from sqre.dashboard_stability_indicators.models import numeric_series, safe_mean, text_series


EVIDENCE_PANEL_COLUMNS = [
    "Snapshot_Evidence_Class",
    "Snapshot_Result_Count",
    "Unique_Snapshot_Query_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Dashboard_Stability_Indicator_Class",
    "Dashboard_Stability_Severity_Class",
    "Evidence_Stability_Diagnostic",
]


def build_evidence_stability_panel(reference_card_indicators: pd.DataFrame, evidence_panel: pd.DataFrame) -> pd.DataFrame:
    source = reference_card_indicators if not reference_card_indicators.empty else evidence_panel
    if source.empty:
        return pd.DataFrame(columns=EVIDENCE_PANEL_COLUMNS)
    evidence_class = text_series(source, ["Snapshot_Evidence_Class"], "INPUT_MISSING")
    sample = numeric_series(source, ["Matched_Outcome_Sample_Size", "Average_Outcome_Sample_Size"])
    dispersion = numeric_series(source, ["Matched_Outcome_Dispersion_Pips", "Average_Outcome_Dispersion_Pips"])
    tier = text_series(source, ["Matched_Reference_Tier", "Reference_Tier"]).str.upper()
    query = text_series(source, ["Snapshot_Query_ID", "Research_Query_ID"])
    indicator, severity = _aggregate_indicator(reference_card_indicators)
    return pd.DataFrame(
        [
            {
                "Snapshot_Evidence_Class": _mode(evidence_class),
                "Snapshot_Result_Count": len(source),
                "Unique_Snapshot_Query_Count": int(query.replace("", pd.NA).dropna().nunique()),
                "Core_Reference_Count": int(tier.str.contains("CORE", na=False).sum()),
                "Supporting_Reference_Count": int(tier.str.contains("SUPPORTING", na=False).sum()),
                "Average_Outcome_Sample_Size": safe_mean(sample),
                "Average_Outcome_Dispersion_Pips": safe_mean(dispersion),
                "Dashboard_Stability_Indicator_Class": indicator,
                "Dashboard_Stability_Severity_Class": severity,
                "Evidence_Stability_Diagnostic": "Evidence panel summarizes dashboard reference stability indicators.",
            }
        ],
        columns=EVIDENCE_PANEL_COLUMNS,
    )


def _aggregate_indicator(cards: pd.DataFrame) -> tuple[str, str]:
    if cards.empty:
        return "INPUT_MISSING", "INPUT_MISSING"
    severities = set(cards["Dashboard_Stability_Severity_Class"].astype(str))
    if "HIGH_STABILITY_WARNING" in severities:
        return "WARNING_EVIDENCE_INDICATOR", "HIGH_STABILITY_WARNING"
    if "MODERATE_STABILITY_WARNING" in severities:
        return "PARTIAL_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING"
    return "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING"


def _mode(values: pd.Series) -> str:
    clean = values.replace("", pd.NA).dropna()
    if clean.empty:
        return "INPUT_MISSING"
    return str(clean.value_counts().index[0])
