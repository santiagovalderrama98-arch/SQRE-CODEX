from sqre.h4_transition_scenario_sensitive_review.findings import (
    profile_diagnostic,
    scenario_review_diagnostic,
    summary_diagnostic,
)


FORBIDDEN = [
    "buy",
    "sell",
    "entry",
    "exit",
    "trade signal",
    "trade setup",
    "take profit",
    "stop loss",
    "profitable",
    "opportunity",
    "edge",
    "best timeframe",
    "ranking",
    "should trade",
    "predicts",
    "optimal",
]


def test_findings_are_descriptive_and_non_ranking():
    text = "\n".join(
        [
            profile_diagnostic("HIGH_TRANSITION_SCENARIO_SENSITIVITY"),
            scenario_review_diagnostic("HIGH_RECURRENT_DEVIATION"),
            summary_diagnostic(0, 3, 3),
        ]
    ).lower()

    assert all(term not in text for term in FORBIDDEN)
