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
    TRANSITION_DISPERSION_FILENAMES,
    TRANSITION_LABEL_ALIASES,
    int_value,
    read_first_summary_row,
    read_optional_csv,
    text_value,
)
from sqre.h4_transition_state_combined_context_review.models import TransitionContext


SENSITIVITY_ALIASES = ["Transition_Sensitivity_Class", "Sensitivity_Class", "H4_Transition_Scenario_Sensitive_Profile"]


def load_transition_contexts(config: H4TransitionStateCombinedContextReviewConfig) -> list[TransitionContext]:
    dispersion_contexts = _load_transition_dispersion_contexts(config)
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
            window = text_value(row, FORWARD_WINDOW_ALIASES, "")
            row_dispersion = text_value(row, DISPERSION_ALIASES, "TRANSITION_DISPERSION_UNAVAILABLE")
            rows.append(
                TransitionContext(
                    source_state=source,
                    target_state=target,
                    transition_label=label,
                    forward_window=window,
                    profile_status=text_value(row, ["Profile_Type", "Transition_Profile_Status"], "TRANSITION_PROFILE_AVAILABLE"),
                    dispersion_status=_matched_transition_dispersion(
                        label,
                        source,
                        target,
                        window,
                        row_dispersion,
                        dispersion_contexts,
                    ),
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


def _load_transition_dispersion_contexts(
    config: H4TransitionStateCombinedContextReviewConfig,
) -> dict[tuple[str, str, str, str], TransitionContext]:
    contexts: dict[tuple[str, str, str, str], TransitionContext] = {}
    for filename in TRANSITION_DISPERSION_FILENAMES:
        frame = read_optional_csv(config.h4_transition_dispersion_dir / filename)
        for _, row in frame.iterrows():
            label = text_value(row, TRANSITION_LABEL_ALIASES, "")
            source = text_value(row, SOURCE_STATE_ALIASES, _source_from_label(label))
            target = text_value(row, TARGET_STATE_ALIASES, _target_from_label(label))
            if not label and source and target:
                label = f"{source} -> {target}"
            if not label:
                continue
            window = text_value(row, FORWARD_WINDOW_ALIASES, "")
            context = TransitionContext(
                source_state=source,
                target_state=target,
                transition_label=label,
                forward_window=window,
                profile_status=text_value(row, ["Profile_Type", "Transition_Profile_Status"], "TRANSITION_PROFILE_AVAILABLE"),
                dispersion_status=_dispersion_status(row, "TRANSITION_DISPERSION_UNAVAILABLE"),
                sensitivity_status=text_value(row, SENSITIVITY_ALIASES, "TRANSITION_SENSITIVITY_UNAVAILABLE"),
                readiness_flag=text_value(row, READINESS_ALIASES, "TRANSITION_READINESS_AVAILABLE"),
                sample_size=int_value(row, SAMPLE_SIZE_ALIASES, 0),
            )
            for key in _transition_keys(label, source, target, window):
                contexts[key] = _dominant_transition_context(contexts.get(key), context)
    return contexts


def _matched_transition_dispersion(
    label: str,
    source: str,
    target: str,
    window: str,
    row_dispersion: str,
    dispersion_contexts: dict[tuple[str, str, str, str], TransitionContext],
) -> str:
    for key in _transition_keys(label, source, target, window):
        matched = dispersion_contexts.get(key)
        if matched is not None and not _is_unavailable(matched.dispersion_status):
            return matched.dispersion_status
    return row_dispersion


def _transition_keys(label: str, source: str, target: str, window: str) -> list[tuple[str, str, str, str]]:
    normalized_label = _normalize_label(label)
    generated_label = _normalize_label(f"{source} -> {target}") if source and target else ""
    return [
        (normalized_label, source, target, window),
        (normalized_label, "", "", window),
        (normalized_label, source, target, ""),
        (generated_label, source, target, window),
        (generated_label, source, target, ""),
        ("", source, target, window),
        ("", source, target, ""),
    ]


def _normalize_label(label: str) -> str:
    return " -> ".join(part.strip() for part in str(label).split("->")) if "->" in str(label) else str(label).strip()


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


def _dominant_transition_context(current: TransitionContext | None, candidate: TransitionContext) -> TransitionContext:
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
