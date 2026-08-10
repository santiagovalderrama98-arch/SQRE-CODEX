"""Build the reference stability scorecard."""

from __future__ import annotations

import pandas as pd


SCORECARD_COLUMNS = [
    "Stability_Dimension",
    "Stable_Count",
    "Partial_Count",
    "Unstable_Or_Limited_Count",
    "Input_Missing_Count",
    "Dominant_Stability_Class",
    "Dimension_Diagnostic",
]


def build_stability_scorecard(
    population: pd.DataFrame,
    horizon: pd.DataFrame,
    granularity: pd.DataFrame,
    sample: pd.DataFrame,
    dispersion: pd.DataFrame,
    directional: pd.DataFrame,
    match_level: pd.DataFrame,
    dashboard: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        _row("Reference Population", population, "Reference_Population_Class", {"REFERENCE_POPULATION_AVAILABLE"}, {"REFERENCE_POPULATION_PARTIAL"}),
        _row("Horizon Stability", horizon, "Horizon_Stability_Class", {"STABLE_ACROSS_HORIZONS"}, {"PARTIAL_HORIZON_STABILITY"}),
        _row("Granularity Stability", granularity, "Granularity_Stability_Class", {"STABLE_GRANULARITY_CONTEXT"}, {"PARTIAL_GRANULARITY_CONTEXT"}),
        _row("Sample Adequacy", sample, "Sample_Adequacy_Class", {"STABLE_SAMPLE_SIZE"}, {"USABLE_SAMPLE_SIZE"}),
        _row("Dispersion Stability", dispersion, "Dispersion_Stability_Class", {"STABLE_DISPERSION"}, {"USABLE_DISPERSION"}),
        _row("Directional Consistency", directional, "Directional_Consistency_Class", {"DIRECTIONAL_BEHAVIOR_CONSISTENT"}, {"MIXED_DIRECTIONAL_BEHAVIOR"}),
        _row("Match Level Stability", match_level, "Match_Level_Stability_Class", {"STABLE_MATCH_LEVEL_USAGE"}, {"PARTIAL_MATCH_LEVEL_USAGE"}),
        _row("Dashboard Reference Stability", dashboard, "Dashboard_Reference_Stability_Class", {"DASHBOARD_REFERENCES_STABLE_FOR_REVIEW"}, {"DASHBOARD_REFERENCES_PARTIAL_FOR_REVIEW"}),
    ]
    return pd.DataFrame(rows, columns=SCORECARD_COLUMNS)


def _row(
    dimension: str,
    frame: pd.DataFrame,
    column: str,
    stable_values: set[str],
    partial_values: set[str],
) -> dict[str, object]:
    if frame.empty or column not in frame.columns:
        return _record(dimension, 0, 0, 0, 1, "INPUT_MISSING")
    values = frame[column].astype(str).str.upper()
    input_missing = int((values == "INPUT_MISSING").sum())
    stable = int(values.isin(stable_values).sum())
    partial = int(values.isin(partial_values).sum())
    limited = max(int(len(values) - stable - partial - input_missing), 0)
    dominant = _dominant(values)
    return _record(dimension, stable, partial, limited, input_missing, dominant)


def _record(dimension: str, stable: int, partial: int, limited: int, missing: int, dominant: str) -> dict[str, object]:
    return {
        "Stability_Dimension": dimension,
        "Stable_Count": stable,
        "Partial_Count": partial,
        "Unstable_Or_Limited_Count": limited,
        "Input_Missing_Count": missing,
        "Dominant_Stability_Class": dominant,
        "Dimension_Diagnostic": f"{dimension} dominant class is {dominant}.",
    }


def _dominant(values: pd.Series) -> str:
    if values.empty:
        return "INPUT_MISSING"
    counts = values.value_counts()
    return str(counts.index[0]) if len(counts) else "INPUT_MISSING"
