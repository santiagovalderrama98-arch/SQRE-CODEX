"""Build dashboard reading guide rows."""

from __future__ import annotations

import pandas as pd


DASHBOARD_GUIDE_COLUMNS = [
    "Dashboard_Element",
    "Dashboard_Reading_Guide_Class",
    "What_It_Shows",
    "How_To_Read_It",
    "Required_Caution",
    "What_Not_To_Infer",
    "Guide_Diagnostic",
]

DASHBOARD_ELEMENTS = [
    "Snapshot Context",
    "Reference Cards",
    "Evidence Panel",
    "Behavior Panel",
    "Fallback Trace",
    "Diagnostic Panel",
    "Readiness Flag",
    "Coverage Ratio",
    "Match Level",
    "Sample Size",
    "Dispersion",
    "Directional Behavior",
]


def build_dashboard_reading_guide(include: bool, dashboard_cards: pd.DataFrame) -> pd.DataFrame:
    if not include:
        return pd.DataFrame(columns=DASHBOARD_GUIDE_COLUMNS)
    card_count = len(dashboard_cards)
    klass = "DASHBOARD_GUIDE_READY" if card_count > 0 else "DASHBOARD_GUIDE_PARTIAL"
    return pd.DataFrame([_row(element, klass, card_count) for element in DASHBOARD_ELEMENTS], columns=DASHBOARD_GUIDE_COLUMNS)


def _row(element: str, klass: str, card_count: int) -> dict[str, object]:
    return {
        "Dashboard_Element": element,
        "Dashboard_Reading_Guide_Class": klass,
        "What_It_Shows": _what_it_shows(element),
        "How_To_Read_It": _how_to_read(element),
        "Required_Caution": "Dashboard cards are research references, not trading instructions.",
        "What_Not_To_Infer": "Do not infer favorable/unfavorable context, profitability, or operational action.",
        "Guide_Diagnostic": f"{element} guide built with dashboard_card_count={card_count}.",
    }


def _what_it_shows(element: str) -> str:
    return {
        "Snapshot Context": "The latest documented H4/D1 research context snapshot.",
        "Reference Cards": "Matched historical reference rows selected for manual review.",
        "Evidence Panel": "Reference sample and dispersion evidence.",
        "Behavior Panel": "Historical behavior descriptors from the reference store.",
        "Fallback Trace": "Whether broader match levels were needed.",
        "Diagnostic Panel": "Input and readiness diagnostics.",
        "Readiness Flag": "Research readiness of the documented reference set.",
        "Coverage Ratio": "How much of the available reference context was matched.",
        "Match Level": "Granularity of the selected reference match.",
        "Sample Size": "Historical sample count behind the reference.",
        "Dispersion": "Historical variation of the measured outcome.",
        "Directional Behavior": "Observed direction labels from descriptive research outputs.",
    }[element]


def _how_to_read(element: str) -> str:
    if element in {"Sample Size", "Dispersion"}:
        return "Read as evidence quality context; stable values do not imply predictive edge."
    if element == "Directional Behavior":
        return "Read direction labels as descriptive historical tags only."
    if element == "Fallback Trace":
        return "Read fallback rows as evidence warnings for broader matching."
    return "Read as descriptive research context for manual inspection."
