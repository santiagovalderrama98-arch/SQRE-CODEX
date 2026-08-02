"""D1 regime/context review."""

from __future__ import annotations

from collections import Counter

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.models import (
    D1ContextRow,
    D1RegimeContextReviewRow,
    H4ContextRow,
    H4D1ContextInventoryRow,
    ScenarioContextMapRow,
)


def build_h4_d1_context_inventory(
    h4_rows: list[H4ContextRow],
    d1_rows: list[D1ContextRow],
    mappings: list[ScenarioContextMapRow],
    partial_status: str,
    config: H4D1ContextualTransitionReviewConfig,
) -> list[H4D1ContextInventoryRow]:
    d1_by_id = {row.d1_scenario_id: row for row in d1_rows if row.d1_scenario_id}
    d1_by_regime = {row.d1_regime_label: row for row in d1_rows}
    rows: list[H4D1ContextInventoryRow] = []
    for h4, mapping in zip(h4_rows, mappings):
        d1 = (
            d1_by_id.get(mapping.d1_scenario_id)
            or d1_by_regime.get(mapping.d1_regime_label)
            or _condition_match(h4, d1_rows, mapping)
        )
        rows.append(
            H4D1ContextInventoryRow(
                context_id=h4.context_id,
                symbol=config.symbol,
                h4_timeframe=config.h4_timeframe,
                d1_timeframe=config.d1_timeframe,
                h4_source_state=h4.h4_source_state,
                h4_target_state=h4.h4_target_state,
                h4_transition_label=h4.h4_transition_label,
                h4_forward_window=h4.h4_forward_window,
                h4_context_interpretation_class=h4.h4_context_interpretation_class,
                h4_context_readiness_flag=h4.h4_context_readiness_flag,
                h4_combined_dispersion_class=h4.h4_combined_dispersion_class,
                h4_combined_sensitivity_class=h4.h4_combined_sensitivity_class,
                d1_regime_label=d1.d1_regime_label if d1 else mapping.d1_regime_label,
                d1_context_status=d1.d1_context_status if d1 else "D1_CONTEXT_UNAVAILABLE",
                d1_sample_adequacy_class=d1.d1_sample_adequacy_class if d1 else "D1_SAMPLE_ADEQUACY_UNAVAILABLE",
                d1_dispersion_class=d1.d1_dispersion_class if d1 else "D1_DISPERSION_UNAVAILABLE",
                d1_regime_sensitivity_class=d1.d1_sensitivity_class if d1 else "D1_REGIME_SENSITIVITY_UNAVAILABLE",
                partial_context_status=partial_status,
                mapping_confidence_class=mapping.mapping_confidence_class,
                context_inventory_diagnostic=_inventory_diagnostic(mapping, d1 is not None),
            )
        )
    return rows


def build_d1_regime_context_review(
    rows: list[H4D1ContextInventoryRow],
    d1_rows: list[D1ContextRow],
) -> list[D1RegimeContextReviewRow]:
    regime_counts = Counter(row.d1_regime_label for row in d1_rows if row.d1_regime_label != "D1_REGIME_UNAVAILABLE")
    return [_build_row(row, regime_counts) for row in rows]


def _build_row(row: H4D1ContextInventoryRow, regime_counts: Counter[str]) -> D1RegimeContextReviewRow:
    sensitivity = _regime_sensitivity(row.d1_regime_sensitivity_class or row.d1_dispersion_class)
    interpretation = _interpret(row, sensitivity)
    return D1RegimeContextReviewRow(
        context_id=row.context_id,
        d1_regime_label=row.d1_regime_label,
        d1_context_status=row.d1_context_status,
        d1_regime_count=regime_counts[row.d1_regime_label],
        d1_sample_adequacy_class=row.d1_sample_adequacy_class,
        d1_dispersion_class=row.d1_dispersion_class,
        d1_regime_sensitivity_class=sensitivity,
        d1_context_interpretation_class=interpretation,
        d1_context_diagnostic=_diagnostic(interpretation),
    )


