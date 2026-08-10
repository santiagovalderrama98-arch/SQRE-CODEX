"""Dashboard reference card stability review."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, safe_mean, text_series, tier_counts


DASHBOARD_COLUMNS = [
    "Reference_Card_Count",
    "Distinct_Horizon_Count",
    "Distinct_Match_Level_Count",
    "Core_Card_Count",
    "Supporting_Card_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Dashboard_Reference_Stability_Class",
    "Dashboard_Reference_Stability_Diagnostic",
]


def build_dashboard_reference_stability_review(
    config: ReferenceStabilityValidationConfig,
    dashboard_reference_cards: pd.DataFrame,
) -> pd.DataFrame:
    if dashboard_reference_cards.empty:
        return pd.DataFrame(
            [
                {
                    "Reference_Card_Count": 0,
                    "Distinct_Horizon_Count": 0,
                    "Distinct_Match_Level_Count": 0,
                    "Core_Card_Count": 0,
                    "Supporting_Card_Count": 0,
                    "Average_Outcome_Sample_Size": 0.0,
                    "Average_Outcome_Dispersion_Pips": 0.0,
                    "Dashboard_Reference_Stability_Class": "DASHBOARD_REFERENCES_INPUT_LIMITED",
                    "Dashboard_Reference_Stability_Diagnostic": _diagnostic("DASHBOARD_REFERENCES_INPUT_LIMITED"),
                }
            ],
            columns=DASHBOARD_COLUMNS,
        )
    sample = numeric_series(dashboard_reference_cards, ["Matched_Outcome_Sample_Size", "Outcome_Sample_Size"])
    dispersion = numeric_series(dashboard_reference_cards, ["Matched_Outcome_Dispersion_Pips", "Outcome_Dispersion_Pips"])
    core, supporting, _ = tier_counts(dashboard_reference_cards, ["Matched_Reference_Tier", "Reference_Tier"])
    horizon_count = int(numeric_series(dashboard_reference_cards, ["Matched_Forward_Horizon_H4_Candles", "Requested_Forward_Horizon_H4_Candles"]).replace(0, pd.NA).dropna().nunique())
    match_count = int(text_series(dashboard_reference_cards, ["Snapshot_Query_Match_Level", "Research_Query_Match_Level"]).replace("", pd.NA).dropna().nunique())
    klass = _classify(config, len(dashboard_reference_cards), safe_mean(sample), safe_mean(dispersion))
    return pd.DataFrame(
        [
            {
                "Reference_Card_Count": len(dashboard_reference_cards),
                "Distinct_Horizon_Count": horizon_count,
                "Distinct_Match_Level_Count": match_count,
                "Core_Card_Count": core,
                "Supporting_Card_Count": supporting,
                "Average_Outcome_Sample_Size": safe_mean(sample),
                "Average_Outcome_Dispersion_Pips": safe_mean(dispersion),
                "Dashboard_Reference_Stability_Class": klass,
                "Dashboard_Reference_Stability_Diagnostic": _diagnostic(klass),
            }
        ],
        columns=DASHBOARD_COLUMNS,
    )


def _classify(config: ReferenceStabilityValidationConfig, card_count: int, avg_sample: float, avg_dispersion: float) -> str:
    if card_count >= config.minimum_dashboard_card_count and avg_sample >= config.minimum_stable_sample_size and avg_dispersion <= config.maximum_stable_dispersion_pips:
        return "DASHBOARD_REFERENCES_STABLE_FOR_REVIEW"
    if card_count > 0 and avg_sample >= config.minimum_usable_sample_size and avg_dispersion <= config.maximum_usable_dispersion_pips:
        return "DASHBOARD_REFERENCES_PARTIAL_FOR_REVIEW"
    return "DASHBOARD_REFERENCES_INPUT_LIMITED"


def _diagnostic(klass: str) -> str:
    return {
        "DASHBOARD_REFERENCES_STABLE_FOR_REVIEW": "Dashboard reference cards are stable for repeated research review.",
        "DASHBOARD_REFERENCES_PARTIAL_FOR_REVIEW": "Dashboard reference cards are usable with stability notes.",
        "DASHBOARD_REFERENCES_INPUT_LIMITED": "Dashboard reference cards are missing or constrained by local inputs.",
        "INPUT_MISSING": "No dashboard reference rows were available.",
    }[klass]
