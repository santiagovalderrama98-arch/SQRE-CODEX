from pathlib import Path

from sqre.h4_targeted_partial_expansion_validation.candidate_selector import load_partial_candidates
from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig

from test_h4_targeted_partial_expansion_helpers import write_feasibility_inputs, write_raw_ohlc


def test_selector_selects_feasible_partial_sample(tmp_path: Path):
    raw_file = write_raw_ohlc(tmp_path / "data" / "raw" / "partial" / "EURUSD_H4_period_5_partial.csv")
    feasibility_dir = write_feasibility_inputs(tmp_path, raw_file=raw_file)
    config = H4TargetedPartialExpansionValidationConfig(
        feasibility_dir=feasibility_dir,
        raw_data_dir=tmp_path / "data" / "raw",
        partial_data_dir=tmp_path / "data" / "raw" / "partial",
    )

    candidates = load_partial_candidates(config)

    assert len(candidates) == 1
    assert candidates[0].candidate_id == "eurusd_h4_period_5_partial"
    assert candidates[0].raw_file_status == "FOUND"


def test_selector_ignores_already_validated_rows(tmp_path: Path):
    feasibility_dir = write_feasibility_inputs(tmp_path)
    config = H4TargetedPartialExpansionValidationConfig(feasibility_dir=feasibility_dir, candidate_id="eurusd_h4_period_6")

    assert load_partial_candidates(config) == []


def test_raw_locator_reports_missing(tmp_path: Path):
    feasibility_dir = write_feasibility_inputs(tmp_path)
    config = H4TargetedPartialExpansionValidationConfig(
        feasibility_dir=feasibility_dir,
        raw_data_dir=tmp_path / "empty_raw",
        partial_data_dir=tmp_path / "empty_partial",
    )

    candidates = load_partial_candidates(config)

    assert candidates[0].raw_file_status == "MISSING"
    assert "no readable" in candidates[0].candidate_diagnostic.lower()
