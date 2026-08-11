"""Build stability interpretation guidance."""

from __future__ import annotations

import pandas as pd


INTERPRETATION_COLUMNS = [
    "Stability_Dimension",
    "Observed_Stability_Class",
    "Documentation_Class",
    "Evidence_Usage_Policy_Class",
    "Interpretation_Text",
    "Manual_Research_Guidance",
    "Required_Caution",
    "Documentation_Diagnostic",
]

REQUIRED_DIMENSIONS = [
    "Reference Population",
    "Horizon Stability",
    "Granularity Stability",
    "Sample Adequacy",
    "Dispersion Stability",
    "Directional Consistency",
    "Match Level Stability",
    "Dashboard Reference Stability",
]


def build_stability_interpretation_guide(scorecard: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in REQUIRED_DIMENSIONS:
        observed = _observed_class(scorecard, dimension)
        documentation_class, policy_class = _map_classes(observed)
        rows.append(
            {
                "Stability_Dimension": dimension,
                "Observed_Stability_Class": observed,
                "Documentation_Class": documentation_class,
                "Evidence_Usage_Policy_Class": policy_class,
                "Interpretation_Text": _interpretation_text(dimension, observed, documentation_class),
                "Manual_Research_Guidance": _manual_guidance(dimension, documentation_class),
                "Required_Caution": _caution(dimension, documentation_class),
                "Documentation_Diagnostic": f"{dimension} documented from stability class {observed}.",
            }
        )
    return pd.DataFrame(rows, columns=INTERPRETATION_COLUMNS)


def _observed_class(scorecard: pd.DataFrame, dimension: str) -> str:
    if scorecard.empty or "Stability_Dimension" not in scorecard.columns or "Dominant_Stability_Class" not in scorecard.columns:
        return "INPUT_MISSING"
    matches = scorecard[scorecard["Stability_Dimension"].astype(str).str.upper() == dimension.upper()]
    if matches.empty:
        return "INPUT_MISSING"
    value = str(matches["Dominant_Stability_Class"].iloc[0]).strip()
    return value or "INPUT_MISSING"


def _map_classes(observed: str) -> tuple[str, str]:
    value = observed.upper()
    if value == "INPUT_MISSING":
        return "INPUT_MISSING", "INPUT_MISSING"
    if value in {"REFERENCE_POPULATION_AVAILABLE", "DASHBOARD_REFERENCES_STABLE_FOR_REVIEW"}:
        return "DOCUMENTED_STABLE_EVIDENCE", "SAFE_FOR_MANUAL_RESEARCH_REVIEW"
    if "STABLE" in value and "UNSTABLE" not in value and "PARTIAL" not in value:
        return "DOCUMENTED_STABLE_EVIDENCE", "SAFE_FOR_MANUAL_RESEARCH_REVIEW"
    if "PARTIAL" in value or "USABLE" in value or "MIXED" in value:
        return "DOCUMENTED_PARTIAL_EVIDENCE", "USE_WITH_STABILITY_WARNINGS"
    if "LOW_SAMPLE" in value or "INPUT_LIMITED" in value or "CONSTRAINED" in value or "FRAGMENTED" in value:
        return "DOCUMENTED_CONSTRAINED_EVIDENCE", "DOCUMENTATION_ONLY"
    return "DOCUMENTED_UNSTABLE_EVIDENCE", "DOCUMENTATION_ONLY"


def _interpretation_text(dimension: str, observed: str, documentation_class: str) -> str:
    if documentation_class == "DOCUMENTED_STABLE_EVIDENCE":
        return f"{dimension} currently has stable historical research diagnostics."
    if documentation_class == "DOCUMENTED_PARTIAL_EVIDENCE":
        return f"{dimension} is available but should be reviewed with stability notes."
    if documentation_class == "DOCUMENTED_CONSTRAINED_EVIDENCE":
        return f"{dimension} is constrained by available historical evidence."
    if documentation_class == "DOCUMENTED_UNSTABLE_EVIDENCE":
        return f"{dimension} shows unstable or fallback-dependent research behavior."
    return f"{dimension} could not be documented because required input was missing ({observed})."


def _manual_guidance(dimension: str, documentation_class: str) -> str:
    if dimension == "Directional Consistency":
        return "Review directional behavior descriptively and avoid over-interpreting direction labels."
    if dimension == "Horizon Stability":
        return "Compare evidence across horizons cautiously when horizon stability is partial."
    if dimension == "Granularity Stability":
        return "Avoid relying on overly specific contexts when granularity fragments the evidence."
    if documentation_class == "DOCUMENTED_STABLE_EVIDENCE":
        return "Use as a stable manual research reference with descriptive context notes."
    if documentation_class == "DOCUMENTED_PARTIAL_EVIDENCE":
        return "Display with stability warnings and compare against broader context rows."
    return "Keep as documentation-only until input completeness or stability improves."


def _caution(dimension: str, documentation_class: str) -> str:
    if dimension == "Sample Adequacy":
        return "Stable sample size does not imply predictive edge."
    if dimension == "Dispersion Stability":
        return "Stable dispersion does not imply predictive edge."
    if documentation_class == "DOCUMENTED_STABLE_EVIDENCE":
        return "Research reference only; no operational decision is produced."
    if documentation_class == "DOCUMENTED_PARTIAL_EVIDENCE":
        return "Partial evidence requires explicit stability warnings."
    return "Do not use beyond descriptive documentation."
