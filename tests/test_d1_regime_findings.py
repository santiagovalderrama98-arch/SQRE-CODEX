from sqre.d1_regime_normalized_research.findings import build_d1_regime_summary, summary_diagnostic
from sqre.d1_regime_normalized_research.models import D1RegimeConditionProfile, D1RegimeScenarioData, D1RegimeScenarioInventoryRow


def test_findings_are_descriptive_and_non_ranking():
    summary = build_d1_regime_summary([_scenario("a"), _scenario("b"), _scenario("c"), _scenario("d")], [_profile("HIGH")], [], [])

    diagnostic = summary_diagnostic(summary)

    assert summary.research_readiness_flag == "READY_FOR_DEEP_RESEARCH"
    assert summary.regime_sensitivity_profile == "REGIME_SENSITIVE"
    assert diagnostic == "D1 price outcomes require regime-normalized interpretation"
    assert "ranking" not in diagnostic.lower()


def _scenario(scenario_id):
    return D1RegimeScenarioData(
        inventory=D1RegimeScenarioInventoryRow(
            scenario_id=scenario_id,
            timeframe="D1",
            status="COMPLETED",
            regime_id=f"REGIME_{scenario_id}",
            regime_label=f"regime_{scenario_id}",
            ohlc_rows=100,
            structures_detected=10,
            states_generated=20,
            unique_states=4,
            most_common_state="DIRECTIONAL_DISPLACEMENT",
            average_forward_range_pips=30,
            direction_alignment_rate=0.5,
            low_sample_conditions_research=0,
            low_sample_conditions_price_outcome=0,
        ),
        scenario_dir=".",
    )


def _profile(flag):
    return D1RegimeConditionProfile(
        condition_type="STATE_CONDITION",
        condition_label="A",
        forward_window=6,
        regime_count=4,
        regimes_present="A;B;C;D",
        scenario_count=4,
        total_sample_size=20,
        average_sample_size_per_regime=5,
        average_forward_close_return_pips=1,
        median_forward_close_return_pips_avg=1,
        average_forward_range_pips=30,
        average_outcome_magnitude_pips=10,
        average_direction_alignment_rate=0.5,
        forward_close_return_cv=0.1,
        forward_range_cv=0.4,
        outcome_magnitude_cv=0.4,
        direction_alignment_cv=0.1,
        min_forward_range_pips=20,
        max_forward_range_pips=40,
        range_dispersion_pips=20,
        min_outcome_magnitude_pips=5,
        max_outcome_magnitude_pips=15,
        outcome_magnitude_dispersion_pips=10,
        sample_adequacy_flag="ADEQUATE",
        regime_coverage_flag="SUFFICIENT",
        regime_sensitivity_flag=flag,
        condition_profile_diagnostic="Condition outcome profile shows elevated regime sensitivity",
        recommended_follow_up="Review D1 regime-normalized outcome dispersion.",
    )
