"""Reference tier classification for Research Reference Store Design."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig


INCLUDED_STATUS = "INCLUDED_IN_RESEARCH_REFERENCE_STORE"
WATCHLIST_STATUS = "WATCHLIST_ONLY"
EXCLUDED_STATUS = "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE"
INPUT_MISSING_STATUS = "INPUT_MISSING"


def classify_reference_tier(row: pd.Series, config: ResearchReferenceStoreDesignConfig) -> tuple[str, str, str]:
    sample_size = _int(row.get("Outcome_Sample_Size"))
    dispersion = _float(row.get("Outcome_Dispersion_Pips"))
    interpretability = str(row.get("Outcome_Interpretability_Class", ""))
    horizon_stability = str(row.get("Horizon_Stability_Class", ""))

    if not str(row.get("Outcome_Profile_ID", "")).strip():
        return "INPUT_MISSING", INPUT_MISSING_STATUS, "Input profile identifier is missing."
    if sample_size <= 0 or "INPUT_MISSING" in interpretability:
        return "INPUT_MISSING", INPUT_MISSING_STATUS, "Input profile is missing or empty."
    if "SAMPLE_CONSTRAINED" in interpretability or sample_size < config.minimum_supporting_reference_sample_size:
        return "EXCLUDED_SAMPLE_CONSTRAINED", EXCLUDED_STATUS, "Profile is constrained by historical sample size."
    if "HIGH_DISPERSION" in interpretability or dispersion > config.maximum_supporting_dispersion_pips:
        return "EXCLUDED_HIGH_DISPERSION", EXCLUDED_STATUS, "Profile dispersion is above reference-store limits."
    if "LOW_INTERPRETABILITY" in interpretability:
        return "EXCLUDED_LOW_INTERPRETABILITY", EXCLUDED_STATUS, "Profile has low interpretability without supporting evidence."
    if config.require_stable_horizon_context and horizon_stability == "UNSTABLE_ACROSS_HORIZONS":
        return "WATCHLIST_RESEARCH_REFERENCE", WATCHLIST_STATUS, "Profile is retained for review due to horizon instability."
    if (
        interpretability == "INTERPRETABLE_OUTCOME_PROFILE"
        and sample_size >= config.minimum_core_reference_sample_size
        and dispersion <= config.maximum_core_dispersion_pips
    ):
        return "CORE_RESEARCH_REFERENCE", INCLUDED_STATUS, "Profile meets core research reference criteria."
    if (
        interpretability == "MODERATELY_INTERPRETABLE_OUTCOME_PROFILE"
        or sample_size >= config.minimum_supporting_reference_sample_size
    ) and dispersion <= config.maximum_supporting_dispersion_pips:
        return "SUPPORTING_RESEARCH_REFERENCE", INCLUDED_STATUS, "Profile meets supporting research reference criteria."
    return "WATCHLIST_RESEARCH_REFERENCE", WATCHLIST_STATUS, "Profile has historical structure but remains limited for reference use."


def _int(value: object) -> int:
    number = pd.to_numeric(value, errors="coerce")
    return int(number) if pd.notna(number) else 0


def _float(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return round(float(number), 6) if pd.notna(number) else 0.0
