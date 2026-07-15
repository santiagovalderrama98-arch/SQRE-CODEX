from sqre.h4_d1_structural_research.findings import build_h4_d1_findings
from sqre.h4_d1_structural_research.models import TimeframeResearchSummary


def test_findings_are_descriptive_and_non_ranking():
    findings = build_h4_d1_findings([_summary()])
    text = " ".join(finding.message for finding in findings)

    assert findings[0].finding_type == "STRUCTURAL_MATURITY"
    assert "H4 structural research baseline appears mature" in text
    assert "best" not in text.lower()
    assert "ranking" not in text.lower()


def _summary():
    return TimeframeResearchSummary(
        timeframe="H4",
        scenario_count=4,
        completed_scenario_count=4,
        total_ohlc_rows=100,
        average_structures_detected=10,
        structure_count_cv=0.1,
        average_states_generated=10,
        average_unique_states=4,
        most_common_state_mode="A",
        average_forward_range_pips=12,
        forward_range_cv=0.1,
        average_direction_alignment_rate=0.4,
        average_low_sample_conditions_research=1,
        average_low_sample_conditions_price_outcome=2,
        state_profile_count=3,
        transition_profile_count=2,
        price_outcome_profile_count=2,
        sequence_profile_count=1,
        structural_maturity_flag="MATURE_RESEARCH_CONTEXT",
        research_sample_quality_flag="MODERATE",
        scenario_sensitivity_flag="MODERATE",
        timeframe_research_diagnostic="H4 structural research baseline appears mature",
        recommended_follow_up="Review H4 state and transition outcome detail.",
    )
