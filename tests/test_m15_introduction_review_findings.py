from sqre.m15_introduction_review.config import M15IntroductionReviewConfig
from sqre.m15_introduction_review.findings import build_m15_review_findings
from sqre.m15_introduction_review.metrics import build_m15_review_rows
from sqre.m15_introduction_review.models import M15Context, M15ValidationSummaryRow


def test_findings_cover_m15_diagnostic_categories():
    rows = build_m15_review_rows(
        [
            M15ValidationSummaryRow(
                scenario_id="eurusd_m15_period_1",
                timeframe="M15",
                status="COMPLETED",
                ohlc_rows=100,
                structures_detected=10,
                average_structure_duration=7200,
                unique_states=5,
                most_common_state="DIRECTIONAL_DRIFT",
                average_forward_range_pips=8,
                direction_alignment_rate=0.4,
                low_sample_conditions_research=4,
                low_sample_conditions_price_outcome=3,
                states_generated=10,
                directional_displacement_count=5,
            )
        ],
        M15IntroductionReviewConfig(),
        M15Context(),
    )

    findings = build_m15_review_findings(rows)

    assert {finding.finding_type for finding in findings} == {
        "STRUCTURE_STABILITY",
        "DURATION_UTILIZATION",
        "STATE_DIVERSITY",
        "LOW_SAMPLE_PRESSURE",
        "FORWARD_RANGE_STABILITY",
        "DIAGNOSTIC_PROFILE",
    }
    assert not _contains_forbidden_language("\n".join(finding.message for finding in findings))


def _contains_forbidden_language(text: str) -> bool:
    forbidden = [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "take profit",
        "stop loss",
        "profitable",
        "best timeframe",
        "ranking",
        "should trade",
        "predicts",
        "optimal",
    ]
    lower = text.lower()
    return any(term in lower for term in forbidden)
