"""Build research query request table."""

from __future__ import annotations

import pandas as pd

from sqre.research_query_interface_design.batch_query_scenario_builder import build_batch_query_source_rows
from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.query_validation import validate_query_request


REQUEST_COLUMNS = [
    "Research_Query_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Research_Query_Mode",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Requested_Forward_Horizon_H4_Candles",
    "Query_Source",
    "Query_Validation_Status",
    "Query_Diagnostic",
]


def build_query_requests(
    usage_scenarios: pd.DataFrame,
    transition_alignment: pd.DataFrame,
    reference_store: pd.DataFrame,
    config: ResearchQueryInterfaceDesignConfig,
) -> pd.DataFrame:
    rows = [_single_query(config)] if config.has_single_query else build_batch_query_source_rows(
        usage_scenarios, transition_alignment, reference_store, config
    )
    records = []
    for sequence, row in enumerate(rows, start=1):
        record = {"Research_Query_ID": f"RQ_{sequence:06d}", **row}
        status, diagnostic = validate_query_request(pd.Series(record))
        record["Query_Validation_Status"] = status
        record["Query_Diagnostic"] = diagnostic
        records.append(record)
    return pd.DataFrame(records, columns=REQUEST_COLUMNS)


def _single_query(config: ResearchQueryInterfaceDesignConfig) -> dict[str, object]:
    return {
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Research_Query_Mode": "SINGLE_RESEARCH_QUERY",
        "H4_Transition_Label": config.query_h4_transition_label or "",
        "D1_Market_State": config.query_d1_market_state or "",
        "D1_Regime_Label": config.query_d1_regime_label or "",
        "D1_Structure_Direction": config.query_d1_structure_direction or "",
        "Requested_Forward_Horizon_H4_Candles": config.query_forward_horizon or 0,
        "Query_Source": "USER_SUPPLIED_QUERY",
    }

