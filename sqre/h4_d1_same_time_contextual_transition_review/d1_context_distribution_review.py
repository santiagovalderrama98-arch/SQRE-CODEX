"""Review H4 transition distribution across D1 market states."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)


MARKET_STATE_DISTRIBUTION_COLUMNS = [
    "H4_Transition_Label",
    "D1_Market_State",
    "Context_Row_Count",
    "Transition_Total_Count",
    "Context_Share_Within_Transition",
    "Distribution_Class",
    "Distribution_Diagnostic",
]


def build_market_state_distribution_review(
    profiles: pd.DataFrame,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> pd.DataFrame:
    return _build_distribution(
        profiles,
        context_column="D1_Market_State",
        output_columns=MARKET_STATE_DISTRIBUTION_COLUMNS,
        config=config,
    )


def classify_distribution(transition_total: int, share: float, distinct_contexts: int, config) -> str:
    if transition_total <= 0:
        return "INPUT_MISSING"
    if transition_total < config.minimum_transition_sample_size:
        return "D1_CONTEXT_SAMPLE_CONSTRAINED"
    if share >= config.concentration_ratio_threshold:
        return "D1_CONTEXT_CONCENTRATED"
    if distinct_contexts <= 2:
        return "D1_CONTEXT_MIXED"
    return "D1_CONTEXT_DISPERSED"


def _build_distribution(
    profiles: pd.DataFrame,
    *,
    context_column: str,
    output_columns: list[str],
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=output_columns)
    grouped = profiles.groupby(["H4_Transition_Label", context_column], dropna=False)["Context_Row_Count"].sum()
    grouped = grouped.reset_index()
    transition_totals = profiles.groupby("H4_Transition_Label")["Context_Row_Count"].sum().to_dict()
    distinct_counts = profiles.groupby("H4_Transition_Label")[context_column].nunique(dropna=False).to_dict()

    rows = []
    for _, row in grouped.iterrows():
        label = row["H4_Transition_Label"]
        count = int(row["Context_Row_Count"])
        total = int(transition_totals.get(label, 0))
        share = round(count / total, 6) if total else 0.0
        distribution_class = classify_distribution(total, share, int(distinct_counts.get(label, 0)), config)
        rows.append(
            {
                "H4_Transition_Label": label,
                context_column: row[context_column],
                "Context_Row_Count": count,
                "Transition_Total_Count": total,
                "Context_Share_Within_Transition": share,
                "Distribution_Class": distribution_class,
                "Distribution_Diagnostic": _diagnostic(distribution_class),
            }
        )
    return pd.DataFrame(rows, columns=output_columns)


def _diagnostic(distribution_class: str) -> str:
    if distribution_class == "D1_CONTEXT_CONCENTRATED":
        return "H4 transition observations are concentrated under one D1 context."
    if distribution_class == "D1_CONTEXT_MIXED":
        return "H4 transition observations are mixed across limited D1 contexts."
    if distribution_class == "D1_CONTEXT_DISPERSED":
        return "H4 transition observations are dispersed across D1 contexts."
    if distribution_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "H4 transition sample is constrained for distribution review."
    return "Distribution input is missing."
