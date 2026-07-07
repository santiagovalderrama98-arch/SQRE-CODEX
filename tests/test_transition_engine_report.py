from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqre.transition_engine.models import (
    StateTransition,
    TransitionEngineSummary,
    TransitionMetrics,
    TransitionSequence,
)
from sqre.transition_engine.reports import write_transition_engine_report


def metrics() -> TransitionMetrics:
    return TransitionMetrics(
        persistence_change=0,
        complexity_change=0,
        stability_change=0,
        efficiency_change=0,
        density_change=0,
        volatility_change=0,
        symmetry_change=0,
        structural_confidence_change=0,
        state_confidence_change=0.2,
        price_displacement_change=0,
        duration_change=0,
        event_count_change=0,
        leg_count_change=0,
        persistence_abs_change=0,
        complexity_abs_change=0,
        stability_abs_change=0,
        efficiency_abs_change=0,
        density_abs_change=0,
        volatility_abs_change=0,
        symmetry_abs_change=0,
        structural_confidence_abs_change=0,
        state_confidence_abs_change=0.2,
        transition_magnitude=0.3,
        transition_stability=0.7,
        structural_quality_change=0.1,
    )


def transition(kind: str, tags: str) -> StateTransition:
    return StateTransition(
        transition_id="TRN_000001",
        from_state_id="STATE_000001",
        to_state_id="STATE_000002",
        from_structure_id="STR_000001",
        to_structure_id="STR_000002",
        symbol="EURUSD",
        timeframe="M5",
        from_market_state="A",
        to_market_state="B",
        transition_label="A -> B",
        start_time=datetime(2026, 1, 1),
        end_time=datetime(2026, 1, 1),
        transition_duration_seconds=0,
        from_direction="UP",
        to_direction="DOWN",
        state_changed=True,
        direction_changed=True,
        primary_transition_type=kind,
        transition_tags=tags,
        metrics=metrics(),
    )


def summary(tmp_path) -> TransitionEngineSummary:
    return TransitionEngineSummary(
        symbol="EURUSD",
        timeframe="M5",
        period_start=datetime(2026, 1, 1),
        period_end=datetime(2026, 1, 2),
        states_processed=3,
        transitions_generated=2,
        unique_states=2,
        unique_transitions=1,
        most_common_transition="A -> B",
        most_common_sequence="A -> B -> A",
        state_change_rate=0.5,
        direction_change_rate=0.5,
        average_transition_duration=300,
        average_transition_magnitude=0.3,
        average_transition_stability=0.7,
        average_state_confidence_change=0.2,
        average_structural_quality_change=0.1,
        state_transitions_path=tmp_path / "state_transitions.csv",
        transition_matrix_path=tmp_path / "transition_matrix.csv",
        transition_sequences_path=tmp_path / "transition_sequences.csv",
        report_path=tmp_path / "report.txt",
    )


def test_transition_engine_report_is_generated_and_descriptive(tmp_path) -> None:
    report_path = tmp_path / "transition_engine_report.txt"
    transitions = [
        transition("DIRECTION_CHANGE", "CONFIDENCE_EXPANSION|STRUCTURAL_IMPROVEMENT|MODERATE_MAGNITUDE"),
        transition("STATE_CHANGE", "CONFIDENCE_STABLE|STRUCTURAL_STABLE|LOW_MAGNITUDE"),
    ]
    sequences = [
        TransitionSequence(
            sequence_id="SEQ_000001",
            sequence="A -> B -> A",
            length=3,
            count=2,
            frequency=1,
            percentage=100,
            average_duration=600,
            average_transition_magnitude=0.3,
        )
    ]

    write_transition_engine_report(report_path, summary(tmp_path), transitions, [], sequences)

    text = report_path.read_text(encoding="utf-8")
    assert "SQRE Transition Engine Report" in text
    assert "Most Common Transition: A -> B" in text
    assert "Most Common Sequence: A -> B -> A" in text
    assert "State Change Rate: 0.5000" in text
    assert "Direction Change Rate: 0.5000" in text
    assert "- Direction Change: 1" in text
    assert "- State Change: 1" in text
    assert "- Confidence Expansion: 1" in text
    assert "- Structural Improvement: 1" in text
    assert "- Low Magnitude: 1" in text
    for forbidden in [
        "Buy",
        "Sell",
        "Entry",
        "Exit",
        "Take profit",
        "Stop loss",
        "Reversal expected",
        "Continuation expected",
        "Trade signal",
        "Opportunity",
    ]:
        assert forbidden not in text
