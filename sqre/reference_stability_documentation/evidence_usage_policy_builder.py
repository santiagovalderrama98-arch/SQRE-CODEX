"""Build reference evidence usage policy rows."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.models import numeric_value


USAGE_POLICY_COLUMNS = [
    "Evidence_Category",
    "Evidence_Usage_Policy_Class",
    "Allowed_Manual_Research_Use",
    "Required_Warning",
    "Disallowed_Interpretation",
    "Policy_Diagnostic",
]

EVIDENCE_CATEGORIES = [
    "Core References",
    "Supporting References",
    "Partial Horizon References",
    "Partial Granularity References",
    "Stable Sample Groups",
    "Stable Dispersion Groups",
    "Directionally Unstable Groups",
    "Fallback-Dependent Match Levels",
    "Dashboard Reference Cards",
]


def build_evidence_usage_policy(summary: pd.DataFrame) -> pd.DataFrame:
    counts = {
        "Core References": numeric_value(summary, ["Core_Reference_Count"]),
        "Supporting References": numeric_value(summary, ["Supporting_Reference_Count"]),
        "Partial Horizon References": numeric_value(summary, ["Partial_Horizon_Count"]),
        "Partial Granularity References": numeric_value(summary, ["Partial_Granularity_Count"]),
        "Stable Sample Groups": numeric_value(summary, ["Stable_Sample_Group_Count"]),
        "Stable Dispersion Groups": numeric_value(summary, ["Stable_Dispersion_Group_Count"]),
        "Directionally Unstable Groups": numeric_value(summary, ["Unstable_Horizon_Count"], 0),
        "Fallback-Dependent Match Levels": numeric_value(summary, ["Fallback_Dependent_Match_Level_Count"]),
        "Dashboard Reference Cards": numeric_value(summary, ["Dashboard_Reference_Card_Count"]),
    }
    return pd.DataFrame([_row(category, counts[category]) for category in EVIDENCE_CATEGORIES], columns=USAGE_POLICY_COLUMNS)


def _row(category: str, count: int) -> dict[str, object]:
    if category in {"Core References", "Stable Sample Groups", "Stable Dispersion Groups"} and count > 0:
        klass = "SAFE_FOR_MANUAL_RESEARCH_REVIEW"
        allowed = "Use as descriptive manual research reference."
        warning = "Stable evidence does not imply predictive edge."
    elif category in {"Supporting References", "Partial Horizon References", "Partial Granularity References", "Dashboard Reference Cards"} and count > 0:
        klass = "USE_WITH_STABILITY_WARNINGS"
        allowed = "Use for manual research review with visible stability notes."
        warning = "Evidence is partial and should be compared with broader diagnostics."
    elif category in {"Directionally Unstable Groups", "Fallback-Dependent Match Levels"} and count > 0:
        klass = "DOCUMENTATION_ONLY"
        allowed = "Use only to document constraints and evidence limitations."
        warning = "Do not over-interpret unstable or fallback-dependent evidence."
    elif count == 0:
        klass = "DOCUMENTATION_ONLY"
        allowed = "Keep as a documented category with no loaded supporting rows."
        warning = "Input count is zero for this evidence category."
    else:
        klass = "NOT_USABLE_WITHOUT_INPUT_REVIEW"
        allowed = "Requires input completeness review."
        warning = "Required evidence is unavailable."
    return {
        "Evidence_Category": category,
        "Evidence_Usage_Policy_Class": klass,
        "Allowed_Manual_Research_Use": allowed,
        "Required_Warning": warning,
        "Disallowed_Interpretation": "Do not convert this evidence category into operational decisions or favorable/unfavorable labels.",
        "Policy_Diagnostic": f"{category} count={count}; policy={klass}.",
    }
