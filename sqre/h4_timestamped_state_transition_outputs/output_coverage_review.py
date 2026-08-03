"""Coverage review for H4 timestamped state/transition outputs."""

from __future__ import annotations

from collections import Counter

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.models import (
    CoverageReviewRow,
    ScenarioInventoryRow,
    TimestampedMarketStateRow,
    TimestampedStateTransitionRow,
)


def build_coverage_review(
    scenarios: list[ScenarioInventoryRow],
    state_rows: list[TimestampedMarketStateRow],
    transition_rows: list[TimestampedStateTransitionRow],
    config: H4TimestampedStateTransitionConfig,
) -> list[CoverageReviewRow]:
    states_by_scenario: dict[str, list[TimestampedMarketStateRow]] = {}
    transitions_by_scenario: dict[str, list[TimestampedStateTransitionRow]] = {}
    for row in state_rows:
        states_by_scenario.setdefault(row.scenario_id, []).append(row)
    for row in transition_rows:
        transitions_by_scenario.setdefault(row.scenario_id, []).append(row)

    coverage: list[CoverageReviewRow] = []
    for scenario in scenarios:
        states = states_by_scenario.get(scenario.scenario_id, [])
        transitions = transitions_by_scenario.get(scenario.scenario_id, [])
        expected_states = _expected_count(scenario.expected_state_count, len(states))
        expected_transitions = _expected_count(scenario.expected_transition_count, len(transitions))
        state_ratio = len(states) / expected_states if expected_states else 0.0
        transition_ratio = len(transitions) / expected_transitions if expected_transitions else 0.0
        coverage_class = _coverage_class(state_ratio, transition_ratio, len(states), len(transitions), config)
        coverage.append(
            CoverageReviewRow(
                scenario_id=scenario.scenario_id,
                symbol=scenario.symbol,
                timeframe=scenario.timeframe,
                period_start=scenario.period_start,
                period_end=scenario.period_end,
                expected_state_count=expected_states,
                expected_transition_count=expected_transitions,
                timestamped_state_row_count=len(states),
                timestamped_transition_row_count=len(transitions),
                state_temporal_key_complete_row_count=sum(1 for row in states if row.state_event_time and row.state_event_date),
                transition_temporal_key_complete_row_count=sum(
                    1 for row in transitions if row.transition_time and row.transition_date
                ),
                state_coverage_ratio=round(state_ratio, 4),
                transition_coverage_ratio=round(transition_ratio, 4),
                coverage_class=coverage_class,
                coverage_diagnostic=_coverage_diagnostic(coverage_class),
            )
        )
    return coverage


def dominant_coverage_class(rows: list[CoverageReviewRow]) -> str:
    if not rows:
        return "NO_TIMESTAMPED_STATE_TRANSITION_COVERAGE"
    counts = Counter(row.coverage_class for row in rows)
    priority = [
        "FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE",
        "PARTIAL_TIMESTAMPED_STATE_TRANSITION_COVERAGE",
        "STATES_ONLY_TIMESTAMPED_COVERAGE",
        "TRANSITIONS_ONLY_TIMESTAMPED_COVERAGE",
        "LOW_TIMESTAMPED_STATE_TRANSITION_COVERAGE",
        "NO_TIMESTAMPED_STATE_TRANSITION_COVERAGE",
    ]
    return max(priority, key=lambda item: (counts.get(item, 0), -priority.index(item)))


def _expected_count(value: int, observed: int) -> int:
    return value if value > 0 else observed


def _coverage_class(
    state_ratio: float,
    transition_ratio: float,
    state_count: int,
    transition_count: int,
    config: H4TimestampedStateTransitionConfig,
) -> str:
    if state_count == 0 and transition_count == 0:
        return "NO_TIMESTAMPED_STATE_TRANSITION_COVERAGE"
    if state_count > 0 and transition_count == 0:
        return "STATES_ONLY_TIMESTAMPED_COVERAGE"
    if state_count == 0 and transition_count > 0:
        return "TRANSITIONS_ONLY_TIMESTAMPED_COVERAGE"
    if state_ratio >= config.minimum_scenario_coverage_ratio and transition_ratio >= config.minimum_scenario_coverage_ratio:
        return "FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE"
    if state_ratio >= 0.50 or transition_ratio >= 0.50:
        return "PARTIAL_TIMESTAMPED_STATE_TRANSITION_COVERAGE"
    return "LOW_TIMESTAMPED_STATE_TRANSITION_COVERAGE"


def _coverage_diagnostic(coverage_class: str) -> str:
    mapping = {
        "FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE": "Scenario has timestamped states and transitions available.",
        "PARTIAL_TIMESTAMPED_STATE_TRANSITION_COVERAGE": "Scenario has partial timestamped state/transition coverage.",
        "STATES_ONLY_TIMESTAMPED_COVERAGE": "Scenario has timestamped states, but timestamped transitions are missing.",
        "TRANSITIONS_ONLY_TIMESTAMPED_COVERAGE": "Scenario has timestamped transitions, but timestamped states are missing.",
        "LOW_TIMESTAMPED_STATE_TRANSITION_COVERAGE": "Scenario has low timestamped state/transition coverage.",
        "NO_TIMESTAMPED_STATE_TRANSITION_COVERAGE": "Scenario has no timestamped state/transition rows.",
    }
    return mapping.get(coverage_class, "Scenario coverage was classified.")
