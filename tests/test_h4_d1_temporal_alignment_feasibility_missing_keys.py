from sqre.h4_d1_temporal_alignment_feasibility_review.missing_key_review import build_missing_key_review
from sqre.h4_d1_temporal_alignment_feasibility_review.models import TemporalKeyInventoryRow


def test_missing_key_review_recommends_h4_timestamped_context_table():
    rows = build_missing_key_review(
        [
            TemporalKeyInventoryRow(
                source_name="h4_context",
                source_type="H4_COMBINED_CONTEXT",
                file_name="h4.csv",
                rows_loaded=1,
                timestamp_columns="",
                start_time_columns="",
                end_time_columns="",
                scenario_id_columns="",
                timeframe_columns="",
                condition_only_columns="Context_ID|Transition_Label|Forward_Window",
                regime_columns="",
                temporal_key_status="CONDITION_ONLY_KEYS_AVAILABLE",
                temporal_key_diagnostic="condition only",
            )
        ]
    )

    assert rows[0].required_source_action == "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE"
    assert "generate timestamped H4 context rows" in rows[0].missing_key_diagnostic
