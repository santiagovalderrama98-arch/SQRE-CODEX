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


def _period_token(value: str) -> str:
    text = str(value)
    marker = "period_"
    if marker not in text:
        return ""
    suffix = text.split(marker, 1)[1]
    return suffix.split("_", 1)[0]