def _interpret(row: H4D1ContextInventoryRow, sensitivity: str) -> str:
    if row.d1_context_status == "D1_CONTEXT_UNAVAILABLE":
        return "D1_CONTEXT_UNAVAILABLE"
    if _sample_constrained(row.d1_sample_adequacy_class) or _sample_constrained(row.d1_dispersion_class):
        return "D1_CONTEXT_SAMPLE_CONSTRAINED"
    if sensitivity == "D1_REGIME_SENSITIVE" or _high(row.d1_dispersion_class):
        return "D1_CONTEXT_REGIME_SENSITIVE"
    if row.d1_context_status in {"D1_CONTEXT_AVAILABLE", "D1_CONTEXT_AVAILABLE_CONDITION_LEVEL"} and not _unavailable(
        row.d1_dispersion_class
    ):
        return "D1_CONTEXT_DESCRIPTIVE_REFERENCE"
    if row.d1_context_status in {"D1_CONTEXT_AVAILABLE", "D1_CONTEXT_AVAILABLE_SUMMARY_LEVEL"}:
        return "D1_CONTEXT_INPUT_LIMITED"
    return "D1_CONTEXT_INCONCLUSIVE"


def _inventory_diagnostic(mapping: ScenarioContextMapRow, has_d1: bool) -> str:
    if has_d1:
        if mapping.mapping_method == "CONDITION_PROFILE_MATCH":
            return "H4 context includes D1 condition-level context; no scenario/date alignment inferred."
        return f"H4 context includes D1 contextual layer via {mapping.mapping_method}."
    return "H4 context has no matched D1 contextual layer."


def _regime_sensitivity(value: str) -> str:
    text = str(value).upper()
    if "REGIME_SENSITIVE" in text or "HIGH" in text:
        return "D1_REGIME_SENSITIVE"
    if "UNAVAILABLE" in text or "MISSING" in text:
        return "D1_REGIME_SENSITIVITY_UNAVAILABLE"
    return "D1_REGIME_NOT_SENSITIVE_DESCRIPTIVE"


def _diagnostic(interpretation: str) -> str:
    diagnostics = {
        "D1_CONTEXT_REGIME_SENSITIVE": "D1 context indicates regime-sensitive descriptive behavior.",
        "D1_CONTEXT_SAMPLE_CONSTRAINED": "D1 context requires sample adequacy review.",
        "D1_CONTEXT_DESCRIPTIVE_REFERENCE": "D1 context is available as descriptive reference.",
        "D1_CONTEXT_INPUT_LIMITED": "D1 context inputs are incomplete.",
        "D1_CONTEXT_UNAVAILABLE": "D1 context inputs are unavailable.",
        "D1_CONTEXT_INCONCLUSIVE": "D1 context remains inconclusive.",
    }
    return diagnostics[interpretation]


def _high(value: str) -> bool:
    return "HIGH" in str(value).upper()


def _sample_constrained(value: str) -> bool:
    text = str(value).upper()
    if "ADEQUATE" in text or "SUFFICIENT" in text:
        return False
    return "CONSTRAINED" in text or "LOW_SAMPLE" in text or "LOW SAMPLE" in text


def _unavailable(value: str) -> bool:
    text = str(value or "").upper()
    return not text or "UNAVAILABLE" in text or "MISSING" in text


def _condition_match(
    h4: H4ContextRow,
    d1_rows: list[D1ContextRow],
    mapping: ScenarioContextMapRow,
) -> D1ContextRow | None:
    if mapping.mapping_method != "CONDITION_PROFILE_MATCH":
        return None
    transition = _matches(d1_rows, h4.h4_transition_label, h4.h4_forward_window, "TRANSITION")
    if transition:
        return _aggregate_condition_matches(transition, h4.h4_transition_label, h4.h4_forward_window)
    state = [
        *_matches(d1_rows, h4.h4_source_state, h4.h4_forward_window, "STATE"),
        *_matches(d1_rows, h4.h4_target_state, h4.h4_forward_window, "STATE"),
    ]
    if state:
        return _aggregate_condition_matches(state, mapping.d1_context_label, h4.h4_forward_window)
    return None


def _matches(d1_rows: list[D1ContextRow], label: str, forward_window: str, family: str) -> list[D1ContextRow]:
    normalized_label = _normalize_label(label)
    normalized_window = _normalize_window(forward_window)
    if not normalized_label or not normalized_window:
        return []
    return [
        row
        for row in d1_rows
        if row.d1_context_status == "D1_CONTEXT_AVAILABLE_CONDITION_LEVEL"
        and _condition_family(row, family)
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
        d1_readiness_flag=next((row.d1_readiness_flag for row in matches if row.d1_readiness_flag), ""),
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
        _high(row.d1_dispersion_class) or _high(row.d1_sensitivity_class) for row in matches
    ):
        return "SAMPLE_CONSTRAINED"
    return next((value for value in values if value), "D1_SAMPLE_ADEQUACY_UNAVAILABLE")


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
