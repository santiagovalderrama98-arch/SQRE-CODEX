"""Missing output review for timestamped H4/D1 state/regime generation."""

from __future__ import annotations

from sqre.timestamped_h4_d1_state_regime_generation.models import CoverageReviewRow, MissingOutputReviewRow


def build_missing_output_review(coverage: CoverageReviewRow) -> list[MissingOutputReviewRow]:
    rows: list[MissingOutputReviewRow] = []
    if "INPUT_MISSING" in {
        coverage.h4_state_coverage_class,
        coverage.h4_transition_coverage_class,
        coverage.d1_state_coverage_class,
    }:
        rows.append(_row(1, "SYNCHRONIZED_INPUTS", "INPUT_MISSING", "REVIEW_SYNCHRONIZED_INPUT_COMPLETENESS"))
        return rows
    if coverage.h4_state_coverage_class == "TIMESTAMPED_OUTPUT_MISSING":
        rows.append(_row(len(rows) + 1, "H4_MARKET_STATES", "MISSING", "GENERATE_H4_MARKET_STATES"))
    if coverage.h4_transition_coverage_class == "TIMESTAMPED_OUTPUT_MISSING":
        rows.append(_row(len(rows) + 1, "H4_STATE_TRANSITIONS", "MISSING", "GENERATE_H4_STATE_TRANSITIONS"))
    if coverage.d1_state_coverage_class == "TIMESTAMPED_OUTPUT_MISSING":
        rows.append(_row(len(rows) + 1, "D1_MARKET_STATES", "MISSING", "GENERATE_D1_MARKET_STATES"))
    if rows:
        return rows
    return [
        MissingOutputReviewRow(
            missing_output_id="MISSING_OUTPUT_000000",
            missing_output_type="NONE",
            current_status="TIMESTAMPED_OUTPUTS_AVAILABLE",
            required_source_action="NO_ACTION_REQUIRED",
            missing_output_diagnostic="No missing timestamped output issue was identified.",
            recommended_follow_up="BUILD_H4_D1_SAME_TIME_ALIGNMENT_TABLE",
        )
    ]


def _row(index: int, missing_type: str, status: str, action: str) -> MissingOutputReviewRow:
    return MissingOutputReviewRow(
        missing_output_id=f"MISSING_OUTPUT_{index:06d}",
        missing_output_type=missing_type,
        current_status=status,
        required_source_action=action,
        missing_output_diagnostic=f"{missing_type} requires review.",
        recommended_follow_up=action,
    )
