"""Build synthetic usage scenarios for the research reference store."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.reference_query_builder import int_value, row_value, text_value


SCENARIO_COLUMNS = [
    "Usage_Scenario_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Forward_Horizon_H4_Candles",
    "Scenario_Source",
    "Scenario_Diagnostic",
]


def build_usage_scenarios(
    transition_alignment: pd.DataFrame,
    reference_store: pd.DataFrame,
    config: ResearchReferenceStoreUsageReviewConfig,
) -> pd.DataFrame:
    if not transition_alignment.empty:
        return _from_alignment(transition_alignment, config)
    if not reference_store.empty:
        return _from_reference_store(reference_store, config)
    return pd.DataFrame([_missing_scenario(config)], columns=SCENARIO_COLUMNS)


def _from_alignment(frame: pd.DataFrame, config: ResearchReferenceStoreUsageReviewConfig) -> pd.DataFrame:
    rows = []
    seen: set[tuple[str, str, str, str, int]] = set()
    for _, source in frame.iterrows():
        base = _base(source, config)
        for horizon in config.preferred_horizons:
            key = (
                base["H4_Transition_Label"],
                base["D1_Market_State"],
                base["D1_Regime_Label"],
                base["D1_Structure_Direction"],
                horizon,
            )
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    **base,
                    "Forward_Horizon_H4_Candles": horizon,
                    "Scenario_Source": "HISTORICAL_ALIGNMENT_SCENARIO",
                    "Scenario_Diagnostic": "Scenario derived from same-time H4/D1 transition alignment.",
                }
            )
            if len(rows) >= config.maximum_scenarios:
                return _with_ids(rows)
    return _with_ids(rows) if rows else pd.DataFrame([_missing_scenario(config)], columns=SCENARIO_COLUMNS)


def _from_reference_store(frame: pd.DataFrame, config: ResearchReferenceStoreUsageReviewConfig) -> pd.DataFrame:
    rows = []
    seen: set[tuple[str, str, str, str, int]] = set()
    for _, source in frame.iterrows():
        base = _base(source, config)
        horizon = int_value(row_value(source, ["Forward_Horizon_H4_Candles"], 0))
        key = (
            base["H4_Transition_Label"],
            base["D1_Market_State"],
            base["D1_Regime_Label"],
            base["D1_Structure_Direction"],
            horizon,
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                **base,
                "Forward_Horizon_H4_Candles": horizon,
                "Scenario_Source": "REFERENCE_STORE_DERIVED_SCENARIO",
                "Scenario_Diagnostic": "Scenario derived from existing research reference rows.",
            }
        )
        if len(rows) >= config.maximum_scenarios:
            break
    return _with_ids(rows) if rows else pd.DataFrame([_missing_scenario(config)], columns=SCENARIO_COLUMNS)


def _base(row: pd.Series, config: ResearchReferenceStoreUsageReviewConfig) -> dict[str, str]:
    return {
        "Symbol": text_value(row_value(row, ["Symbol"], config.symbol), config.symbol),
        "H4_Timeframe": text_value(row_value(row, ["H4_Timeframe"], config.h4_timeframe), config.h4_timeframe),
        "D1_Timeframe": text_value(row_value(row, ["D1_Timeframe"], config.d1_timeframe), config.d1_timeframe),
        "H4_Transition_Label": text_value(row_value(row, ["H4_Transition_Label", "Transition_Label"], "UNKNOWN")),
        "D1_Market_State": text_value(row_value(row, ["D1_Market_State", "Market_State"], "UNKNOWN")),
        "D1_Regime_Label": text_value(row_value(row, ["D1_Regime_Label", "Regime_Label"], "UNKNOWN")),
        "D1_Structure_Direction": text_value(row_value(row, ["D1_Structure_Direction", "Structure_Direction"], "UNKNOWN")),
    }


def _with_ids(rows: list[dict[str, object]]) -> pd.DataFrame:
    records = [{"Usage_Scenario_ID": f"USAGE_{index:06d}", **row} for index, row in enumerate(rows, start=1)]
    return pd.DataFrame(records, columns=SCENARIO_COLUMNS)


def _missing_scenario(config: ResearchReferenceStoreUsageReviewConfig) -> dict[str, object]:
    return {
        "Usage_Scenario_ID": "USAGE_000000",
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "H4_Transition_Label": "INPUT_MISSING",
        "D1_Market_State": "INPUT_MISSING",
        "D1_Regime_Label": "INPUT_MISSING",
        "D1_Structure_Direction": "INPUT_MISSING",
        "Forward_Horizon_H4_Candles": 0,
        "Scenario_Source": "INPUT_MISSING",
        "Scenario_Diagnostic": "No alignment scenarios or reference-store rows were available.",
    }
