"""Map H4 combined context rows to available D1 context rows."""

from __future__ import annotations

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.models import D1ContextRow, H4ContextRow, ScenarioContextMapRow


def build_scenario_context_map(
    h4_rows: list[H4ContextRow],
    d1_rows: list[D1ContextRow],
    config: H4D1ContextualTransitionReviewConfig,
) -> list[ScenarioContextMapRow]:
    return [_map_row(index, row, d1_rows, config) for index, row in enumerate(h4_rows, start=1)]


def _map_row(
    index: int,
    h4: H4ContextRow,
    d1_rows: list[D1ContextRow],
    config: H4D1ContextualTransitionReviewConfig,
) -> ScenarioContextMapRow:
    explicit = _match_explicit(h4, d1_rows)
    if explicit is not None:
        return _mapped(index, h4, explicit, config, "EXPLICIT_SCENARIO_ID", "HIGH_CONFIDENCE_MAPPING")
    period = _match_period(h4, d1_rows)
    if period is not None:
        return _mapped(index, h4, period, config, "EXPLICIT_PERIOD_ID", "MODERATE_CONFIDENCE_MAPPING")
    overlap = _match_date_overlap(h4, d1_rows)
    if overlap is not None:
        return _mapped(index, h4, overlap, config, "DATE_RANGE_OVERLAP", "LOW_CONFIDENCE_MAPPING")
    condition = _match_condition_profile(h4, d1_rows)
    if condition is not None:
        return ScenarioContextMapRow(
            scenario_context_id=f"SCM_{index:06d}",
            symbol=config.symbol,
            h4_scenario_id="",
            d1_scenario_id="",
            d1_regime_label=condition.d1_regime_label,
            d1_context_label=condition.d1_context_label,
            mapping_method="CONDITION_PROFILE_MATCH",
            mapping_confidence_class="MODERATE_CONFIDENCE_MAPPING",
            mapping_diagnostic="Mapped by condition label and forward window; no scenario/date alignment inferred.",
        )
    return ScenarioContextMapRow(
        scenario_context_id=f"SCM_{index:06d}",
        symbol=config.symbol,
        h4_scenario_id=h4.h4_scenario_id,
        d1_scenario_id="",
        d1_regime_label="D1_CONTEXT_UNMAPPED",
        d1_context_label="D1_CONTEXT_UNMAPPED",
        mapping_method="UNMAPPED",
        mapping_confidence_class="NO_CONFIDENCE_MAPPING",
        mapping_diagnostic="No explicit scenario, period, or date-range mapping was available.",
    )


def _mapped(
    index: int,
    h4: H4ContextRow,
    d1: D1ContextRow,
    config: H4D1ContextualTransitionReviewConfig,
    method: str,
    confidence: str,
) -> ScenarioContextMapRow:
    return ScenarioContextMapRow(
        scenario_context_id=f"SCM_{index:06d}",
        symbol=config.symbol,
        h4_scenario_id=h4.h4_scenario_id,
        d1_scenario_id=d1.d1_scenario_id,
        d1_regime_label=d1.d1_regime_label,
        d1_context_label=d1.d1_context_label,
        mapping_method=method,
        mapping_confidence_class=confidence,
        mapping_diagnostic=f"D1 context mapped by {method}.",
    )


def _match_explicit(h4: H4ContextRow, d1_rows: list[D1ContextRow]) -> D1ContextRow | None:
    if not h4.h4_scenario_id:
        return None
    for row in d1_rows:
        if row.d1_scenario_id and row.d1_scenario_id == h4.h4_scenario_id:
            return row
    return None


def _match_period(h4: H4ContextRow, d1_rows: list[D1ContextRow]) -> D1ContextRow | None:
    if not h4.h4_scenario_id:
        return None
    h4_period = _period_token(h4.h4_scenario_id)
    if not h4_period:
        return None
    for row in d1_rows:
        if _period_token(row.d1_scenario_id) == h4_period:
            return row
    return None


def _match_date_overlap(h4: H4ContextRow, d1_rows: list[D1ContextRow]) -> D1ContextRow | None:
    if not h4.start_date or not h4.end_date:
        return None
    for row in d1_rows:
        if row.start_date == h4.start_date and row.end_date == h4.end_date:
            return row
    return None


def _match_condition_profile(h4: H4ContextRow, d1_rows: list[D1ContextRow]) -> D1ContextRow | None:
    transition_matches = _condition_matches(
        d1_rows,
        h4.h4_transition_label,
        h4.h4_forward_window,
        "TRANSITION",
    )
    if transition_matches:
        return _aggregate_condition_matches(transition_matches, h4.h4_transition_label, h4.h4_forward_window)

    state_matches = [
        *_condition_matches(d1_rows, h4.h4_source_state, h4.h4_forward_window, "STATE"),
        *_condition_matches(d1_rows, h4.h4_target_state, h4.h4_forward_window, "STATE"),
    ]
    if state_matches:
        label = h4.h4_source_state if _condition_matches(d1_rows, h4.h4_source_state, h4.h4_forward_window, "STATE") else h4.h4_target_state
        return _aggregate_condition_matches(state_matches, label, h4.h4_forward_window)
    return None


