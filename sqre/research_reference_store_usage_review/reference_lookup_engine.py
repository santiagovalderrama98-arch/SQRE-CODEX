"""Reference lookup engine for research-only usage scenarios."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.match_quality_classifier import (
    classify_evidence_quality,
    classify_match_quality,
)
from sqre.research_reference_store_usage_review.reference_query_builder import (
    find_column,
    float_value,
    int_value,
    same_text,
    text_value,
)


LOOKUP_COLUMNS = [
    "Reference_Lookup_ID",
    "Usage_Scenario_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Forward_Horizon_H4_Candles",
    "Matched_Research_Reference_ID",
    "Matched_Outcome_Profile_ID",
    "Matched_Context_Granularity",
    "Matched_Reference_Tier",
    "Matched_Outcome_Sample_Size",
    "Matched_Outcome_Dispersion_Pips",
    "Matched_Directional_Behavior_Class",
    "Matched_Dominant_Observed_Direction",
    "Matched_Excursion_Behavior_Class",
    "Matched_Horizon_Stability_Class",
    "Reference_Match_Level",
    "Reference_Match_Quality_Class",
    "Reference_Evidence_Quality_Class",
    "Lookup_Diagnostic",
]
MATCH_LEVELS = [
    "EXACT_D1_STATE_REGIME_CONTEXT_MATCH",
    "D1_REGIME_CONTEXT_MATCH",
    "D1_MARKET_STATE_CONTEXT_MATCH",
    "H4_TRANSITION_ONLY_CONTEXT_MATCH",
]


def build_reference_lookup_results(
    usage_scenarios: pd.DataFrame,
    reference_store: pd.DataFrame,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> pd.DataFrame:
    rows = [_lookup(index + 1, scenario, reference_store, config) for index, scenario in usage_scenarios.iterrows()]
    return pd.DataFrame(rows, columns=LOOKUP_COLUMNS)


def _lookup(
    lookup_number: int,
    scenario: pd.Series,
    reference_store: pd.DataFrame,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> dict[str, object]:
    if scenario.get("Scenario_Source") == "INPUT_MISSING":
        return _empty_lookup(lookup_number, scenario, "INPUT_MISSING", "Required scenario inputs are missing.")
    if reference_store.empty:
        return _empty_lookup(lookup_number, scenario, "NO_REFERENCE_MATCH", "Research reference store has no rows.")
    for match_level in MATCH_LEVELS:
        matches = _filter(reference_store, scenario, match_level)
        if matches.empty:
            continue
        match = _best(matches)
        sample_size = int_value(match.get("Outcome_Sample_Size", 0))
        dispersion = float_value(match.get("Outcome_Dispersion_Pips", 0.0))
        tier = text_value(match.get("Reference_Tier", ""))
        return {
            **_scenario_fields(lookup_number, scenario),
            "Matched_Research_Reference_ID": text_value(match.get("Research_Reference_ID", "")),
            "Matched_Outcome_Profile_ID": text_value(match.get("Outcome_Profile_ID", "")),
            "Matched_Context_Granularity": text_value(match.get("Context_Granularity", "")),
            "Matched_Reference_Tier": tier,
            "Matched_Outcome_Sample_Size": sample_size,
            "Matched_Outcome_Dispersion_Pips": dispersion,
            "Matched_Directional_Behavior_Class": text_value(match.get("Directional_Behavior_Class", "")),
            "Matched_Dominant_Observed_Direction": text_value(match.get("Dominant_Observed_Direction", "")),
            "Matched_Excursion_Behavior_Class": text_value(match.get("Excursion_Behavior_Class", "")),
            "Matched_Horizon_Stability_Class": text_value(match.get("Horizon_Stability_Class", "")),
            "Reference_Match_Level": match_level,
            "Reference_Match_Quality_Class": classify_match_quality(match_level, sample_size, dispersion, config),
            "Reference_Evidence_Quality_Class": classify_evidence_quality(tier, sample_size, dispersion, config),
            "Lookup_Diagnostic": f"Matched reference using {match_level}.",
        }
    return _empty_lookup(lookup_number, scenario, "NO_REFERENCE_MATCH", "No descriptive reference matched this scenario.")


def _filter(frame: pd.DataFrame, scenario: pd.Series, match_level: str) -> pd.DataFrame:
    matches = _match_column(frame, "H4_Transition_Label", scenario["H4_Transition_Label"])
    matches = _match_column(matches, "Forward_Horizon_H4_Candles", scenario["Forward_Horizon_H4_Candles"])
    if match_level == "EXACT_D1_STATE_REGIME_CONTEXT_MATCH":
        matches = _match_column(matches, "D1_Market_State", scenario["D1_Market_State"])
        matches = _match_column(matches, "D1_Regime_Label", scenario["D1_Regime_Label"])
    elif match_level == "D1_REGIME_CONTEXT_MATCH":
        matches = _match_column(matches, "D1_Regime_Label", scenario["D1_Regime_Label"])
    elif match_level == "D1_MARKET_STATE_CONTEXT_MATCH":
        matches = _match_column(matches, "D1_Market_State", scenario["D1_Market_State"])
    return matches


def _match_column(frame: pd.DataFrame, column_name: str, expected: object) -> pd.DataFrame:
    column = find_column(frame, [column_name])
    if column is None:
        return pd.DataFrame(columns=frame.columns)
    return frame[frame[column].map(lambda item: same_text(item, expected))]


def _best(matches: pd.DataFrame) -> pd.Series:
    ranked = matches.copy()
    tier_order = {"CORE_REFERENCE": 0, "SUPPORTING_REFERENCE": 1, "WATCHLIST_REFERENCE": 2}
    ranked["_tier_order"] = ranked.get("Reference_Tier", "").map(lambda item: tier_order.get(text_value(item).upper(), 9))
    ranked["_sample_order"] = ranked.get("Outcome_Sample_Size", 0).map(int_value)
    return ranked.sort_values(["_tier_order", "_sample_order"], ascending=[True, False]).iloc[0]


def _empty_lookup(lookup_number: int, scenario: pd.Series, match_level: str, diagnostic: str) -> dict[str, object]:
    return {
        **_scenario_fields(lookup_number, scenario),
        "Matched_Research_Reference_ID": "",
        "Matched_Outcome_Profile_ID": "",
        "Matched_Context_Granularity": "",
        "Matched_Reference_Tier": "",
        "Matched_Outcome_Sample_Size": 0,
        "Matched_Outcome_Dispersion_Pips": 0.0,
        "Matched_Directional_Behavior_Class": "",
        "Matched_Dominant_Observed_Direction": "",
        "Matched_Excursion_Behavior_Class": "",
        "Matched_Horizon_Stability_Class": "",
        "Reference_Match_Level": match_level,
        "Reference_Match_Quality_Class": "INPUT_MISSING"
        if match_level == "INPUT_MISSING"
        else "NO_USABLE_REFERENCE_MATCH",
        "Reference_Evidence_Quality_Class": "INPUT_MISSING"
        if match_level == "INPUT_MISSING"
        else "INSUFFICIENT_REFERENCE_EVIDENCE",
        "Lookup_Diagnostic": diagnostic,
    }


def _scenario_fields(lookup_number: int, scenario: pd.Series) -> dict[str, object]:
    return {
        "Reference_Lookup_ID": f"LOOKUP_{lookup_number:06d}",
        "Usage_Scenario_ID": scenario["Usage_Scenario_ID"],
        "Symbol": scenario["Symbol"],
        "H4_Timeframe": scenario["H4_Timeframe"],
        "D1_Timeframe": scenario["D1_Timeframe"],
        "H4_Transition_Label": scenario["H4_Transition_Label"],
        "D1_Market_State": scenario["D1_Market_State"],
        "D1_Regime_Label": scenario["D1_Regime_Label"],
        "D1_Structure_Direction": scenario["D1_Structure_Direction"],
        "Forward_Horizon_H4_Candles": scenario["Forward_Horizon_H4_Candles"],
    }
