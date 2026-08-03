"""Missing output diagnostics for H4 timestamped state/transition outputs."""

from __future__ import annotations

from sqre.h4_timestamped_state_transition_outputs.models import CoverageReviewRow, MissingOutputReviewRow


def build_missing_output_review(coverage_rows: list[CoverageReviewRow]) -> list[MissingOutputReviewRow]:
    rows: list[MissingOutputReviewRow] = []
    for coverage in coverage_rows:
        if coverage.timestamped_state_row_count == 0:
            rows.append(
                _missing_row(
                    len(rows) + 1,
                    coverage.scenario_id,
                    "TIMESTAMPED_MARKET_STATES",
                    coverage.coverage_class,
                    "GENERATE_MARKET_STATES_WITH_TIMESTAMPS",
                    "Timestamped market state rows are missing for this scenario.",
                )
            )
        if coverage.timestamped_transition_row_count == 0:
            rows.append(
                _missing_row(
                    len(rows) + 1,
                    coverage.scenario_id,
                    "TIMESTAMPED_STATE_TRANSITIONS",
                    coverage.coverage_class,
                    "GENERATE_STATE_TRANSITIONS_WITH_TIMESTAMPS",
                    "Timestamped state transition rows are missing for this scenario.",
                )
            )
    if rows:
        return rows
    return [
        MissingOutputReviewRow(
            missing_output_id="MISSING_OUTPUT_000000",
            scenario_id="ALL_SCENARIOS",
            missing_output_type="NONE",
            current_source_status="TIMESTAMPED_OUTPUTS_AVAILABLE",
            required_source_action="NO_ACTION_REQUIRED",
            missing_output_diagnostic="No missing timestamped state/transition outputs were identified.",
            recommended_follow_up="H4_TIMESTAMPED_CONTEXT_TABLE_GENERATION_RETRY",
        )
    ]


def _missing_row(
    index: int,
    scenario_id: str,
    missing_type: str,
    status: str,
    action: str,
    diagnostic: str,
) -> MissingOutputReviewRow:
    return MissingOutputReviewRow(
        missing_output_id=f"MISSING_OUTPUT_{index:06d}",
        scenario_id=scenario_id,
        missing_output_type=missing_type,
        current_source_status=status,
        required_source_action=action,
        missing_output_diagnostic=diagnostic,
        recommended_follow_up=action,
    )
