from pathlib import Path

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.models import PartialCandidate, PartialValidationRunSummary
from sqre.h4_targeted_partial_expansion_validation.partial_output_loader import (
    load_price_outcome_summary,
    load_structure_state_summary,
    load_transition_summary,
)


def test_output_loader_reads_synthetic_partial_outputs(tmp_path: Path):
    candidate = PartialCandidate("cid", "EURUSD", "H4", "PARTIAL_SAMPLE", "FEASIBLE_PARTIAL_SAMPLE", 0.5)
    config = H4TargetedPartialExpansionValidationConfig(output_dir=tmp_path / "validation", research_output_dir=tmp_path / "research")
    processed = config.output_dir / "cid" / "processed"
    research = config.research_output_dir / "cid" / "research"
    processed.mkdir(parents=True)
    research.mkdir(parents=True)
    pd.DataFrame(
        [{"Duration_Seconds": 100.0, "Price_Displacement": 0.0010}, {"Duration_Seconds": 200.0, "Price_Displacement": -0.0020}]
    ).to_csv(processed / "structures.csv", index=False)
    pd.DataFrame([{"Market_State": "A"}, {"Market_State": "B"}]).to_csv(processed / "market_states.csv", index=False)
    pd.DataFrame(
        [
            {"Transition_Label": "A -> B", "From_Market_State": "DIRECTIONAL_DISPLACEMENT", "To_Market_State": "VOLATILE_ROTATION"},
            {"Transition_Label": "B -> C", "From_Market_State": "VOLATILE_ROTATION", "To_Market_State": "DIRECTIONAL_EXPANSION"},
        ]
    ).to_csv(processed / "state_transitions.csv", index=False)
    pd.DataFrame(
        [
            {"Average_Forward_Range_Pips": 10, "Average_Outcome_Magnitude_Pips": 5, "Direction_Alignment_Rate": 0.5, "Low_Sample_Size": False},
            {"Average_Forward_Range_Pips": 14, "Average_Outcome_Magnitude_Pips": 7, "Direction_Alignment_Rate": 0.7, "Low_Sample_Size": True},
        ]
    ).to_csv(research / "condition_price_outcome_summary.csv", index=False)
    run = PartialValidationRunSummary("cid", "PARTIAL_SAMPLE", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", 20, 5, 2, 2, 2, 2, "ok")

    structure = load_structure_state_summary(candidate, run, config)
    transitions = load_transition_summary(candidate, run, config)
    price = load_price_outcome_summary(candidate, run, config)

    assert structure.structure_count == 2
    assert structure.unique_state_count == 2
    assert transitions.directional_to_rotation_count == 1
    assert transitions.rotation_to_directional_count == 1
    assert price.condition_profile_count == 2
    assert price.sample_constrained_profile_count == 1
