"""SQRE Phase 4 Market Structure pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from sqre.market_structure.config import MarketStructureConfig
from sqre.market_structure.legs import LegBuilder
from sqre.market_structure.loader import MarketStructureLoader
from sqre.market_structure.models import Leg, MarketStructure, StructureEventLink, StructuralUnit
from sqre.market_structure.reports import MarketStructureReport
from sqre.market_structure.structural_points import StructuralPointBuilder
from sqre.market_structure.structures import StructureBuilder
from sqre.market_structure.traceability import TraceabilityBuilder


@dataclass(frozen=True)
class MarketStructureResult:
    events_processed: int
    structural_points: int
    legs_created: int
    structures_detected: int
    structures_path: Path
    structure_events_path: Path
    structural_units_path: Path
    structural_fingerprints_path: Path
    report_path: Path
    success: bool
    message: str


class MarketStructurePipeline:
    """Build structural datasets from detected events."""

    def __init__(
        self,
        *,
        config: MarketStructureConfig | None = None,
        loader: MarketStructureLoader | None = None,
    ) -> None:
        self.config = config or MarketStructureConfig()
        self.loader = loader or MarketStructureLoader()
        self.point_builder = StructuralPointBuilder()
        self.leg_builder = LegBuilder(self.config)
        self.structure_builder = StructureBuilder(self.config)
        self.traceability_builder = TraceabilityBuilder()
        self.reporter = MarketStructureReport()

    def run(self, *, events_path: Path | str, output_dir: Path | str, report_path: Path | str) -> MarketStructureResult:
        events_path = Path(events_path)
        output_dir = Path(output_dir)
        report_path = Path(report_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = self._paths(output_dir, report_path)
        events = self.loader.load(events_path)
        points = self.point_builder.compress(self.point_builder.build(events))
        legs = self.leg_builder.build(points, events)
        structures = self.structure_builder.build(legs, points, events)

        structure_links = self.traceability_builder.build_event_links(structures)
        structural_units = self.traceability_builder.build_units(structures)

        structures_frame = self._structures_frame(structures)
        structure_events_frame = self._structure_events_frame(structure_links)
        structural_units_frame = self._structural_units_frame(structural_units)
        fingerprints_frame = self._fingerprints_frame(structures)

        structures_frame.to_csv(paths["structures"], index=False)
        structure_events_frame.to_csv(paths["structure_events"], index=False)
        structural_units_frame.to_csv(paths["structural_units"], index=False)
        fingerprints_frame.to_csv(paths["structural_fingerprints"], index=False)
        self.reporter.write(structures_frame, paths["report"])

        return MarketStructureResult(
            events_processed=len(events),
            structural_points=len(points),
            legs_created=len(legs),
            structures_detected=len(structures),
            structures_path=paths["structures"],
            structure_events_path=paths["structure_events"],
            structural_units_path=paths["structural_units"],
            structural_fingerprints_path=paths["structural_fingerprints"],
            report_path=paths["report"],
            success=True,
            message="Market structure completed",
        )

    def _paths(self, output_dir: Path, report_path: Path) -> dict[str, Path]:
        return {
            "structures": output_dir / "structures.csv",
            "structure_events": output_dir / "structure_events.csv",
            "structural_units": output_dir / "structural_units.csv",
            "structural_fingerprints": output_dir / "structural_fingerprints.csv",
            "report": report_path,
        }

    def _structures_frame(self, structures: list[MarketStructure]) -> pd.DataFrame:
        columns = [
            "Structure_ID",
            "Symbol",
            "Timeframe",
            "Start_Time",
            "End_Time",
            "Duration_Seconds",
            "Start_Price",
            "End_Price",
            "Price_Displacement",
            "Direction",
            "Lifecycle_Stage",
            "Event_Count",
            "Point_Count",
            "Pivot_Count",
            "Swing_Count",
            "Large_Candle_Count",
            "Small_Candle_Count",
            "Range_Expansion_Count",
            "Range_Contraction_Count",
            "Leg_Count",
            "Impulse_Count",
            "Correction_Count",
            "Range_Count",
            "Persistence_Index",
            "Structural_Complexity",
            "Structural_Stability",
            "Structural_Efficiency",
            "Event_Density",
            "Structural_Volatility",
            "Structural_Symmetry",
            "Structural_Confidence",
        ]
        rows: list[dict[str, object]] = []
        for structure in structures:
            metrics = structure.metrics
            if metrics is None:
                continue
            rows.append(
                {
                    "Structure_ID": structure.structure_id,
                    "Symbol": structure.symbol,
                    "Timeframe": structure.timeframe,
                    "Start_Time": structure.start_time,
                    "End_Time": structure.end_time,
                    "Duration_Seconds": (structure.end_time - structure.start_time).total_seconds(),
                    "Start_Price": structure.start_price,
                    "End_Price": structure.end_price,
                    "Price_Displacement": structure.end_price - structure.start_price,
                    "Direction": structure.direction,
                    "Lifecycle_Stage": structure.lifecycle_stage,
                    "Event_Count": metrics.event_count,
                    "Point_Count": len(structure.points),
                    "Pivot_Count": metrics.pivot_count,
                    "Swing_Count": metrics.swing_count,
                    "Large_Candle_Count": metrics.large_candle_count,
                    "Small_Candle_Count": metrics.small_candle_count,
                    "Range_Expansion_Count": metrics.range_expansion_count,
                    "Range_Contraction_Count": metrics.range_contraction_count,
                    "Leg_Count": metrics.leg_count,
                    "Impulse_Count": 0,
                    "Correction_Count": 0,
                    "Range_Count": 0,
                    "Persistence_Index": metrics.persistence_index,
                    "Structural_Complexity": metrics.structural_complexity,
                    "Structural_Stability": metrics.structural_stability,
                    "Structural_Efficiency": metrics.structural_efficiency,
                    "Event_Density": metrics.event_density,
                    "Structural_Volatility": metrics.structural_volatility,
                    "Structural_Symmetry": metrics.structural_symmetry,
                    "Structural_Confidence": metrics.structural_confidence,
                }
            )
        return pd.DataFrame(rows, columns=columns)

    def _structure_events_frame(self, links: list[StructureEventLink]) -> pd.DataFrame:
        columns = [
            "Structure_ID",
            "Event_ID",
            "Event_Time",
            "Event_Type",
            "Event_Price",
            "Event_Index",
            "Role_In_Structure",
        ]
        return pd.DataFrame(
            [
                {
                    "Structure_ID": link.structure_id,
                    "Event_ID": link.event_id,
                    "Event_Time": link.event_time,
                    "Event_Type": link.event_type,
                    "Event_Price": link.event_price,
                    "Event_Index": link.event_index,
                    "Role_In_Structure": link.role_in_structure,
                }
                for link in links
            ],
            columns=columns,
        )

    def _structural_units_frame(self, units: list[StructuralUnit]) -> pd.DataFrame:
        columns = [
            "Unit_ID",
            "Structure_ID",
            "Unit_Type",
            "Start_Time",
            "End_Time",
            "Duration_Seconds",
            "Start_Price",
            "End_Price",
            "Price_Displacement",
            "Direction",
            "Event_Count",
            "Confidence",
        ]
        return pd.DataFrame(
            [
                {
                    "Unit_ID": unit.unit_id,
                    "Structure_ID": unit.structure_id,
                    "Unit_Type": unit.unit_type,
                    "Start_Time": unit.start_time,
                    "End_Time": unit.end_time,
                    "Duration_Seconds": unit.duration_seconds,
                    "Start_Price": unit.start_price,
                    "End_Price": unit.end_price,
                    "Price_Displacement": unit.price_displacement,
                    "Direction": unit.direction,
                    "Event_Count": unit.event_count,
                    "Confidence": unit.confidence,
                }
                for unit in units
            ],
            columns=columns,
        )

    def _fingerprints_frame(self, structures: list[MarketStructure]) -> pd.DataFrame:
        columns = [
            "Structure_ID",
            "Persistence",
            "Complexity",
            "Stability",
            "Efficiency",
            "Density",
            "Volatility",
            "Symmetry",
            "Confidence",
        ]
        rows: list[dict[str, object]] = []
        for structure in structures:
            if structure.fingerprint is None:
                continue
            raw = asdict(structure.fingerprint)
            rows.append(
                {
                    "Structure_ID": raw["structure_id"],
                    "Persistence": raw["persistence"],
                    "Complexity": raw["complexity"],
                    "Stability": raw["stability"],
                    "Efficiency": raw["efficiency"],
                    "Density": raw["density"],
                    "Volatility": raw["volatility"],
                    "Symmetry": raw["symmetry"],
                    "Confidence": raw["confidence"],
                }
            )
        return pd.DataFrame(rows, columns=columns)
