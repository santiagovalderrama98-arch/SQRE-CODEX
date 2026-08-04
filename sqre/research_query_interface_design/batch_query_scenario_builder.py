"""Build batch research query source rows."""

from __future__ import annotations

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_reference_store_usage_review.reference_query_builder import int_value, row_value, text_value


def build_batch_query_source_rows(
    usage_scenarios: pd.DataFrame,
    transition_alignment: pd.DataFrame,
    reference_store: pd.DataFrame,
    config: ResearchQueryInterfaceDesignConfig,
) -> list[dict[str, object]]:
    if not usage_scenarios.empty:
        return _from_usage_scenarios(usage_scenarios, config)
    if not transition_alignment.empty:
        return _from_alignment(transition_alignment, config)
    if not reference_store.empty:
        return _from_reference_store(reference_store, config)
    return [_missing_query(config)]


def _from_usage_scenarios(frame: pd.DataFrame, config: ResearchQueryInterfaceDesignConfig) -> list[dict[str, object]]:
    rows = []
    for _, source in frame.iterrows():
        rows.append(
            {
                **_base(source, config),
                "Research_Query_Mode": "BATCH_HISTORICAL_RESEARCH_QUERY",
                "Requested_Forward_Horizon_H4_Candles": int_value(
                    row_value(source, ["Forward_Horizon_H4_Candles", "Requested_Forward_Horizon_H4_Candles"], 0)
                ),
                "Query_Source": "REFERENCE_USAGE_BATCH_QUERY",
            }
        )
        if len(rows) >= config.maximum_query_scenarios:
            break
    return rows


def _from_alignment(frame: pd.DataFrame, config: ResearchQueryInterfaceDesignConfig) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
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
                    "Research_Query_Mode": "BATCH_HISTORICAL_RESEARCH_QUERY",
                    "Requested_Forward_Horizon_H4_Candles": horizon,
                    "Query_Source": "HISTORICAL_ALIGNMENT_BATCH_QUERY",
                }
            )
            if len(rows) >= config.maximum_query_scenarios:
                return rows
    return rows if rows else [_missing_query(config)]


def _from_reference_store(frame: pd.DataFrame, config: ResearchQueryInterfaceDesignConfig) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
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
                "Research_Query_Mode": "REFERENCE_STORE_DERIVED_RESEARCH_QUERY",
                "Requested_Forward_Horizon_H4_Candles": horizon,
                "Query_Source": "REFERENCE_STORE_DERIVED_QUERY",
            }
        )
        if len(rows) >= config.maximum_query_scenarios:
            break
    return rows if rows else [_missing_query(config)]


def _base(row: pd.Series, config: ResearchQueryInterfaceDesignConfig) -> dict[str, object]:
    return {
        "Symbol": text_value(row_value(row, ["Symbol"], config.symbol), config.symbol),
        "H4_Timeframe": text_value(row_value(row, ["H4_Timeframe"], config.h4_timeframe), config.h4_timeframe),
        "D1_Timeframe": text_value(row_value(row, ["D1_Timeframe"], config.d1_timeframe), config.d1_timeframe),
        "H4_Transition_Label": text_value(row_value(row, ["H4_Transition_Label", "Transition_Label"], "")),
        "D1_Market_State": text_value(row_value(row, ["D1_Market_State", "Market_State"], "")),
        "D1_Regime_Label": text_value(row_value(row, ["D1_Regime_Label", "Regime_Label"], "")),
        "D1_Structure_Direction": text_value(row_value(row, ["D1_Structure_Direction", "Structure_Direction"], "")),
    }


def _missing_query(config: ResearchQueryInterfaceDesignConfig) -> dict[str, object]:
    return {
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Research_Query_Mode": "INPUT_MISSING",
        "H4_Transition_Label": "INPUT_MISSING",
        "D1_Market_State": "INPUT_MISSING",
        "D1_Regime_Label": "INPUT_MISSING",
        "D1_Structure_Direction": "INPUT_MISSING",
        "Requested_Forward_Horizon_H4_Candles": 0,
        "Query_Source": "INPUT_MISSING",
    }

