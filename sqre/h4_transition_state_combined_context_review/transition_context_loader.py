"""Load H4 transition context inputs."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.loader import (
    DISPERSION_ALIASES,
    FORWARD_WINDOW_ALIASES,
    READINESS_ALIASES,
    SAMPLE_SIZE_ALIASES,
    SOURCE_STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TRANSITION_LABEL_ALIASES,
    int_value,
    read_first_summary_row,
    read_optional_csv,
    text_value,
)
from sqre.h4_transition_state_combined_context_review.models import TransitionContext


SENSITIVITY_ALIASES = ["Transition_Sensitivity_Class", "Sensitivity_Class", "H4_Transition_Scenario_Sensitive_Profile"]


def load_transition_contexts(config: H4TransitionStateCombinedContextReviewConfig) -> list[TransitionContext]:
    rows: list[TransitionContext] = []
    for path in [
        config.h4_transition_sensitive_dir / "h4_transition_scenario_sensitive_profile_review.csv",
        config.h4_transition_deep_dive_dir / "h4_transition_deep_dive_profile_inventory.csv",
        config.h4_transition_deep_dive_dir / "h4_transition_outcome_statistics.csv",
    ]:
        frame = read_optional_csv(path)
        for _, row in frame.iterrows():
            label = text_value(row, TRANSITION_LABEL_ALIASES, "")
            if not label:
                continue
            source = text_value(row, SOURCE_STATE_ALIASES, _source_from_label(label))
            target = text_value(row, TARGET_STATE_ALIASES, _target_from_label(label))
            rows.append(
                TransitionContext(
                    source_state=source,
                    target_state=target,
                    transition_label=label,
                    forward_window=text_value(row, FORWARD_WINDOW_ALIASES, ""),
                    profile_status=text_value(row, ["Profile_Type", "Transition_Profile_Status"], "TRANSITION_PROFILE_AVAILABLE"),
                    dispersion_status=text_value(row, DISPERSION_ALIASES, "TRANSITION_DISPERSION_AVAILABLE"),
                    sensitivity_status=text_value(row, SENSITIVITY_ALIASES, "TRANSITION_SENSITIVITY_UNAVAILABLE"),
                    readiness_flag=text_value(row, READINESS_ALIASES, "TRANSITION_READINESS_AVAILABLE"),
                    sample_size=int_value(row, SAMPLE_SIZE_ALIASES, 0),
                    near_aggregation_candidate_flag=text_value(row, ["Near_Aggregation_Candidate_Flag"], "false"),
                )
            )
    if rows:
        return rows
    return []


def load_transition_summary_context(config: H4TransitionStateCombinedContextReviewConfig) -> TransitionContext:
    dispersion = read_first_summary_row(config.h4_transition_dispersion_dir)
    sensitive = read_first_summary_row(config.h4_transition_sensitive_dir)
    return TransitionContext(
        source_state="SOURCE_STATE_UNAVAILABLE",
        target_state="TARGET_STATE_UNAVAILABLE",
        transition_label="TRANSITION_CONTEXT",
        forward_window="",
        dispersion_status=text_value(dispersion, DISPERSION_ALIASES, "TRANSITION_DISPERSION_UNAVAILABLE") if dispersion is not None else "TRANSITION_DISPERSION_UNAVAILABLE",
        sensitivity_status=text_value(sensitive, SENSITIVITY_ALIASES, "TRANSITION_SENSITIVITY_UNAVAILABLE") if sensitive is not None else "TRANSITION_SENSITIVITY_UNAVAILABLE",
        readiness_flag=text_value(dispersion, READINESS_ALIASES, "TRANSITION_READINESS_UNAVAILABLE") if dispersion is not None else "TRANSITION_READINESS_UNAVAILABLE",
    )


def _source_from_label(label: str) -> str:
    parts = label.split("->")
    return parts[0].strip() if len(parts) == 2 else "SOURCE_STATE_UNAVAILABLE"


def _target_from_label(label: str) -> str:
    parts = label.split("->")
    return parts[1].strip() if len(parts) == 2 else "TARGET_STATE_UNAVAILABLE"
