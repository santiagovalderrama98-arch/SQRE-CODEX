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
    first_row,
    int_value,
    read_first_summary_row,
    read_optional_csv,
    text_value,
)
from sqre.h4_transition_state_combined_context_review.models import StateContext


STATE_LABEL_ALIASES = ["Condition_Label", "Condition_Value", "State", "Market_State", "Source_State", "Target_State"]
PROFILE_ALIASES = ["Profile_Type", "State_Profile_Status", "Research_Class", "Transition_Research_Class"]
SENSITIVITY_ALIASES = ["Sensitivity_Class", "H4_Scenario_Sensitive_Profile", "Scenario_Sensitive_Profile"]


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
    summary = read_first_summary_row(config.h4_state_dispersion_dir)
    sensitive = read_first_summary_row(config.h4_state_sensitive_dir)
    summary_dispersion = text_value(summary, DISPERSION_ALIASES, "STATE_DISPERSION_UNAVAILABLE") if summary is not None else "STATE_DISPERSION_UNAVAILABLE"
    summary_ready = text_value(summary, READINESS_ALIASES, "STATE_READINESS_UNAVAILABLE") if summary is not None else "STATE_READINESS_UNAVAILABLE"
    summary_sensitivity = text_value(sensitive, SENSITIVITY_ALIASES, "STATE_SENSITIVITY_UNAVAILABLE") if sensitive is not None else "STATE_SENSITIVITY_UNAVAILABLE"
    return {
        key: StateContext(
            state_label=value.state_label,
            forward_window=value.forward_window,
            profile_status=value.profile_status,
            dispersion_status=value.dispersion_status if value.dispersion_status != "STATE_DISPERSION_AVAILABLE" else summary_dispersion,
            sensitivity_status=value.sensitivity_status if value.sensitivity_status != "STATE_SENSITIVITY_UNAVAILABLE" else summary_sensitivity,
            readiness_flag=summary_ready if summary_ready != "STATE_READINESS_UNAVAILABLE" else value.readiness_flag,
            sample_size=value.sample_size,
        )
        for key, value in contexts.items()
    }


def load_state_summary_context(config: H4TransitionStateCombinedContextReviewConfig) -> StateContext:
    summary = read_first_summary_row(config.h4_state_dispersion_dir)
    sensitive = read_first_summary_row(config.h4_state_sensitive_dir)
    return StateContext(
        state_label="STATE_CONTEXT",
        forward_window="",
        profile_status="STATE_PROFILE_AVAILABLE" if first_row(read_optional_csv(config.h4_state_deep_dive_dir / "h4_state_deep_dive_summary.csv")) is not None else "STATE_PROFILE_UNAVAILABLE",
        dispersion_status=text_value(summary, DISPERSION_ALIASES, "STATE_DISPERSION_UNAVAILABLE") if summary is not None else "STATE_DISPERSION_UNAVAILABLE",
        sensitivity_status=text_value(sensitive, SENSITIVITY_ALIASES, "STATE_SENSITIVITY_UNAVAILABLE") if sensitive is not None else "STATE_SENSITIVITY_UNAVAILABLE",
        readiness_flag=text_value(summary, READINESS_ALIASES, "STATE_READINESS_UNAVAILABLE") if summary is not None else "STATE_READINESS_UNAVAILABLE",
    )
