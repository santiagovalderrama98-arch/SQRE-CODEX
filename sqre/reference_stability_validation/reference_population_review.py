"""Reference population review for reference stability validation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.models import numeric_series, text_series, tier_counts


POPULATION_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Watchlist_Reference_Count",
    "Distinct_Context_Granularity_Count",
    "Distinct_Forward_Horizon_Count",
    "Reference_Population_Class",
    "Population_Diagnostic",
]


def build_reference_population_review(
    config: ReferenceStabilityValidationConfig,
    reference_store: pd.DataFrame,
    missing_required_inputs: bool,
) -> pd.DataFrame:
    if missing_required_inputs:
        return pd.DataFrame([_row(config, 0, 0, 0, 0, 0, 0, "INPUT_MISSING", "Required reference inputs are missing.")])
    reference_count = len(reference_store)
    core, supporting, watchlist = tier_counts(reference_store)
    distinct_granularity = int(text_series(reference_store, ["Context_Granularity"]).replace("", pd.NA).dropna().nunique())
    distinct_horizon = int(numeric_series(reference_store, ["Forward_Horizon_H4_Candles"]).replace(0, pd.NA).dropna().nunique())
    if reference_count == 0:
        population_class = "REFERENCE_POPULATION_EMPTY"
        diagnostic = "No included reference rows are available."
    elif core + supporting > 0 and distinct_granularity > 0 and distinct_horizon > 0:
        population_class = "REFERENCE_POPULATION_AVAILABLE"
        diagnostic = "Reference population contains included historical reference rows."
    else:
        population_class = "REFERENCE_POPULATION_PARTIAL"
        diagnostic = "Reference population is available but incomplete across tiers or context dimensions."
    return pd.DataFrame(
        [
            _row(
                config,
                reference_count,
                core,
                supporting,
                watchlist,
                distinct_granularity,
                distinct_horizon,
                population_class,
                diagnostic,
            )
        ],
        columns=POPULATION_COLUMNS,
    )


def _row(
    config: ReferenceStabilityValidationConfig,
    reference_count: int,
    core: int,
    supporting: int,
    watchlist: int,
    distinct_granularity: int,
    distinct_horizon: int,
    population_class: str,
    diagnostic: str,
) -> dict[str, object]:
    return {
        "Symbol": config.symbol,
        "H4_Timeframe": config.h4_timeframe,
        "D1_Timeframe": config.d1_timeframe,
        "Reference_Count": reference_count,
        "Core_Reference_Count": core,
        "Supporting_Reference_Count": supporting,
        "Watchlist_Reference_Count": watchlist,
        "Distinct_Context_Granularity_Count": distinct_granularity,
        "Distinct_Forward_Horizon_Count": distinct_horizon,
        "Reference_Population_Class": population_class,
        "Population_Diagnostic": diagnostic,
    }
