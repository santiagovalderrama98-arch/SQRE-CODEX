"""Load available D1 contextual research rows."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.loader import (
    D1_DISPERSION_ALIASES,
    D1_STATE_PROFILE_ALIASES,
    END_DATE_ALIASES,
    READINESS_ALIASES,
    REGIME_LABEL_ALIASES,
    SAMPLE_ADEQUACY_ALIASES,
    SCENARIO_ID_ALIASES,
    START_DATE_ALIASES,
    STATE_LABEL_ALIASES,
    read_optional_csv,
    text_value,
)
from sqre.h4_d1_contextual_transition_review.models import D1ContextRow


D1_INPUTS = [
    ("d1_regime_normalized_summary.csv", "REGIME_NORMALIZED"),
    ("d1_regime_outcome_review_summary.csv", "REGIME_OUTCOME"),
    ("d1_state_deep_dive_profile_inventory.csv", "STATE_DEEP_DIVE"),
    ("h4_d1_structural_research_summary.csv", "H4_D1_STRUCTURAL"),
    ("multi_scenario_validation_summary.csv", "VALIDATION"),
]


def load_d1_contexts(config: H4D1ContextualTransitionReviewConfig) -> list[D1ContextRow]:
    rows: list[D1ContextRow] = []
    for directory, filenames in _source_directories(config):
        for filename, source_type in filenames:
            rows.extend(_load_file(directory / filename, source_type))
    return _dedupe(rows)


def _source_directories(config: H4D1ContextualTransitionReviewConfig):
    return [
        (config.d1_regime_normalized_dir, [D1_INPUTS[0]]),
        (config.d1_regime_outcome_review_dir, [D1_INPUTS[1]]),
        (config.d1_state_deep_dive_dir, [D1_INPUTS[2]]),
        (config.h4_d1_structural_research_dir, [D1_INPUTS[3]]),
        (config.h4_d1_validation_dir, [D1_INPUTS[4]]),
    ]


def _load_file(path: Path, source_type: str) -> list[D1ContextRow]:
    frame = read_optional_csv(path)
    rows: list[D1ContextRow] = []
    for index, row in frame.iterrows():
        scenario_id = text_value(row, SCENARIO_ID_ALIASES, "")
        regime = text_value(row, REGIME_LABEL_ALIASES, "")
        state = text_value(row, STATE_LABEL_ALIASES, regime or source_type)
        context_id = scenario_id or regime or f"{source_type}_{index + 1:03d}"
        rows.append(
            D1ContextRow(
                d1_context_id=context_id,
                d1_scenario_id=scenario_id,
                d1_regime_label=regime or "D1_REGIME_UNAVAILABLE",
                d1_context_label=state or "D1_CONTEXT",
                d1_state_profile=text_value(row, D1_STATE_PROFILE_ALIASES, source_type),
                d1_dispersion_class=text_value(row, D1_DISPERSION_ALIASES, "D1_DISPERSION_UNAVAILABLE"),
                d1_sample_adequacy_class=text_value(row, SAMPLE_ADEQUACY_ALIASES, "D1_SAMPLE_ADEQUACY_UNAVAILABLE"),
                d1_readiness_flag=text_value(row, READINESS_ALIASES, "D1_READINESS_UNAVAILABLE"),
                start_date=text_value(row, START_DATE_ALIASES, ""),
                end_date=text_value(row, END_DATE_ALIASES, ""),
            )
        )
    return rows


def _dedupe(rows: list[D1ContextRow]) -> list[D1ContextRow]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[D1ContextRow] = []
    for row in rows:
        key = (row.d1_scenario_id, row.d1_regime_label, row.d1_context_label)
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique
