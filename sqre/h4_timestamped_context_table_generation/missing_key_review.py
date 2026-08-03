"""Missing context diagnostics for H4 timestamped context table generation."""

from __future__ import annotations

from sqre.h4_timestamped_context_table_generation.models import MissingContextReviewRow, ScenarioInventoryRow


def build_missing_context_review(scenarios: list[ScenarioInventoryRow]) -> list[MissingContextReviewRow]:
    rows: list[MissingContextReviewRow] = []
    for scenario in scenarios:
        if scenario.scenario_context_coverage_class == "TIMESTAMPED_CONTEXT_AVAILABLE":
            continue
        action = _required_action(scenario)
        rows.append(
            MissingContextReviewRow(
                missing_context_id=f"MISSING_H4_CTX_{len(rows) + 1:06d}",
                scenario_id=scenario.scenario_id,
                missing_source_type=_missing_source_type(scenario),
                missing_source_diagnostic=scenario.scenario_diagnostic,
                required_source_action=action,
                recommended_follow_up=_follow_up(action),
            )
        )
    return rows


def _missing_source_type(scenario: ScenarioInventoryRow) -> str:
    if scenario.scenario_status == "SCENARIO_INPUT_MISSING":
        return "SCENARIO_INVENTORY"
    if not scenario.timestamped_transition_source_available:
        return "TIMESTAMPED_TRANSITION_OUTPUT"
    return "TIMESTAMPED_CONTEXT_OUTPUT"


def _required_action(scenario: ScenarioInventoryRow) -> str:
    if scenario.scenario_status == "SCENARIO_INPUT_MISSING":
        return "REVIEW_VALIDATION_OUTPUT_DIRECTORY_STRUCTURE"
    if not scenario.timestamped_transition_source_available and not scenario.timestamped_state_source_available:
        return "GENERATE_STATE_TRANSITION_OUTPUTS_WITH_TIMESTAMPS"
    if scenario.timestamped_state_source_available and not scenario.timestamped_transition_source_available:
        return "GENERATE_STATE_TRANSITION_OUTPUTS_WITH_TIMESTAMPS"
    if scenario.timestamped_context_row_count == 0:
        return "ADD_EVENT_TIME_TO_CONTEXT_OUTPUTS"
    return "NO_ACTION_REQUIRED"


def _follow_up(action: str) -> str:
    mapping = {
        "REVIEW_VALIDATION_OUTPUT_DIRECTORY_STRUCTURE": "Confirm scenario validation output paths and filenames.",
        "GENERATE_STATE_TRANSITION_OUTPUTS_WITH_TIMESTAMPS": "Generate timestamped H4 state transition outputs.",
        "GENERATE_MARKET_STATE_OUTPUTS_WITH_TIMESTAMPS": "Generate timestamped H4 market state outputs.",
        "ADD_SCENARIO_ID_TO_TRANSITION_OUTPUTS": "Add scenario identifiers to H4 transition outputs.",
        "ADD_EVENT_TIME_TO_CONTEXT_OUTPUTS": "Add event timestamps to H4 context outputs.",
        "NO_ACTION_REQUIRED": "No follow-up required for this scenario.",
    }
    return mapping.get(action, "Review H4 timestamped context completeness.")
