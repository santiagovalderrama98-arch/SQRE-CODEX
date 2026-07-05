"""SQRE Phase 5 Market States pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from sqre.market_states.classifier import MarketStateClassifier
from sqre.market_states.confidence import StateConfidenceCalculator
from sqre.market_states.config import MarketStatesConfig
from sqre.market_states.loader import MarketStatesLoader
from sqre.market_states.models import MarketState, StructuralInput
from sqre.market_states.reports import STATE_ORDER, MarketStatesReport


@dataclass(frozen=True)
class MarketStatesResult:
    structures_processed: int
    states_generated: int
    most_common_state: str
    output_path: Path
    report_path: Path
    success: bool
    message: str


class MarketStatesPipeline:
    """Classify Market Structures into descriptive Market States."""

    def __init__(
        self,
        *,
        config: MarketStatesConfig | None = None,
        loader: MarketStatesLoader | None = None,
    ) -> None:
        self.config = config or MarketStatesConfig()
        self.loader = loader or MarketStatesLoader()
        self.classifier = MarketStateClassifier(self.config)
        self.confidence_calculator = StateConfidenceCalculator()
        self.reporter = MarketStatesReport()

    def run(
        self,
        *,
        structures_path: Path | str,
        output_path: Path | str,
        report_path: Path | str,
    ) -> MarketStatesResult:
        output_path = Path(output_path)
        report_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        structures = self.loader.load(structures_path)
        states = [self._build_market_state(index, structure) for index, structure in enumerate(structures, start=1)]

        self._states_frame(states).to_csv(output_path, index=False)
        self.reporter.write(states, report_path)

        return MarketStatesResult(
            structures_processed=len(structures),
            states_generated=len(states),
            most_common_state=self._most_common_state(states),
            output_path=output_path,
            report_path=report_path,
            success=True,
            message="Market states completed",
        )

    def _build_market_state(self, index: int, structure: StructuralInput) -> MarketState:
        classification = self.classifier.classify(structure)
        state_confidence = self.confidence_calculator.calculate(structure, classification)
        return MarketState(
            state_id=f"STATE_{index:06d}",
            structure_id=structure.structure_id,
            symbol=structure.symbol,
            timeframe=structure.timeframe,
            start_time=structure.start_time,
            end_time=structure.end_time,
            direction=structure.direction,
            market_state=classification.market_state,
            state_confidence=state_confidence,
            classification_rule=classification.classification_rule,
            persistence_index=structure.persistence_index,
            structural_complexity=structure.structural_complexity,
            structural_stability=structure.structural_stability,
            structural_efficiency=structure.structural_efficiency,
            event_density=structure.event_density,
            structural_volatility=structure.structural_volatility,
            structural_symmetry=structure.structural_symmetry,
            structural_confidence=structure.structural_confidence,
            lifecycle_stage=structure.lifecycle_stage,
            duration_seconds=structure.duration_seconds,
            price_displacement=structure.price_displacement,
            event_count=structure.event_count,
            leg_count=structure.leg_count,
        )

    def _states_frame(self, states: list[MarketState]) -> pd.DataFrame:
        columns = [
            "State_ID",
            "Structure_ID",
            "Symbol",
            "Timeframe",
            "Start_Time",
            "End_Time",
            "Direction",
            "Market_State",
            "State_Confidence",
            "Classification_Rule",
            "Persistence_Index",
            "Structural_Complexity",
            "Structural_Stability",
            "Structural_Efficiency",
            "Event_Density",
            "Structural_Volatility",
            "Structural_Symmetry",
            "Structural_Confidence",
            "Lifecycle_Stage",
            "Duration_Seconds",
            "Price_Displacement",
            "Event_Count",
            "Leg_Count",
        ]
        rows = [
            {
                "State_ID": state.state_id,
                "Structure_ID": state.structure_id,
                "Symbol": state.symbol,
                "Timeframe": state.timeframe,
                "Start_Time": state.start_time,
                "End_Time": state.end_time,
                "Direction": state.direction,
                "Market_State": state.market_state,
                "State_Confidence": state.state_confidence,
                "Classification_Rule": state.classification_rule,
                "Persistence_Index": state.persistence_index,
                "Structural_Complexity": state.structural_complexity,
                "Structural_Stability": state.structural_stability,
                "Structural_Efficiency": state.structural_efficiency,
                "Event_Density": state.event_density,
                "Structural_Volatility": state.structural_volatility,
                "Structural_Symmetry": state.structural_symmetry,
                "Structural_Confidence": state.structural_confidence,
                "Lifecycle_Stage": state.lifecycle_stage,
                "Duration_Seconds": state.duration_seconds,
                "Price_Displacement": state.price_displacement,
                "Event_Count": state.event_count,
                "Leg_Count": state.leg_count,
            }
            for state in states
        ]
        return pd.DataFrame(rows, columns=columns)

    def _most_common_state(self, states: list[MarketState]) -> str:
        if not states:
            return "UNCLASSIFIED"
        counts: dict[str, int] = {}
        for state in states:
            counts[state.market_state] = counts.get(state.market_state, 0) + 1
        return max(STATE_ORDER, key=lambda state: (counts.get(state, 0), -STATE_ORDER.index(state)))
