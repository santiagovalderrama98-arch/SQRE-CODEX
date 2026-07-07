import pandas as pd

from sqre.event_analytics.transition_matrix import TransitionMatrix
from sqre.transition_engine.matrix import build_transition_matrix
from sqre.transition_engine.models import StateTransition, TransitionMetrics


def test_transition_matrix_computes_counts_and_probabilities():
    events = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=4, freq="5min"),
            "EventType": ["PIVOT_LOW", "PIVOT_HIGH", "PIVOT_LOW", "PIVOT_HIGH"],
            "Price": [1.0, 1.1, 1.0, 1.2],
        }
    )

    matrix = TransitionMatrix().build(events)

    row = matrix[(matrix["CurrentEvent"] == "PIVOT_LOW") & (matrix["NextEvent"] == "PIVOT_HIGH")].iloc[0]
    assert row["Count"] == 2
    assert row["Probability"] == 1.0
    assert row["Percentage"] == 100.0


def transition(from_state: str, to_state: str, magnitude: float, stability: float, confidence_change: float, quality_change: float):
    return StateTransition(
        transition_id="TRN",
        from_state_id="FROM",
        to_state_id="TO",
        from_structure_id="FROM_STR",
        to_structure_id="TO_STR",
        symbol="EURUSD",
        timeframe="M5",
        from_market_state=from_state,
        to_market_state=to_state,
        transition_label=f"{from_state} -> {to_state}",
        start_time=pd.Timestamp("2026-01-01").to_pydatetime(),
        end_time=pd.Timestamp("2026-01-01 00:05:00").to_pydatetime(),
        transition_duration_seconds=0.0,
        from_direction="UP",
        to_direction="UP",
        state_changed=from_state != to_state,
        direction_changed=False,
        primary_transition_type="STATE_CHANGE",
        transition_tags="CONFIDENCE_STABLE|STRUCTURAL_STABLE|LOW_MAGNITUDE",
        metrics=TransitionMetrics(
            persistence_change=0.0,
            complexity_change=0.0,
            stability_change=0.0,
            efficiency_change=0.0,
            density_change=0.0,
            volatility_change=0.0,
            symmetry_change=0.0,
            structural_confidence_change=0.0,
            state_confidence_change=confidence_change,
            price_displacement_change=0.0,
            duration_change=0.0,
            event_count_change=0,
            leg_count_change=0,
            persistence_abs_change=0.0,
            complexity_abs_change=0.0,
            stability_abs_change=0.0,
            efficiency_abs_change=0.0,
            density_abs_change=0.0,
            volatility_abs_change=0.0,
            symmetry_abs_change=0.0,
            structural_confidence_abs_change=0.0,
            state_confidence_abs_change=abs(confidence_change),
            transition_magnitude=magnitude,
            transition_stability=stability,
            structural_quality_change=quality_change,
        ),
    )


def test_transition_engine_matrix_groups_counts_probabilities_and_averages():
    rows = build_transition_matrix(
        [
            transition("A", "B", 0.2, 0.8, 0.1, 0.2),
            transition("A", "B", 0.4, 0.6, 0.3, 0.0),
            transition("A", "C", 0.6, 0.4, -0.1, -0.2),
            transition("B", "C", 0.1, 0.9, 0.0, 0.1),
        ]
    )

    ab = next(row for row in rows if row.from_state == "A" and row.to_state == "B")

    assert ab.count == 2
    assert round(ab.probability, 4) == round(2 / 3, 4)
    assert round(ab.percentage, 4) == round((2 / 3) * 100, 4)
    assert round(ab.average_transition_magnitude, 4) == 0.3
    assert round(ab.average_transition_stability, 4) == 0.7
    assert round(ab.average_state_confidence_change, 4) == 0.2
    assert round(ab.average_structural_quality_change, 4) == 0.1
