"""Load H4 state context inputs."""

from __future__ import annotations

from sqre.h4_transition_state_combined_context_review.config import (
    H4TransitionStateCombinedContextReviewConfig,
)
from sqre.h4_transition_state_combined_context_review.loader import (
    DISPERSION_ALIASES,
    FORWARD_WINDOW_ALIASES,
    READINESS_ALIASES,
    SAMPLE_SIZE_ALIASES,
    STATE_DISPERSION_FILENAMES,
    STATE_SENSITIVE_FILENAMES,
    first_row,
    int_value,
    read_first_existing_row,
    read_first_summary_row,
    read_optional_csv,
    text_value,
)
from sqre.h4_transition_state_combined_context_review.models import StateContext


STATE_LABEL_ALIASES = [
    "Condition_Label",
    "condition_label",
    "Condition_Value",
    "condition_value",
    "Condition",
    "condition",
    "State",
    "state",
    "Market_State",
    "market_state",
    "Source_State",
    "source_state",
    "Target_State",
    "target_state",
    "Condition_ID",
    "condition_id",
]
PROFILE_ALIASES = ["Profile_Type", "State_Profile_Status", "Research_Class", "Transition_Research_Class"]
SENSITIVITY_ALIASES = [
    "Sensitivity_Class",
    "Scenario_Sensitivity_Class",
    "H4_Scenario_Sensitive_Profile",
    "Scenario_Sensitive_Profile",
]


def load_state_contexts(config: H4TransitionStateCombinedContextReviewConfig) -> dict[tuple[str, str], StateContext]:
    contexts: dict[tuple[str, str], StateContext] = {}
    for filename in [
        "h4_state_deep_dive_profile_inventory.csv",
        "h4_state_outcome_statistics.csv",
        "h4_state_scenario_comparison_matrix.csv",
    ]:
        frame = read_optional_csv(config.h4_state_deep_dive_dir / filename)
        for _, row in frame.iterrows():
            state = text_value(row, STATE_LABEL_ALIASES, "")
            if not state:
                continue
            window = text_value(row, FORWARD_WINDOW_ALIASES, "")
            key = (state, window)
            contexts[key] = StateContext(
                state_label=state,
                forward_window=window,
                profile_status=text_value(row, PROFILE_ALIASES, "STATE_PROFILE_AVAILABLE"),
                dispersion_status=text_value(row, DISPERSION_ALIASES, "STATE_DISPERSION_AVAILABLE"),
                sensitivity_status=text_value(row, SENSITIVITY_ALIASES, "STATE_SENSITIVITY_UNAVAILABLE"),
                readiness_flag="STATE_READINESS_AVAILABLE",
                sample_size=int_value(row, SAMPLE_SIZE_ALIASES, 0),
            )
    dispersion_contexts = _load_state_dispersion_contexts(config)
    summary = read_first_summary_row(config.h4_state_dispersion_dir)
    sensitive = read_first_existing_row(config.h4_state_sensitive_dir, STATE_SENSITIVE_FILENAMES)
    summary_dispersion = text_value(summary, DISPERSION_ALIASES, "STATE_DISPERSION_UNAVAILABLE") if summary is not None else "STATE_DISPERSION_UNAVAILABLE"
    summary_ready = text_value(summary, READINESS_ALIASES, "STATE_READINESS_UNAVAILABLE") if summary is not None else "STATE_READINESS_UNAVAILABLE"
    summary_sensitivity = text_value(sensitive, SENSITIVITY_ALIASES, "STATE_SENSITIVITY_UNAVAILABLE") if sensitive is not None else "STATE_SENSITIVITY_UNAVAILABLE"
    return {
        key: StateContext(
            state_label=value.state_label,
            forward_window=value.forward_window,
            profile_status=value.profile_status,
            dispersion_status=_matched_state_dispersion(
                value,
                dispersion_contexts,
                summary_dispersion,
            ),
            sensitivity_status=value.sensitivity_status if value.sensitivity_status != "STATE_SENSITIVITY_UNAVAILABLE" else summary_sensitivity,
            readiness_flag=summary_ready if summary_ready != "STATE_READINESS_UNAVAILABLE" else value.readiness_flag,
            sample_size=value.sample_size,
        )
        for key, value in contexts.items()
    }


