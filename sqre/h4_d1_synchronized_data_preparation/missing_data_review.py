"""Missing data review for H4/D1 synchronization preparation."""

from __future__ import annotations

from sqre.h4_d1_synchronized_data_preparation.models import H4ContinuityReviewRow, MissingDataReviewRow, SynchronizationReviewRow


def build_missing_data_review(
    continuity: H4ContinuityReviewRow,
    synchronization: SynchronizationReviewRow,
) -> list[MissingDataReviewRow]:
    rows: list[MissingDataReviewRow] = []
    if continuity.h4_continuity_class == "H4_INPUT_MISSING":
        rows.append(_row(1, "H4_HISTORICAL_OHLC", "MISSING", "PROVIDE_H4_HISTORICAL_OHLC", "H4 historical OHLC input is missing."))
    if continuity.conflicting_duplicate_timestamp_count > 0:
        rows.append(_row(len(rows) + 1, "H4_DUPLICATE_TIMESTAMPS", "CONFLICTING", "REVIEW_DUPLICATE_TIMESTAMPS", "Conflicting duplicate H4 timestamps were found."))
    if continuity.h4_continuity_class in {"PARTIAL_H4_CONTINUITY", "LOW_H4_CONTINUITY"}:
        rows.append(_row(len(rows) + 1, "H4_TIMESTAMP_CONTINUITY", continuity.h4_continuity_class, "REVIEW_H4_TIMESTAMP_CONTINUITY", "H4 continuity requires review."))
    if synchronization.unaligned_h4_row_count > 0:
        rows.append(_row(len(rows) + 1, "H4_D1_ALIGNMENT", "UNALIGNED_H4_ROWS", "REBUILD_D1_FROM_H4_AFTER_DATA_FIX", "Some H4 candles could not be mapped to derived D1 candles."))
    if rows:
        return rows
    return [
        MissingDataReviewRow(
            missing_data_id="MISSING_DATA_000000",
            missing_data_type="NONE",
            current_status="SYNCHRONIZED_DATA_AVAILABLE",
            required_source_action="NO_ACTION_REQUIRED",
            missing_data_diagnostic="No missing synchronized data issue was identified.",
            recommended_follow_up="GENERATE_TIMESTAMPED_H4_D1_STATE_REGIME_TABLES",
        )
    ]


def _row(index: int, missing_type: str, status: str, action: str, diagnostic: str) -> MissingDataReviewRow:
    return MissingDataReviewRow(
        missing_data_id=f"MISSING_DATA_{index:06d}",
        missing_data_type=missing_type,
        current_status=status,
        required_source_action=action,
        missing_data_diagnostic=diagnostic,
        recommended_follow_up=action,
    )
