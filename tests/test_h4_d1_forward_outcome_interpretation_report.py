import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.h4_d1_forward_outcome_interpretation_pipeline import (
    H4D1ForwardOutcomeInterpretationReviewPipeline,
)
from sqre.h4_d1_forward_outcome_interpretation_review.reports import FORBIDDEN_REPORT_TERMS
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_contextual_inputs, write_phase_7515_inputs


def test_report_includes_sections_and_excludes_forbidden_operational_language(tmp_path):
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

    H4D1ForwardOutcomeInterpretationReviewPipeline(config).run()
    text = config.report_path.read_text()
    lowered = text.lower()

    assert "Outcome Profile Interpretability Review" in text
    assert "This phase does not generate trading signals." in text
    assert "This phase does not produce operational recommendations." in text
    assert not [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    assert len(pd.read_csv(output_dir / "h4_d1_forward_outcome_interpretation_review_summary.csv")) == 1
