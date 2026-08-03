from sqre.h4_timestamped_context_table_generation.temporal_key_builder import event_date, temporal_key_class


def test_temporal_key_builder_creates_event_date_and_alignment_key():
    assert event_date("2026-01-02 04:00:00") == "2026-01-02"
    assert temporal_key_class("2026-01-02 04:00:00", "2026-01-01", "2026-01-31") == "EXACT_EVENT_TIMESTAMP"
    assert temporal_key_class("", "2026-01-01", "2026-01-31") == "TEMPORAL_KEY_INCOMPLETE"
