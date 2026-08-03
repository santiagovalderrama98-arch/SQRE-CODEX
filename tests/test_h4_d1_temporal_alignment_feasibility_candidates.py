from __future__ import annotations

from sqre.h4_d1_temporal_alignment_feasibility_review.alignment_candidate_review import classify_candidate
from sqre.h4_d1_temporal_alignment_feasibility_review.models import TemporalKeyInventoryRow


def test_candidate_classifies_exact_timestamp_alignment_readiness():
    _method, feasibility, confidence, _diagnostic = classify_candidate(
        _key("H4", timestamp="Timestamp"),
        _key("D1", timestamp="Timestamp"),
    )

    assert feasibility == "READY_FOR_EXACT_TIMESTAMP_ALIGNMENT"
    assert confidence == "HIGH_CONFIDENCE_TEMPORAL_ALIGNMENT_READY"


def test_candidate_classifies_interval_overlap_readiness():
    method, feasibility, _confidence, _diagnostic = classify_candidate(
        _key("H4", start="Start_Time", end="End_Time"),
        _key("D1", timestamp="Date"),
    )

    assert method == "H4_INTERVAL_TO_D1_INTERVAL_OVERLAP"
    assert feasibility == "READY_FOR_INTERVAL_OVERLAP_ALIGNMENT"


def test_candidate_classifies_scenario_period_readiness():
    method, feasibility, _confidence, _diagnostic = classify_candidate(
        _key("H4", start="Period_Start", end="Period_End", scenario="Scenario_ID"),
        _key("D1", start="Period_Start", end="Period_End", scenario="Scenario_ID"),
    )

    assert method == "SCENARIO_PERIOD_JOIN"
    assert feasibility == "READY_FOR_SCENARIO_PERIOD_ALIGNMENT"


def test_candidate_does_not_classify_condition_only_as_temporal_alignment():
    method, feasibility, confidence, diagnostic = classify_candidate(
        _key("H4", condition="Condition_Label|Forward_Window", status="CONDITION_ONLY_KEYS_AVAILABLE"),
        _key("D1", condition="Condition_Label|Forward_Window", status="CONDITION_ONLY_KEYS_AVAILABLE"),
    )

    assert method == "CONDITION_ONLY_MATCH_NOT_TEMPORAL"
    assert feasibility == "CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT"
    assert confidence == "NO_TEMPORAL_ALIGNMENT_CONFIDENCE"
    assert "do not prove same-time alignment" in diagnostic


def _key(
    side: str,
    timestamp: str = "",
    start: str = "",
    end: str = "",
    scenario: str = "",
    condition: str = "",
    status: str | None = None,
) -> TemporalKeyInventoryRow:
    key_status = status
    if key_status is None:
        if timestamp:
            key_status = "EXACT_TIMESTAMP_KEYS_AVAILABLE"
        elif scenario and start and end:
            key_status = "SCENARIO_PERIOD_KEYS_AVAILABLE"
        elif start and end:
            key_status = "START_END_TIME_KEYS_AVAILABLE"
        else:
            key_status = "TEMPORAL_KEYS_MISSING"
    return TemporalKeyInventoryRow(
        source_name=f"{side.lower()}_source",
        source_type=f"{side}_SOURCE",
        file_name="source.csv",
        rows_loaded=1,
        timestamp_columns=timestamp,
        start_time_columns=start,
        end_time_columns=end,
        scenario_id_columns=scenario,
        timeframe_columns="",
        condition_only_columns=condition,
        regime_columns="",
        temporal_key_status=key_status,
        temporal_key_diagnostic="diagnostic",
    )
