from sqre.h4_d1_structural_research.models import H4D1StructuralResearchResult, TimeframeResearchSummary
from sqre.h4_d1_structural_research.reports import write_h4_d1_research_report


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path):
    report = tmp_path / "report.txt"
    result = H4D1StructuralResearchResult(
        input_validation_summary="summary.csv",
        validation_output_dir="validation",
        scenarios_loaded=1,
        output_dir=tmp_path,
        report_path=report,
        timeframe_summaries=[_summary()],
    )

    write_h4_d1_research_report(report, result)
    text = report.read_text(encoding="utf-8")

    assert "SQRE H4/D1 Structural Research Report" in text
    assert "Executive Diagnostic Summary" in text
    assert "Scenario Inventory" in text
    assert "Research Readiness Assessment" in text
    assert "No comparative ordering is produced." in text
    assert not _contains_forbidden_language(text)


def _summary():
    return TimeframeResearchSummary(
        timeframe="D1",
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
        timeframe_research_diagnostic="D1 state distribution is structurally consistent across historical periods",
        recommended_follow_up="Continue D1 descriptive structural research review.",
    )


def _contains_forbidden_language(text: str) -> bool:
    forbidden = [
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
    lower = text.lower()
    return any(term in lower for term in forbidden)
