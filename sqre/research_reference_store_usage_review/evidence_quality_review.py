"""Evidence quality review for reference-store usage."""

from __future__ import annotations

import pandas as pd


EVIDENCE_QUALITY_COLUMNS = [
    "Reference_Evidence_Quality_Class",
    "Lookup_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Evidence_Quality_Diagnostic",
]


def build_evidence_quality_review(lookup_results: pd.DataFrame) -> pd.DataFrame:
    if lookup_results.empty:
        return pd.DataFrame([_empty("INPUT_MISSING", "No lookup rows were produced.")], columns=EVIDENCE_QUALITY_COLUMNS)
    rows = []
    for evidence_class, group in lookup_results.groupby("Reference_Evidence_Quality_Class", sort=False):
        sample = pd.to_numeric(group["Matched_Outcome_Sample_Size"], errors="coerce").fillna(0)
        dispersion = pd.to_numeric(group["Matched_Outcome_Dispersion_Pips"], errors="coerce").fillna(0)
        rows.append(
            {
                "Reference_Evidence_Quality_Class": evidence_class,
                "Lookup_Count": len(group),
                "Core_Reference_Count": int((group["Reference_Evidence_Quality_Class"] == "CORE_REFERENCE_EVIDENCE").sum()),
                "Supporting_Reference_Count": int(
                    (group["Reference_Evidence_Quality_Class"] == "SUPPORTING_REFERENCE_EVIDENCE").sum()
                ),
                "Average_Outcome_Sample_Size": round(float(sample.mean()), 4) if not sample.empty else 0.0,
                "Average_Outcome_Dispersion_Pips": round(float(dispersion.mean()), 4) if not dispersion.empty else 0.0,
                "Evidence_Quality_Diagnostic": f"{len(group)} lookup rows classified as {evidence_class}.",
            }
        )
    return pd.DataFrame(rows, columns=EVIDENCE_QUALITY_COLUMNS)


def _empty(evidence_class: str, diagnostic: str) -> dict[str, object]:
    return {
        "Reference_Evidence_Quality_Class": evidence_class,
        "Lookup_Count": 0,
        "Core_Reference_Count": 0,
        "Supporting_Reference_Count": 0,
        "Average_Outcome_Sample_Size": 0.0,
        "Average_Outcome_Dispersion_Pips": 0.0,
        "Evidence_Quality_Diagnostic": diagnostic,
    }
