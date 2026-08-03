"""Missing temporal key review for H4/D1 feasibility."""

from __future__ import annotations

from sqre.h4_d1_temporal_alignment_feasibility_review.models import MissingTemporalKeyReviewRow, TemporalKeyInventoryRow
from sqre.h4_d1_temporal_alignment_feasibility_review.temporal_key_inventory import has_temporal_alignment_keys


def build_missing_key_review(keys: list[TemporalKeyInventoryRow]) -> list[MissingTemporalKeyReviewRow]:
    rows: list[MissingTemporalKeyReviewRow] = []
    for key in keys:
        if key.temporal_key_status == "INPUT_MISSING":
            rows.append(_row(len(rows) + 1, key, "INPUT_FILE", "REVIEW_SOURCE_INPUT_COMPLETENESS"))
            continue
        if not has_temporal_alignment_keys(key):
            action = _action_for_source(key)
            rows.append(_row(len(rows) + 1, key, "TIMESTAMP_OR_INTERVAL_KEY", action))
    return rows


def _row(
    index: int,
    key: TemporalKeyInventoryRow,
    missing_type: str,
    action: str,
) -> MissingTemporalKeyReviewRow:
    return MissingTemporalKeyReviewRow(
        missing_key_id=f"MISS_{index:06d}",
        source_name=key.source_name,
        source_type=key.source_type,
        missing_key_type=missing_type,
        current_key_status=key.temporal_key_status,
        required_key_for_same_time_alignment="Timestamp, interval, or scenario-period keys",
        required_source_action=action,
        missing_key_diagnostic=_diagnostic(key, action),
    )


def _action_for_source(key: TemporalKeyInventoryRow) -> str:
    if key.source_type == "H4_COMBINED_CONTEXT":
        return "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE"
    if key.source_type.startswith("D1"):
        return "GENERATE_D1_TIMESTAMPED_REGIME_TABLE"
    if key.source_type in {"H4_D1_STRUCTURAL_RESEARCH", "H4_D1_VALIDATION"}:
        return "GENERATE_H4_D1_SCENARIO_MAPPING_TABLE"
    return "REVIEW_SOURCE_INPUT_COMPLETENESS"


def _diagnostic(key: TemporalKeyInventoryRow, action: str) -> str:
    if key.temporal_key_status == "INPUT_MISSING":
        return "Source is missing; review source input completeness before temporal alignment."
    if action == "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE":
        return "H4 context lacks same-time keys; generate timestamped H4 context rows."
    if action == "GENERATE_D1_TIMESTAMPED_REGIME_TABLE":
        return "D1 context lacks same-time keys; generate timestamped D1 regime/state rows."
    if action == "GENERATE_H4_D1_SCENARIO_MAPPING_TABLE":
        return "Scenario-period mapping keys are incomplete for H4/D1 temporal alignment."
    return "Temporal alignment keys are incomplete."
