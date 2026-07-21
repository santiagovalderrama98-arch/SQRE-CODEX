from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.models import PartialCandidate
from sqre.h4_targeted_partial_expansion_validation.partial_sample_runner import run_partial_sample

from test_h4_targeted_partial_expansion_helpers import write_raw_ohlc


def candidate(raw_file: Path, status: str = "FOUND") -> PartialCandidate:
    return PartialCandidate(
        candidate_id="eurusd_h4_period_5_partial",
        symbol="EURUSD",
        timeframe="H4",
        sample_label="PARTIAL_SAMPLE",
        feasibility_class="FEASIBLE_PARTIAL_SAMPLE",
        coverage_ratio=0.62,
        raw_file_path=str(raw_file),
        raw_file_status=status,
    )


def test_runner_handles_missing_raw_without_fabricating_counts(tmp_path: Path):
    run = run_partial_sample(candidate(tmp_path / "missing.csv", "MISSING"), H4TargetedPartialExpansionValidationConfig())

    assert run.run_status == "SKIPPED"
    assert run.ohlc_rows == 0
    assert run.structure_count == 0


def test_runner_can_complete_with_mocked_stages(tmp_path: Path, monkeypatch):
    raw_file = write_raw_ohlc(tmp_path / "raw.csv", rows=12)
    config = H4TargetedPartialExpansionValidationConfig(output_dir=tmp_path / "validation", research_output_dir=tmp_path / "research")

    class FakeEventPipeline:
        def run(self, *, output_events, output_report, **kwargs):
            Path(output_events).parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame([{"Date": "2024-01-01", "EventType": "PIVOT_HIGH"}]).to_csv(output_events, index=False)
            Path(output_report).parent.mkdir(parents=True, exist_ok=True)
            Path(output_report).write_text("report")
            return SimpleNamespace(success=True, events=1, events_path=Path(output_events), message="ok")

    class FakeStructurePipeline:
        def __init__(self, config=None):
            pass

        def run(self, *, output_dir, report_path, **kwargs):
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            structures_path = Path(output_dir) / "structures.csv"
            pd.DataFrame([{"Structure_ID": "S1"}]).to_csv(structures_path, index=False)
            return SimpleNamespace(success=True, structures_detected=1, structures_path=structures_path, message="ok")

    class FakeStatesPipeline:
        def run(self, *, output_path, report_path, **kwargs):
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame([{"State_ID": "STATE_1", "Market_State": "DIRECTIONAL_DISPLACEMENT"}]).to_csv(output_path, index=False)
            return SimpleNamespace(success=True, states_generated=1, output_path=Path(output_path), message="ok")

    def fake_transition_engine(*, output_dir, report_path, **kwargs):
        path = Path(output_dir) / "state_transitions.csv"
        pd.DataFrame([{"Transition_Label": "A -> B"}]).to_csv(path, index=False)
        return SimpleNamespace(transitions_generated=1, state_transitions_path=path)

    def fake_research_engine(*, output_dir, **kwargs):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return SimpleNamespace(condition_summary_rows=3)

    def fake_price_outcome(*, output_dir, **kwargs):
        pd.DataFrame([{"Condition_ID": "C1"}] * 4).to_csv(Path(output_dir) / "condition_price_outcome_summary.csv", index=False)
        return SimpleNamespace(summary_rows=4)

    monkeypatch.setattr("sqre.h4_targeted_partial_expansion_validation.partial_sample_runner.EventPipeline", FakeEventPipeline)
    monkeypatch.setattr("sqre.h4_targeted_partial_expansion_validation.partial_sample_runner.MarketStructurePipeline", FakeStructurePipeline)
    monkeypatch.setattr("sqre.h4_targeted_partial_expansion_validation.partial_sample_runner.MarketStatesPipeline", FakeStatesPipeline)
    monkeypatch.setattr("sqre.h4_targeted_partial_expansion_validation.partial_sample_runner.run_transition_engine", fake_transition_engine)
    monkeypatch.setattr("sqre.h4_targeted_partial_expansion_validation.partial_sample_runner.run_research_engine", fake_research_engine)
    monkeypatch.setattr("sqre.h4_targeted_partial_expansion_validation.partial_sample_runner.run_price_outcome_research", fake_price_outcome)

    run = run_partial_sample(candidate(raw_file), config)

    assert run.run_status == "COMPLETED"
    assert run.ohlc_rows == 12
    assert run.condition_profile_count == 4
