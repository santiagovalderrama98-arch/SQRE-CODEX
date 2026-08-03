"""Load Phase 7.5.13 H4 combined context rows."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.loader import (
    CONTEXT_ID_ALIASES,
    END_DATE_ALIASES,
    FORWARD_WINDOW_ALIASES,
    H4_DISPERSION_ALIASES,
    H4_INTERPRETATION_ALIASES,
    H4_READINESS_ALIASES,
    H4_SENSITIVITY_ALIASES,
    SCENARIO_ID_ALIASES,
    SOURCE_STATE_ALIASES,
    START_DATE_ALIASES,
    TARGET_STATE_ALIASES,
    TRANSITION_LABEL_ALIASES,
    read_optional_csv,
    text_value,
)
from sqre.h4_d1_contextual_transition_review.models import H4ContextRow


def load_h4_contexts(config: H4D1ContextualTransitionReviewConfig) -> list[H4ContextRow]:
    frames = [
        read_optional_csv(config.h4_combined_context_dir / "h4_transition_state_context_interpretation_matrix.csv"),
        read_optional_csv(config.h4_combined_context_dir / "h4_transition_state_context_inventory.csv"),
    ]
    rows: list[H4ContextRow] = []
    for frame in frames:
        for index, row in frame.iterrows():
            context_id = text_value(row, CONTEXT_ID_ALIASES, f"CTX_{index + 1:06d}")
            if any(existing.context_id == context_id for existing in rows):
                continue
            transition = text_value(row, TRANSITION_LABEL_ALIASES, "")
            source = text_value(row, SOURCE_STATE_ALIASES, _source_from_label(transition))
            target = text_value(row, TARGET_STATE_ALIASES, _target_from_label(transition))
            rows.append(
                H4ContextRow(
                    context_id=context_id,
                    symbol=config.symbol,
                    h4_source_state=source,
                    h4_target_state=target,
                    h4_transition_label=transition,
                    h4_forward_window=text_value(row, FORWARD_WINDOW_ALIASES, ""),
                    h4_context_interpretation_class=text_value(
                        row,
                        H4_INTERPRETATION_ALIASES,
                        "CONTEXT_INPUT_LIMITED",
                    ),
                    h4_context_readiness_flag=text_value(
                        row,
                        H4_READINESS_ALIASES,
                        "REQUIRES_INPUT_COMPLETENESS_REVIEW",
                    ),
                    h4_combined_dispersion_class=text_value(row, H4_DISPERSION_ALIASES, "COMBINED_BASELINE_UNAVAILABLE"),
                    h4_combined_sensitivity_class=text_value(row, H4_SENSITIVITY_ALIASES, "COMBINED_BASELINE_UNAVAILABLE"),
                    h4_scenario_id=text_value(row, SCENARIO_ID_ALIASES, ""),
                    start_date=text_value(row, START_DATE_ALIASES, ""),
                    end_date=text_value(row, END_DATE_ALIASES, ""),
                )
            )
    if rows:
        return rows
    return [
        H4ContextRow(
            context_id="CTX_000001",
            symbol=config.symbol,
            h4_source_state="H4_SOURCE_STATE_UNAVAILABLE",
            h4_target_state="H4_TARGET_STATE_UNAVAILABLE",
            h4_transition_label="H4_CONTEXT_UNAVAILABLE",
            h4_forward_window="",
            h4_context_interpretation_class="CONTEXT_INPUT_LIMITED",
            h4_context_readiness_flag="REQUIRES_INPUT_COMPLETENESS_REVIEW",
            h4_combined_dispersion_class="COMBINED_BASELINE_UNAVAILABLE",
            h4_combined_sensitivity_class="COMBINED_BASELINE_UNAVAILABLE",
        )
    ]


def _source_from_label(label: str) -> str:
    parts = str(label).split("->")
    return parts[0].strip() if len(parts) == 2 else "H4_SOURCE_STATE_UNAVAILABLE"


def _target_from_label(label: str) -> str:
    parts = str(label).split("->")
    return parts[1].strip() if len(parts) == 2 else "H4_TARGET_STATE_UNAVAILABLE"
