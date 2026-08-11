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
    (
        "STABLE_EVIDENCE",
        "STABLE_EVIDENCE_INDICATOR",
        "LOW_STABILITY_WARNING",
        "Stable evidence",
        "Evidence has acceptable sample and dispersion for historical research review.",
        "Stable evidence does not imply directional edge.",
    ),
    (
        "PARTIAL_EVIDENCE",
        "PARTIAL_EVIDENCE_INDICATOR",
        "MODERATE_STABILITY_WARNING",
        "Partial evidence",
        "Evidence exists but depends on horizon, granularity, or context limitations.",
        "Compare across horizons and context levels carefully.",
    ),
    (
        "STABILITY_WARNING",
        "WARNING_EVIDENCE_INDICATOR",
        "HIGH_STABILITY_WARNING",
        "Stability warning",
        "Evidence has an important stability constraint.",
        "Review diagnostic before interpreting.",
    ),
    (
        "DOCUMENTATION_ONLY",
        "DOCUMENTATION_ONLY_INDICATOR",
        "HIGH_STABILITY_WARNING",
        "Documentation only",
        "Use only to understand system limitations.",
        "Do not use as a primary research reference.",
    ),
    (
        "FALLBACK_DEPENDENT",
        "WARNING_EVIDENCE_INDICATOR",
        "MODERATE_STABILITY_WARNING",
        "Fallback dependent",
        "Exact context was unavailable and a broader context was used.",
        "Evidence is available but less specific.",
    ),
    (
        "DIRECTIONALLY_UNSTABLE",
        "WARNING_EVIDENCE_INDICATOR",
        "HIGH_STABILITY_WARNING",
        "Directionally unstable",
        "Historical behavior was mixed across direction classes.",
        "Do not interpret as directional bias.",
    ),
    (
        "HORIZON_PARTIAL",
        "PARTIAL_EVIDENCE_INDICATOR",
        "MODERATE_STABILITY_WARNING",
        "Partial horizon",
        "Evidence stability varies across forward horizons.",
        "Review each horizon separately.",
    ),
    (
        "GRANULARITY_PARTIAL",
        "PARTIAL_EVIDENCE_INDICATOR",
        "MODERATE_STABILITY_WARNING",
        "Partial granularity",
        "Specific context granularity may fragment the sample.",
        "Compare specific and broader context levels.",
    ),
    (
        "SAMPLE_STABLE",
        "STABLE_EVIDENCE_INDICATOR",
        "LOW_STABILITY_WARNING",
        "Stable sample",
        "Sample size meets review criteria.",
        "Sample size alone does not imply predictability.",
    ),
    (
        "DISPERSION_STABLE",
        "STABLE_EVIDENCE_INDICATOR",
        "LOW_STABILITY_WARNING",
        "Stable dispersion",
        "Observed dispersion is within review limits.",
        "Stable dispersion does not imply prediction.",
    ),
]


def build_stability_indicator_legend(include: bool) -> pd.DataFrame:
    if not include:
        return pd.DataFrame(columns=LEGEND_COLUMNS)
    return pd.DataFrame([_row(*values) for values in LEGEND_ROWS], columns=LEGEND_COLUMNS)


def _row(
    key: str,
    indicator_class: str,
    severity: str,
    label: str,
    meaning: str,
    caution: str,
) -> dict[str, str]:
    return {
        "Indicator_Key": key,
        "Dashboard_Stability_Indicator_Class": indicator_class,
        "Dashboard_Stability_Severity_Class": severity,
        "Display_Label": label,
        "Display_Description": f"{label} indicator for manual dashboard review.",
        "Manual_Research_Meaning": meaning,
        "Required_Caution": caution,
        "What_Not_To_Infer": "Do not infer favorable/unfavorable context, profitability, or operational action.",
    }