def _condition_matches(
    d1_rows: list[D1ContextRow],
    label: str,
    forward_window: str,
    condition_family: str,
) -> list[D1ContextRow]:
    normalized_label = _normalize_label(label)
    normalized_window = _normalize_window(forward_window)
    if not normalized_label or not normalized_window:
        return []
    return [
        row
        for row in d1_rows
        if row.d1_context_status == "D1_CONTEXT_AVAILABLE_CONDITION_LEVEL"
        and _condition_family(row, condition_family)
        and _normalize_label(row.d1_context_label) == normalized_label
        and _normalize_window(row.d1_forward_window) == normalized_window
    ]


def _aggregate_condition_matches(matches: list[D1ContextRow], label: str, forward_window: str) -> D1ContextRow:
    return D1ContextRow(
        d1_context_id="D1_CONDITION_PROFILE_MATCH",
        d1_scenario_id="",
        d1_regime_label=_aggregate_regime_label(matches),
        d1_context_label=label,
        d1_state_profile="CONDITION_PROFILE_MATCH",
        d1_dispersion_class=_dominant_dispersion(matches),
        d1_sample_adequacy_class=_dominant_sample_adequacy(matches),
        d1_readiness_flag=_dominant_readiness(matches),
        d1_condition_type=matches[0].d1_condition_type,
        d1_forward_window=forward_window,
        d1_context_status="D1_CONTEXT_AVAILABLE_CONDITION_LEVEL",
        d1_sensitivity_class=_dominant_sensitivity(matches),
        source_type="CONDITION_PROFILE_MATCH",
    )


def _aggregate_regime_label(matches: list[D1ContextRow]) -> str:
    regimes = sorted(
        {
            regime
            for row in matches
            for regime in _split_regime_label(row.d1_regime_label)
            if regime and regime not in {"D1_REGIME_UNAVAILABLE", "D1_CONTEXT_UNMAPPED"}
        }
    )
    if len(regimes) > 1:
        return f"MULTI_REGIME:{'|'.join(regimes)}"
    if len(regimes) == 1:
        return regimes[0]
    return "D1_REGIME_UNAVAILABLE"


def _split_regime_label(label: str) -> list[str]:
    text = str(label or "").strip()
    if text.startswith("MULTI_REGIME:"):
        text = text.split(":", 1)[1]
    if text == "MULTI_REGIME_CONTEXT":
        return [text]
    return [part.strip() for part in text.split("|") if part.strip()]


def _dominant_dispersion(matches: list[D1ContextRow]) -> str:
    values = [row.d1_dispersion_class for row in matches]
    if any("HIGH" in value.upper() for value in values):
        return "HIGH_DISPERSION"
    if any("MODERATE" in value.upper() for value in values):
        return "MODERATE_DISPERSION"
    return next((value for value in values if value), "D1_DISPERSION_UNAVAILABLE")


def _dominant_sensitivity(matches: list[D1ContextRow]) -> str:
    values = [row.d1_sensitivity_class or row.d1_dispersion_class for row in matches]
    if any("REGIME_SENSITIVE" in value.upper() or "HIGH_SENSITIVITY" in value.upper() for value in values):
        return "REGIME_SENSITIVE"
    return next((value for value in values if value), "")


def _dominant_sample_adequacy(matches: list[D1ContextRow]) -> str:
    values = [row.d1_sample_adequacy_class for row in matches]
    if any(_sample_constrained(value) for value in values) and not any(
        _high_signal(row.d1_dispersion_class) or _high_signal(row.d1_sensitivity_class) for row in matches
    ):
        return "SAMPLE_CONSTRAINED"
    return next((value for value in values if value), "D1_SAMPLE_ADEQUACY_UNAVAILABLE")


def _dominant_readiness(matches: list[D1ContextRow]) -> str:
    values = [row.d1_readiness_flag for row in matches]
    return next((value for value in values if value), "D1_READINESS_UNAVAILABLE")


def _condition_family(row: D1ContextRow, expected: str) -> bool:
    text = f"{row.d1_condition_type} {row.source_type} {row.d1_context_label}".upper()
    if expected == "TRANSITION":
        return "TRANSITION" in text or "->" in row.d1_context_label
    return "STATE" in text and "TRANSITION" not in text


def _normalize_label(value: str) -> str:
    return " ".join(str(value or "").strip().upper().split())


def _normalize_window(value: str) -> str:
    text = str(value or "").strip()
    try:
        return str(int(float(text)))
    except ValueError:
        return text.upper()


def _sample_constrained(value: str) -> bool:
    text = str(value or "").upper()
    if "ADEQUATE" in text or "SUFFICIENT" in text:
        return False
    return "LOW_SAMPLE" in text or "LOW SAMPLE" in text or "CONSTRAINED" in text or "INSUFFICIENT" in text


def _high_signal(value: str) -> bool:
    text = str(value or "").upper()
    return "HIGH" in text or "REGIME_SENSITIVE" in text


def _period_token(value: str) -> str:
    text = str(value)
    marker = "period_"
    if marker not in text:
        return ""
    suffix = text.split(marker, 1)[1]
    return suffix.split("_", 1)[0]
