"""Build dashboard stability indicator legend."""

from __future__ import annotations

import pandas as pd


LEGEND_COLUMNS = [
    "Indicator_Key",
    "Dashboard_Stability_Indicator_Class",
    "Dashboard_Stability_Severity_Class",
    "Display_Label",
    "Display_Description",
    "Manual_Research_Meaning",
    "Required_Caution",
    "What_Not_To_Infer",
]

LEGEND_ROWS = [
    ("STABLE_EVIDENCE", "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING", "Stable evidence"),
    ("PARTIAL_EVIDENCE", "PARTIAL_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING", "Partial evidence"),
    ("STABILITY_WARNING", "WARNING_EVIDENCE_INDICATOR", "HIGH_STABILITY_WARNING", "Stability warning"),
    ("DOCUMENTATION_ONLY", "DOCUMENTATION_ONLY_INDICATOR", "HIGH_STABILITY_WARNING", "Documentation only"),
    ("FALLBACK_DEPENDENT", "WARNING_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING", "Fallback dependent"),
    ("DIRECTIONALLY_UNSTABLE", "WARNING_EVIDENCE_INDICATOR", "HIGH_STABILITY_WARNING", "Directionally unstable"),
    ("HORIZON_PARTIAL", "PARTIAL_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING", "Partial horizon"),
    ("GRANULARITY_PARTIAL", "PARTIAL_EVIDENCE_INDICATOR", "MODERATE_STABILITY_WARNING", "Partial granularity"),
    ("SAMPLE_STABLE", "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING", "Stable sample"),
    ("DISPERSION_STABLE", "STABLE_EVIDENCE_INDICATOR", "LOW_STABILITY_WARNING", "Stable dispersion"),
]


def build_stability_indicator_legend(include: bool) -> pd.DataFrame:
    if not include:
        return pd.DataFrame(columns=LEGEND_COLUMNS)
    return pd.DataFrame([_row(*values) for values in LEGEND_ROWS], columns=LEGEND_COLUMNS)


def _row(key: str, indicator_class: str, severity: str, label: str) -> dict[str, str]:
    return {
        "Indicator_Key": key,
        "Dashboard_Stability_Indicator_Class": indicator_class,
        "Dashboard_Stability_Severity_Class": severity,
        "Display_Label": label,
        "Display_Description": f"{label} indicator for manual dashboard review.",
        "Manual_Research_Meaning": "Describes evidence stability and quality constraints for research review.",
        "Required_Caution": "Indicator is descriptive and research-only.",
        "What_Not_To_Infer": "Do not infer favorable/unfavorable context, profitability, or operational action.",
    }
