"""Scope safety review for forbidden operational language."""

from __future__ import annotations

import re

import pandas as pd


SCOPE_SAFETY_COLUMNS = [
    "Reviewed_Source",
    "Forbidden_Term",
    "Occurrence_Count",
    "Scope_Safety_Class",
    "Scope_Safety_Diagnostic",
]

FORBIDDEN_TERMS = [
    "buy",
    "sell",
    "entry",
    "exit",
    "trade signal",
    "trade setup",
    "take profit",
    "stop loss",
    "profitable",
    "opportunity",
    "predicts",
    "optimal",
    "should trade",
]

NEGATIVE_CUES = ["does not", "do not", "no ", "not ", "without", "never"]


def build_scope_safety_review(texts: dict[str, str]) -> pd.DataFrame:
    records = []
    for source_key, text in texts.items():
        source_name = _source_label(source_key)
        if not text.strip():
            records.extend(_missing_source_rows(source_name))
            continue
        for term in FORBIDDEN_TERMS:
            count = count_unsafe_occurrences(text, term)
            safety_class = "SCOPE_VIOLATION" if count else "SCOPE_SAFE"
            records.append(
                {
                    "Reviewed_Source": source_name,
                    "Forbidden_Term": term,
                    "Occurrence_Count": count,
                    "Scope_Safety_Class": safety_class,
                    "Scope_Safety_Diagnostic": _diagnostic(source_name, term, count),
                }
            )
    return pd.DataFrame(records, columns=SCOPE_SAFETY_COLUMNS)


def count_unsafe_occurrences(text: str, term: str) -> int:
    count = 0
    for sentence in _sentences(text):
        lower = sentence.lower()
        if term.lower() not in lower:
            continue
        if any(cue in lower for cue in NEGATIVE_CUES):
            continue
        count += len(re.findall(rf"\b{re.escape(term.lower())}\b", lower))
    return count


def _sentences(text: str) -> list[str]:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    return [part.strip() for part in re.split(r"[.\n;]+", cleaned) if part.strip()]


def _missing_source_rows(source_name: str) -> list[dict[str, object]]:
    return [
        {
            "Reviewed_Source": source_name,
            "Forbidden_Term": term,
            "Occurrence_Count": 0,
            "Scope_Safety_Class": "INPUT_MISSING",
            "Scope_Safety_Diagnostic": f"{source_name} was missing and could not be scanned.",
        }
        for term in FORBIDDEN_TERMS
    ]


def _diagnostic(source_name: str, term: str, count: int) -> str:
    if count:
        return f"{source_name} contains {count} unsafe occurrence(s) of '{term}'."
    return f"{source_name} has no unsafe occurrence of '{term}'."


def _source_label(source_key: str) -> str:
    labels = {
        "prototype_report": "Prototype Report",
        "prototype_html": "Prototype HTML",
        "manual_review_report": "Manual Review Report",
        "manual_refined_html": "Manual Refined HTML",
    }
    return labels.get(source_key, source_key.replace("_", " ").title())
