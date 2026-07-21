"""Run current SQRE research stages for one H4 partial sample."""

from __future__ import annotations

from pathlib import Path

from sqre.event_engine.event_pipeline import EventPipeline
from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.loader import count_data_rows
from sqre.h4_targeted_partial_expansion_validation.models import PartialCandidate, PartialValidationRunSummary
from sqre.market_states import MarketStatesPipeline
from sqre.market_structure import MarketStructureConfig, MarketStructurePipeline
from sqre.price_outcome_research import PriceOutcomeResearchConfig, run_price_outcome_research
from sqre.research_engine import ResearchEngineConfig, run_research_engine
from sqre.transition_engine import TransitionEngineConfig, run_transition_engine


def run_partial_sample(
    candidate: PartialCandidate,
    config: H4TargetedPartialExpansionValidationConfig,
) -> PartialValidationRunSummary:
    if not config.allow_partial_validation:
        return _skipped(candidate, "Partial validation disabled by configuration.")
    if candidate.raw_file_status != "FOUND" or not candidate.raw_file_path:
        return _skipped(candidate, "Candidate raw file is not available.")

    raw_path = Path(candidate.raw_file_path)
    processed_dir = config.output_dir / candidate.candidate_id / "processed"
    stage_report_dir = config.output_dir / candidate.candidate_id / "reports"
    research_dir = config.research_output_dir / candidate.candidate_id / "research"
    processed_dir.mkdir(parents=True, exist_ok=True)
    stage_report_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)

    statuses = {
        "event_detection_status": "NOT_RUN",
        "market_structure_status": "NOT_RUN",
        "market_states_status": "NOT_RUN",
        "transition_engine_status": "NOT_RUN",
        "research_engine_status": "NOT_RUN",
        "price_outcome_status": "NOT_RUN",
    }
    counts = {
        "ohlc_rows": count_data_rows(raw_path),
        "event_count": 0,
        "structure_count": 0,
        "state_count": 0,
        "transition_count": 0,
        "condition_profile_count": 0,
    }

    try:
        event_result = EventPipeline().run(
            input_path=raw_path,
            output_events=processed_dir / "events.csv",
            output_report=stage_report_dir / "event_report.txt",
            symbol=candidate.symbol,
            timeframe=candidate.timeframe,
        )
        statuses["event_detection_status"] = "COMPLETED" if event_result.success else "FAILED"
        counts["event_count"] = event_result.events
        if not event_result.success:
            return _failed(candidate, statuses, counts, event_result.message)

        structure_result = MarketStructurePipeline(
            config=MarketStructureConfig(
                pip_size=config.pip_size,
                max_structure_duration_seconds=config.max_structure_duration_seconds,
            )
        ).run(
            events_path=event_result.events_path,
            output_dir=processed_dir,
            report_path=stage_report_dir / "market_structure_report.txt",
        )
        statuses["market_structure_status"] = "COMPLETED" if structure_result.success else "FAILED"
        counts["structure_count"] = structure_result.structures_detected
        if not structure_result.success:
            return _failed(candidate, statuses, counts, structure_result.message)

        state_result = MarketStatesPipeline().run(
            structures_path=structure_result.structures_path,
            output_path=processed_dir / "market_states.csv",
            report_path=stage_report_dir / "market_states_report.txt",
        )
        statuses["market_states_status"] = "COMPLETED" if state_result.success else "FAILED"
        counts["state_count"] = state_result.states_generated
        if not state_result.success:
            return _failed(candidate, statuses, counts, state_result.message)

        transition_result = run_transition_engine(
            states_path=state_result.output_path,
            output_dir=processed_dir,
            report_path=stage_report_dir / "transition_engine_report.txt",
            config=TransitionEngineConfig(),
        )
        statuses["transition_engine_status"] = "COMPLETED"
        counts["transition_count"] = transition_result.transitions_generated

        research_result = run_research_engine(
            states_path=state_result.output_path,
            transitions_path=transition_result.state_transitions_path,
            output_dir=research_dir,
            report_path=research_dir / "research_engine_report.txt",
            config=ResearchEngineConfig(minimum_sample_size=config.minimum_sample_size),
        )
        statuses["research_engine_status"] = "COMPLETED"

        price_result = run_price_outcome_research(
            states_path=state_result.output_path,
            transitions_path=transition_result.state_transitions_path,
            ohlc_path=raw_path,
            output_dir=research_dir,
            report_path=research_dir / "price_outcome_research_report.txt",
            config=PriceOutcomeResearchConfig(
                forward_candles=config.forward_candles,
                minimum_sample_size=config.minimum_sample_size,
                pip_size=config.pip_size,
            ),
        )
        statuses["price_outcome_status"] = "COMPLETED"
        counts["condition_profile_count"] = max(
            int(getattr(price_result, "summary_rows", 0)),
            int(getattr(research_result, "condition_summary_rows", 0)),
        )
    except Exception as exc:
        return _failed(candidate, statuses, counts, f"Stage failed: {exc}")

    return PartialValidationRunSummary(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        run_status="COMPLETED",
        run_diagnostic="Partial H4 sample completed isolated validation.",
        **statuses,
        **counts,
    )


def _skipped(candidate: PartialCandidate, diagnostic: str) -> PartialValidationRunSummary:
    return PartialValidationRunSummary(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        run_status="SKIPPED",
        event_detection_status="SKIPPED",
        market_structure_status="SKIPPED",
        market_states_status="SKIPPED",
        transition_engine_status="SKIPPED",
        research_engine_status="SKIPPED",
        price_outcome_status="SKIPPED",
        ohlc_rows=0,
        event_count=0,
        structure_count=0,
        state_count=0,
        transition_count=0,
        condition_profile_count=0,
        run_diagnostic=diagnostic,
    )


def _failed(
    candidate: PartialCandidate,
    statuses: dict[str, str],
    counts: dict[str, int],
    diagnostic: str,
) -> PartialValidationRunSummary:
    return PartialValidationRunSummary(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        run_status="FAILED",
        run_diagnostic=diagnostic,
        **statuses,
        **counts,
    )