def load_state_summary_context(config: H4TransitionStateCombinedContextReviewConfig) -> StateContext:
    summary = read_first_summary_row(config.h4_state_dispersion_dir)
    sensitive = read_first_existing_row(config.h4_state_sensitive_dir, STATE_SENSITIVE_FILENAMES)
    return StateContext(
        state_label="STATE_CONTEXT",
        forward_window="",
        profile_status="STATE_PROFILE_AVAILABLE" if first_row(read_optional_csv(config.h4_state_deep_dive_dir / "h4_state_deep_dive_summary.csv")) is not None else "STATE_PROFILE_UNAVAILABLE",
        dispersion_status=text_value(summary, DISPERSION_ALIASES, "STATE_DISPERSION_UNAVAILABLE") if summary is not None else "STATE_DISPERSION_UNAVAILABLE",
        sensitivity_status=text_value(sensitive, SENSITIVITY_ALIASES, "STATE_SENSITIVITY_UNAVAILABLE") if sensitive is not None else "STATE_SENSITIVITY_UNAVAILABLE",
        readiness_flag=text_value(summary, READINESS_ALIASES, "STATE_READINESS_UNAVAILABLE") if summary is not None else "STATE_READINESS_UNAVAILABLE",
    )


def _load_state_dispersion_contexts(config: H4TransitionStateCombinedContextReviewConfig) -> dict[tuple[str, str], StateContext]:
    contexts: dict[tuple[str, str], StateContext] = {}
    for filename in STATE_DISPERSION_FILENAMES:
        frame = read_optional_csv(config.h4_state_dispersion_dir / filename)
        for _, row in frame.iterrows():
            state = text_value(row, STATE_LABEL_ALIASES, "")
            if not state:
                continue
            window = text_value(row, FORWARD_WINDOW_ALIASES, "")
            context = StateContext(
                state_label=state,
                forward_window=window,
                profile_status=text_value(row, PROFILE_ALIASES, "STATE_PROFILE_AVAILABLE"),
                dispersion_status=_dispersion_status(row, "STATE_DISPERSION_UNAVAILABLE"),
                sensitivity_status=text_value(row, SENSITIVITY_ALIASES, "STATE_SENSITIVITY_UNAVAILABLE"),
                readiness_flag=text_value(row, READINESS_ALIASES, "STATE_READINESS_AVAILABLE"),
                sample_size=int_value(row, SAMPLE_SIZE_ALIASES, 0),
            )
            for key in _state_keys(state, window):
                contexts[key] = _dominant_state_context(contexts.get(key), context)
    return contexts


def _matched_state_dispersion(
    context: StateContext,
    dispersion_contexts: dict[tuple[str, str], StateContext],
    summary_dispersion: str,
) -> str:
    for key in _state_keys(context.state_label, context.forward_window):
        matched = dispersion_contexts.get(key)
        if matched is not None and not _is_unavailable(matched.dispersion_status):
            return matched.dispersion_status
    if context.dispersion_status != "STATE_DISPERSION_AVAILABLE":
        return context.dispersion_status
    return summary_dispersion


def _state_keys(state: str, window: str) -> list[tuple[str, str]]:
    return [(state, window), (state, "")]


def _dispersion_status(row, default: str) -> str:
    dispersion = text_value(row, DISPERSION_ALIASES, "")
    readiness = text_value(row, READINESS_ALIASES, "")
    if _is_high(dispersion):
        return dispersion
    if _is_moderate(dispersion):
        return dispersion
    if _is_sample_constrained(readiness):
        return readiness
    if dispersion:
        return dispersion
    return default


def _dominant_state_context(current: StateContext | None, candidate: StateContext) -> StateContext:
    if current is None:
        return candidate
    return candidate if _rank(candidate.dispersion_status) > _rank(current.dispersion_status) else current


def _rank(value: str) -> int:
    if _is_high(value):
        return 5
    if _is_moderate(value):
        return 4
    if _is_stable(value):
        return 3
    if _is_sample_constrained(value):
        return 2
    if _is_unavailable(value):
        return 0
    return 1


def _is_high(value: str) -> bool:
    return "HIGH" in str(value).upper() or "SCENARIO_SENSITIVE" in str(value).upper()


def _is_moderate(value: str) -> bool:
    return "MODERATE" in str(value).upper()


def _is_sample_constrained(value: str) -> bool:
    text = str(value).upper()
    return "SAMPLE" in text or "CONSTRAINED" in text


def _is_stable(value: str) -> bool:
    text = str(value).upper()
    return "STABLE" in text or "DESCRIPTIVE" in text or "CONSISTENT" in text


def _is_unavailable(value: str) -> bool:
    text = str(value or "").upper()
    return not text or "UNAVAILABLE" in text or "MISSING" in text
