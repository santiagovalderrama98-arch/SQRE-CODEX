from sqre.h4_transition_outcome_deep_dive.transition_parser import parse_transition_label


def test_transition_parser_handles_supported_formats():
    assert parse_transition_label("DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION").source_state == "DIRECTIONAL_DISPLACEMENT"
    assert parse_transition_label("DIRECTIONAL_DISPLACEMENT_TO_DIRECTIONAL_EXPANSION").target_state == "DIRECTIONAL_EXPANSION"
    assert parse_transition_label("VOLATILE_ROTATION|DIRECTIONAL_DISPLACEMENT").transition_family == "ROTATION_TO_DIRECTIONAL"
    assert parse_transition_label("TRANSITION:DIRECTIONAL_DISPLACEMENT:DIRECTIONAL_DISPLACEMENT").transition_family == "DIRECTIONAL_TO_DIRECTIONAL"


def test_transition_parser_handles_unknown_labels_safely():
    parsed = parse_transition_label("UNREADABLE")

    assert parsed.source_state == "UNKNOWN"
    assert parsed.target_state == "UNKNOWN"
    assert parsed.transition_family == "UNKNOWN_TRANSITION_FAMILY"
