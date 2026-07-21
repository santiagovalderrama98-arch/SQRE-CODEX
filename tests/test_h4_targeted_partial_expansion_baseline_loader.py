from pathlib import Path

from sqre.h4_targeted_partial_expansion_validation.baseline_loader import load_baseline_metrics

from test_h4_targeted_partial_expansion_helpers import write_baseline_inputs


def test_baseline_loader_reads_h4_synthetic_summaries(tmp_path: Path):
    validation_dir, research_dir = write_baseline_inputs(tmp_path)

    metrics = load_baseline_metrics(validation_dir, research_dir)

    assert metrics.scenario_count == 2
    assert metrics.average_ohlc_rows == 950
    assert metrics.average_structure_count == 45
    assert metrics.average_forward_range_pips == 11


def test_baseline_loader_handles_missing_optional_files(tmp_path: Path):
    metrics = load_baseline_metrics(tmp_path / "missing_validation", tmp_path / "missing_research")

    assert metrics.scenario_count == 0
    assert metrics.average_outcome_magnitude_pips == 0
