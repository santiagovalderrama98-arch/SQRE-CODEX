"""Unmatched alignment review for H4/D1 same-time alignment."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_alignment_table.models import UnmatchedAlignmentReviewRow


def build_unmatched_alignment_review(
    transition_alignment: pd.DataFrame,
    state_alignment: pd.DataFrame,
    *,
    d1_state_count: int,
) -> list[UnmatchedAlignmentReviewRow]:
    rows: list[UnmatchedAlignmentReviewRow] = []
    rows.extend(_unmatched_transition_rows(transition_alignment, d1_state_count, len(rows)))
    rows.extend(_unmatched_state_rows(state_alignment, d1_state_count, len(rows)))
    if rows:
        return rows
    return [
        UnmatchedAlignmentReviewRow(
            unmatched_id="UNMATCHED_000000",
            unmatched_source_type="NONE",
            h4_source_id="",
            h4_timestamp="",
            h4_date="",
            missing_match_type="NONE",
            current_status="NO_UNMATCHED_ALIGNMENT_ROWS",
            required_source_action="NO_ACTION_REQUIRED",
            unmatched_diagnostic="No unmatched H4/D1 same-time alignment rows were identified.",
            recommended_follow_up="H4_D1_SAME_TIME_CONTEXTUAL_REVIEW",
        )
    ]


def _unmatched_transition_rows(frame: pd.DataFrame, d1_state_count: int, offset: int) -> list[UnmatchedAlignmentReviewRow]:
    if frame.empty:
        return []
    unmatched = frame[frame["Alignment_Method"] == "NO_D1_SAME_TIME_MATCH"]
    rows: list[UnmatchedAlignmentReviewRow] = []
    for index, (_, row) in enumerate(unmatched.iterrows(), start=offset + 1):
        rows.append(
            _row(
                index,
                "H4_STATE_TRANSITION",
                row.get("H4_Transition_ID", ""),
                row.get("H4_Transition_Time", ""),
                row.get("H4_Transition_Date", ""),
                "D1_CONTEXT_NOT_FOUND",
                _required_action("transition", row.get("H4_Transition_Time", ""), d1_state_count),
            )
        )
    return rows


def _unmatched_state_rows(frame: pd.DataFrame, d1_state_count: int, offset: int) -> list[UnmatchedAlignmentReviewRow]:
    if frame.empty:
        return []
    unmatched = frame[frame["Alignment_Method"] == "NO_D1_SAME_TIME_MATCH"]
    rows: list[UnmatchedAlignmentReviewRow] = []
    for index, (_, row) in enumerate(unmatched.iterrows(), start=offset + 1):
        rows.append(
            _row(
                index,
                "H4_MARKET_STATE",
                row.get("H4_State_ID", ""),
                row.get("H4_State_Event_Time", ""),
                row.get("H4_State_Event_Date", ""),
                "D1_CONTEXT_NOT_FOUND",
                _required_action("state", row.get("H4_State_Event_Time", ""), d1_state_count),
            )
        )
    return rows


def _required_action(source_type: str, timestamp: object, d1_state_count: int) -> str:
    if d1_state_count == 0:
        return "REVIEW_D1_TIMESTAMPED_STATE_COVERAGE"
    if not str(timestamp).strip():
        return "REVIEW_H4_TRANSITION_TIMESTAMPS" if source_type == "transition" else "REVIEW_H4_STATE_TIMESTAMPS"
    return "REVIEW_SYNCHRONIZED_DATA_RANGE"


def _row(
    index: int,
    source_type: str,
    source_id: object,
    timestamp: object,
    date_value: object,
    missing_type: str,
    action: str,
) -> UnmatchedAlignmentReviewRow:
    return UnmatchedAlignmentReviewRow(
        unmatched_id=f"UNMATCHED_{index:06d}",
        unmatched_source_type=source_type,
        h4_source_id="" if pd.isna(source_id) else str(source_id),
        h4_timestamp="" if pd.isna(timestamp) else str(timestamp),
        h4_date="" if pd.isna(date_value) else str(date_value),
        missing_match_type=missing_type,
        current_status="UNMATCHED",
        required_source_action=action,
        unmatched_diagnostic=f"{source_type} did not find same-time D1 context.",
        recommended_follow_up=action,
    )
