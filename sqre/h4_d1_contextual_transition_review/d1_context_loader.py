"""Load available D1 contextual research rows."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.loader import (
    CONDITION_LABEL_ALIASES,
    CONDITION_TYPE_ALIASES,
    D1_DISPERSION_ALIASES,
    D1_FORWARD_WINDOW_ALIASES,
    D1_SENSITIVITY_ALIASES,
    D1_STATE_PROFILE_ALIASES,
    END_DATE_ALIASES,
    READINESS_ALIASES,
    REGIME_COUNT_ALIASES,
    REGIME_LABEL_ALIASES,
    REGIMES_PRESENT_ALIASES,
    SAMPLE_ADEQUACY_ALIASES,
    SCENARIO_ID_ALIASES,
    START_DATE_ALIASES,
    STATE_LABEL_ALIASES,
    int_value,
    read_optional_csv,
    text_value,
)
from sqre.h4_d1_contextual_transition_review.models import D1ContextRow


D1_INPUTS: list[tuple[list[str], str]] = [
    (["d1_regime_research_summary.csv", "d1_regime_normalized_summary.csv"], "REGIME_NORMALIZED_SUMMARY"),
    (["d1_regime_outcome_review_summary.csv"], "REGIME_OUTCOME_SUMMARY"),
    (["d1_state_deep_dive_profile_inventory.csv"], "STATE_DEEP_DIVE_CONDITION"),
    (["h4_d1_timeframe_research_summary.csv", "h4_d1_structural_research_summary.csv"], "H4_D1_STRUCTURAL_SUMMARY"),
    (["h4_d1_validation_summary.csv", "multi_scenario_validation_summary.csv"], "VALIDATION_SUMMARY"),
]

D1_REGIME_NORMALIZED_CONDITION_INPUTS: list[tuple[list[str], str]] = [
    (["d1_regime_condition_outcomes.csv"], "REGIME_CONDITION_OUTCOME"),
    (["d1_regime_state_outcome_profiles.csv"], "STATE_CONDITION_PROFILE"),
    (["d1_regime_transition_outcome_profiles.csv"], "TRANSITION_CONDITION_PROFILE"),
]

D1_REGIME_OUTCOME_CONDITION_INPUTS: list[tuple[list[str], str]] = [
    (["d1_condition_quality_inventory.csv"], "CONDITION_QUALITY"),
    (["d1_regime_sensitive_condition_profiles.csv"], "REGIME_SENSITIVE_CONDITION"),
    (["d1_research_ready_condition_profiles.csv"], "RESEARCH_READY_CONDITION"),
    (["d1_low_sample_condition_profiles.csv"], "LOW_SAMPLE_CONDITION"),
    (["d1_limited_coverage_condition_profiles.csv"], "LIMITED_COVERAGE_CONDITION"),
    (["d1_state_condition_quality_summary.csv"], "STATE_CONDITION_PROFILE"),
    (["d1_transition_condition_quality_summary.csv"], "TRANSITION_CONDITION_PROFILE"),
]

D1_STATE_DEEP_DIVE_CONDITION_INPUTS: list[tuple[list[str], str]] = [
    (["d1_state_deep_dive_profile_inventory.csv"], "STATE_DEEP_DIVE_CONDITION"),
    (["d1_state_regime_breakdown.csv"], "STATE_REGIME_BREAKDOWN"),
    (["d1_state_regime_comparison_matrix.csv"], "STATE_REGIME_COMPARISON"),
]


def load_d1_contexts(config: H4D1ContextualTransitionReviewConfig) -> list[D1ContextRow]:
    rows: list[D1ContextRow] = []
    for directory, filenames in _source_directories(config):
        for filename_aliases, source_type in filenames:
            rows.extend(_load_first_existing_file(directory, filename_aliases, source_type))
    return _dedupe(rows)


def _source_directories(config: H4D1ContextualTransitionReviewConfig):
    return [
        (config.d1_regime_normalized_dir, [D1_INPUTS[0], *D1_REGIME_NORMALIZED_CONDITION_INPUTS]),
        (config.d1_regime_outcome_review_dir, [D1_INPUTS[1], *D1_REGIME_OUTCOME_CONDITION_INPUTS]),
        (config.d1_state_deep_dive_dir, [D1_INPUTS[2], *D1_STATE_DEEP_DIVE_CONDITION_INPUTS]),
        (config.h4_d1_structural_research_dir, [D1_INPUTS[3]]),
        (config.h4_d1_validation_dir, [D1_INPUTS[4]]),
    ]


def _load_first_existing_file(filedir: Path, filename_aliases: list[str], source_type: str) -> list[D1ContextRow]:
    for filename in filename_aliases:
        path = filedir / filename
        if path.exists():
            return _load_file(path, source_type)
    return []


def _load_file(path: Path, source_type: str) -> list[D1ContextRow]:
    frame = read_optional_csv(path)
    rows: list[D1ContextRow] = []
    for index, row in frame.iterrows():
        scenario_id = text_value(row, SCENARIO_ID_ALIASES, "")
        condition_type = _condition_type(row, source_type)
        forward_window = text_value(row, D1_FORWARD_WINDOW_ALIASES, "")
        regime = _regime_label(row)
        state = text_value(row, CONDITION_LABEL_ALIASES, "") or text_value(row, STATE_LABEL_ALIASES, regime or source_type)
        context_id = scenario_id or regime or f"{source_type}_{index + 1:03d}"
        status = _context_status(state, forward_window, source_type)
        rows.append(
            D1ContextRow(
                d1_context_id=_context_id(context_id, state, forward_window, source_type, index),
                d1_scenario_id=scenario_id,
                d1_regime_label=regime or "D1_REGIME_UNAVAILABLE",
                d1_context_label=state or "D1_CONTEXT",
                d1_state_profile=text_value(row, D1_STATE_PROFILE_ALIASES, source_type),
                d1_dispersion_class=text_value(row, D1_DISPERSION_ALIASES, "D1_DISPERSION_UNAVAILABLE"),
                d1_sample_adequacy_class=text_value(row, SAMPLE_ADEQUACY_ALIASES, "D1_SAMPLE_ADEQUACY_UNAVAILABLE"),
                d1_readiness_flag=text_value(row, READINESS_ALIASES, "D1_READINESS_UNAVAILABLE"),
                start_date=text_value(row, START_DATE_ALIASES, ""),
                end_date=text_value(row, END_DATE_ALIASES, ""),
                d1_condition_type=condition_type,
                d1_forward_window=forward_window,
                d1_context_status=status,
                d1_sensitivity_class=text_value(row, D1_SENSITIVITY_ALIASES, ""),
                source_type=source_type,
            )
        )
    return rows


def _dedupe(rows: list[D1ContextRow]) -> list[D1ContextRow]:
    seen: set[tuple[str, str, str, str, str]] = set()
    unique: list[D1ContextRow] = []
    for row in rows:
        key = (
            row.d1_scenario_id,
            row.d1_regime_label,
            row.d1_context_label,
            row.d1_condition_type,
            row.d1_forward_window,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def _context_id(base: str, label: str, window: str, source_type: str, index: int) -> str:
    if label and window:
        return f"{source_type}_{_slug(label)}_{_slug(window)}_{index + 1:03d}"
    return base


def _condition_type(row, source_type: str) -> str:
    explicit = text_value(row, CONDITION_TYPE_ALIASES, "")
    if explicit:
        return explicit
    if "TRANSITION" in source_type:
        return "TRANSITION"
    if "STATE" in source_type:
        return "STATE"
    return ""


def _context_status(label: str, forward_window: str, source_type: str) -> str:
    if label and forward_window and "SUMMARY" not in source_type:
        return "D1_CONTEXT_AVAILABLE_CONDITION_LEVEL"
    return "D1_CONTEXT_AVAILABLE_SUMMARY_LEVEL"


def _regime_label(row) -> str:
    regime = text_value(row, REGIME_LABEL_ALIASES, "")
    if regime:
        return regime
    regimes_present = text_value(row, REGIMES_PRESENT_ALIASES, "")
    if regimes_present:
        regimes = _split_regimes(regimes_present)
        if len(regimes) > 1:
            return f"MULTI_REGIME:{'|'.join(regimes)}"
        if regimes:
            return regimes[0]
    regime_count = int_value(row, REGIME_COUNT_ALIASES, 0)
    if regime_count > 1:
        return "MULTI_REGIME_CONTEXT"
    return ""


def _split_regimes(value: str) -> list[str]:
    text = str(value).strip()
    if not text:
        return []
    for char in "[]'\"":
        text = text.replace(char, "")
    parts = text.replace(";", "|").replace(",", "|").split("|")
    return sorted({part.strip() for part in parts if part.strip()})


def _slug(value: str) -> str:
    text = str(value).strip().upper().replace(" ", "_")
    for char in ">/\\:,;[](){}":
        text = text.replace(char, "_")
    return "_".join(part for part in text.split("_") if part)
