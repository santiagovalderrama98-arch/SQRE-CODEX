from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.loader import H4D1ForwardOutcomeInterpretationLoader
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_contextual_inputs, write_phase_7515_inputs


def test_loader_handles_missing_inputs_safely(tmp_path):
    config = H4D1ForwardOutcomeInterpretationReviewConfig(
        forward_outcome_dir=tmp_path / "missing_forward",
        contextual_transition_dir=tmp_path / "missing_context",
    )
    loader = H4D1ForwardOutcomeInterpretationLoader(config)

    assert loader.load_outcome_profiles().empty
    assert loader.load_contextual_profiles().empty


def test_loader_loads_forward_profiles_and_supporting_reviews(tmp_path):
    forward_dir = tmp_path / "forward"
    context_dir = tmp_path / "context"
    write_phase_7515_inputs(forward_dir)
    write_contextual_inputs(context_dir)
    config = H4D1ForwardOutcomeInterpretationReviewConfig(
        forward_outcome_dir=forward_dir,
        contextual_transition_dir=context_dir,
    )
    loader = H4D1ForwardOutcomeInterpretationLoader(config)

    assert len(loader.load_outcome_profiles()) == 7
    assert len(loader.load_dispersion_review()) == 7
    assert len(loader.load_sample_adequacy_review()) == 7
    assert len(loader.load_contextual_profiles()) == 1
