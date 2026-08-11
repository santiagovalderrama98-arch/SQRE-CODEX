"""Scope safety review for reference stability documentation."""

from __future__ import annotations

import re

import pandas as pd


SCOPE_SAFETY_COLUMNS = [
    "Reviewed_Source",
    "Forbidden_Term",
    "Occurrence_Count",
    "Documentation_Scope_Safety_Class",
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

NEGATIVE_MARKERS = [
    "does not",
    "do not",
    "not ",
    "no ",
    "must not",
    "without",
]


def build_scope_safety_review(include: bool, sources: dict[str, str]) -> pd.DataFrame:
    if not include:
        return pd.DataFrame(columns=SCOPE_SAFETY_COLUMNS)
    rows = []
    for source_name, text in sources.items():
        for term in FORBIDDEN_TERMS:
            count = _unsafe_count(text, term)
            klass = _class_for_count(count)
            rows.append(
                {
                    "Reviewed_Source": source_name,
                    "Forbidden_Term": term,
                    "Occurrence_Count": count,
                    "Documentation_Scope_Safety_Class": klass,
                    "Scope_Safety_Diagnostic": _diagnostic(source_name, term, count),
                }
            )
    return pd.DataFrame(rows, columns=SCOPE_SAFETY_COLUMNS)


def scope_safety_class(review: pd.DataFrame) -> str:
    if review.empty:
        return "INPUT_MISSING"
    violations = int((review["Documentation_Scope_Safety_Class"] == "DOCUMENTATION_SCOPE_VIOLATION").sum())
    warnings = int((review["Documentation_Scope_Safety_Class"] == "DOCUMENTATION_SCOPE_WARNING").sum())
    if violations:
        return "DOCUMENTATION_SCOPE_VIOLATION"
    if warnings:
        return "DOCUMENTATION_SCOPE_WARNING"
    return "DOCUMENTATION_SCOPE_SAFE"


def _unsafe_count(text: str, term: str) -> int:
    if not text:
        return 0
    count = 0
    pattern = re.compile(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)
    for line in str(text).splitlines():
        matches = list(pattern.finditer(line))
        if not matches:
            continue
        if _is_negative_scope_line(line):
            continue
        count += len(matches)
    return count


def _is_negative_scope_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in NEGATIVE_MARKERS)


def _class_for_count(count: int) -> str:
    return "DOCUMENTATION_SCOPE_VIOLATION" if count > 0 else "DOCUMENTATION_SCOPE_SAFE"


def _diagnostic(source_name: str, term: str, count: int) -> str:
    if count:
        return f"{source_name} contains {count} unsafe occurrence(s) of {term}."
    return f"{source_name} has no unsafe occurrence of {term}."
