"""Refinement recommendations for manual dashboard usability."""

from __future__ import annotations

import pandas as pd


REFINEMENT_RECOMMENDATION_COLUMNS = [
    "Recommendation_ID",
    "Recommendation_Category",
    "Recommendation_Priority",
    "Recommendation_Text",
    "Rationale",
    "Implementation_Scope",
]


def build_refinement_recommendations(
    panel_completeness: pd.DataFrame,
    panel_readability: pd.DataFrame,
    redundancy_review: pd.DataFrame,
    scope_safety: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for _, row in panel_completeness.iterrows():
        if row.get("Panel_Completeness_Class") in {"PANEL_EMPTY", "INPUT_MISSING"}:
            records.append(
                _record(
                    "CONTEXT_VISIBILITY",
                    "HIGH",
                    f"Restore visible content for {row.get('Panel_Name')}.",
                    str(row.get("Completeness_Diagnostic", "")),
                    "FUTURE_DASHBOARD_PHASE",
                )
            )
    for _, row in panel_readability.iterrows():
        if row.get("Readability_Class") == "LOW_READABILITY":
            records.append(
                _record(
                    "HTML_READABILITY",
                    "MEDIUM",
                    f"Reduce field density or add clearer labels for {row.get('Panel_Name')}.",
                    str(row.get("Readability_Diagnostic", "")),
                    "CURRENT_PHASE_REFINED_HTML",
                )
            )
    if (redundancy_review.get("Potential_Redundancy_Class", pd.Series(dtype=str)) == "POSSIBLY_REDUNDANT").any():
        records.append(
            _record(
                "FIELD_REDUCTION",
                "MEDIUM",
                "Review repeated fields before a later dashboard phase.",
                "Repeated fields can make manual research review slower.",
                "FUTURE_DASHBOARD_PHASE",
            )
        )
    if (scope_safety.get("Scope_Safety_Class", pd.Series(dtype=str)) == "SCOPE_VIOLATION").any():
        records.append(
            _record(
                "SCOPE_SAFETY",
                "HIGH",
                "Remove unsafe operational language from reviewed dashboard text.",
                "The dashboard must remain descriptive and research-only.",
                "CURRENT_PHASE_REFINED_HTML",
            )
        )
    if not records:
        records.append(
            _record(
                "DOCUMENTATION_ONLY",
                "LOW",
                "Maintain manual review notes for repeated research use.",
                "Dashboard inputs appear usable for manual descriptive review.",
                "DOCUMENTATION_ONLY",
            )
        )
    for index, record in enumerate(records, start=1):
        record["Recommendation_ID"] = f"DASH_RECO_{index:06d}"
    return pd.DataFrame(records, columns=REFINEMENT_RECOMMENDATION_COLUMNS)


def _record(
    category: str,
    priority: str,
    text: str,
    rationale: str,
    implementation_scope: str,
) -> dict[str, object]:
    return {
        "Recommendation_ID": "",
        "Recommendation_Category": category,
        "Recommendation_Priority": priority,
        "Recommendation_Text": text,
        "Rationale": rationale,
        "Implementation_Scope": implementation_scope,
    }
