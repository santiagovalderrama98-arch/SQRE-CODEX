from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.h4_d1_forward_outcome_interpretation_pipeline import (
    H4D1ForwardOutcomeInterpretationReviewPipeline,
)
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_contextual_inputs, write_phase_7515_inputs


def test_pipeline_writes_all_expected_outputs(tmp_path):
    forward_dir = tmp_path / "forward"
    context_dir = tmp_path / "context"
    output_dir = tmp_path / "out"
    write_phase_7515_inputs(forward_dir)
    write_contextual_inputs(context_dir)
    config = H4D1ForwardOutcomeInterpretationReviewConfig(
        forward_outcome_dir=forward_dir,
        contextual_transition_dir=context_dir,
        output_dir=output_dir,
        report_path=output_dir / "report.txt",
    )

    result = H4D1ForwardOutcomeInterpretationReviewPipeline(config).run()

    assert result.summary is not None
    for filename in [
        "h4_d1_forward_outcome_interpretation_source_inventory.csv",
        "h4_d1_outcome_profile_interpretability_review.csv",
        "h4_d1_directional_behavior_review.csv",
        "h4_d1_excursion_behavior_review.csv",
        "h4_d1_horizon_stability_review.csv",
        "h4_d1_context_granularity_utility_review.csv",
        "h4_d1_forward_outcome_interpretation_review_summary.csv",
    ]:
        assert (output_dir / filename).exists()
    assert config.report_path.exists()
