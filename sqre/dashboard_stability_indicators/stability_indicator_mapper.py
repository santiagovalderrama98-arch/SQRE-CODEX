"""Map documentation classes to dashboard stability indicators."""

from __future__ import annotations

import pandas as pd


INDICATOR_MAP_COLUMNS = [
    "Stability_Dimension",
    "Observed_Stability_Class",
    "Documentation_Class",
    "Evidence_Usage_Policy_Class",
    "Dashboard_Stability_Indicator_Class",
    "Dashboard_Stability_Severity_Class",
    "Indicator_Label",
    "Indicator_Diagnostic",
]


def build_stability_indicator_map(interpretation_guide: pd.DataFrame) -> pd.DataFrame:
    if interpretation_guide.empty:
        return pd.DataFrame(columns=INDICATOR_MAP_COLUMNS)
    rows = []
    for _, row in interpretation_guide.iterrows():
        doc_class = str(row.get("Documentation_Class", "INPUT_MISSING"))
        indicator_class, severity, label = indicator_for_documentation_class(doc_class)
        rows.append(
            {
                "Stability_Dimension": row.get("Stability_Dimension", ""),
                "Observed_Stability_Class": row.get("Observed_Stability_Class", ""),
                "Documentation_Class": doc_class,
                "Evidence_Usage_Policy_Class": row.get("Evidence_Usage_Policy_Class", ""),
                "Dashboard_Stability_Indicator_Class": indicator_class,
                "Dashboard_Stability_Severity_Class": severity,
                "Indicator_Label": label,
                "Indicator_Diagnostic": f"{row.get('Stability_Dimension', '')} mapped to {indicator_class}.",
            }
        )
    return pd.DataFrame(rows, columns=INDICATOR_MAP_COLUMNS)


def indicator_for_documentation_class(documentation_class: str) -> tuple[str, str, str]:
    value = str(documentation_class).upper()
    if value == "DOCUMENTED_STABLE_EVIDENCE":
        return "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING", "Stable evidence"
    if value == "DOCUMENTED_PARTIAL_EVIDENCE":
        return "PARTIAL_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING", "Partial evidence"
    if value == "DOCUMENTED_UNSTABLE_EVIDENCE":
        return "WARNING_EVIDENCE_INDICATOR", "HIGH_STABILITY_WARNING", "Stability warning"
    if value == "DOCUMENTED_CONSTRAINED_EVIDENCE":
        return "DOCUMENTATION_ONLY_INDICATOR", "HIGH_STABILITY_WARNING", "Documentation only"
    return "INPUT_MISSING", "INPUT_MISSING", "Input missing"
