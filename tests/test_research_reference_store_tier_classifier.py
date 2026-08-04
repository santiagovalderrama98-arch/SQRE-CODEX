import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.reference_tier_classifier import classify_reference_tier


def test_tier_classifier_identifies_core_research_reference():
    tier, status, _ = classify_reference_tier(_row("INTERPRETABLE_OUTCOME_PROFILE", 25, 20), ResearchReferenceStoreDesignConfig())

    assert tier == "CORE_RESEARCH_REFERENCE"
    assert status == "INCLUDED_IN_RESEARCH_REFERENCE_STORE"


def test_tier_classifier_identifies_supporting_research_reference():
    tier, status, _ = classify_reference_tier(
        _row("MODERATELY_INTERPRETABLE_OUTCOME_PROFILE", 12, 50), ResearchReferenceStoreDesignConfig()
    )

    assert tier == "SUPPORTING_RESEARCH_REFERENCE"
    assert status == "INCLUDED_IN_RESEARCH_REFERENCE_STORE"


def test_tier_classifier_excludes_sample_constrained_profiles():
    tier, status, _ = classify_reference_tier(
        _row("NOT_INTERPRETABLE_SAMPLE_CONSTRAINED", 5, 10), ResearchReferenceStoreDesignConfig()
    )

    assert tier == "EXCLUDED_SAMPLE_CONSTRAINED"
    assert status == "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE"


def test_tier_classifier_excludes_high_dispersion_profiles():
    tier, status, _ = classify_reference_tier(
        _row("NOT_INTERPRETABLE_HIGH_DISPERSION", 30, 100), ResearchReferenceStoreDesignConfig()
    )

    assert tier == "EXCLUDED_HIGH_DISPERSION"
    assert status == "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE"


def test_tier_classifier_excludes_low_interpretability_profiles():
    tier, status, _ = classify_reference_tier(
        _row("LOW_INTERPRETABILITY_OUTCOME_PROFILE", 30, 20), ResearchReferenceStoreDesignConfig()
    )

    assert tier == "EXCLUDED_LOW_INTERPRETABILITY"
    assert status == "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE"


def _row(interpretability: str, sample_size: int, dispersion: float) -> pd.Series:
    return pd.Series(
        {
            "Outcome_Profile_ID": "OP_1",
            "Outcome_Interpretability_Class": interpretability,
            "Outcome_Sample_Size": sample_size,
            "Outcome_Dispersion_Pips": dispersion,
            "Horizon_Stability_Class": "STABLE_ACROSS_HORIZONS",
        }
    )
