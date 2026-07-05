"""Traceability outputs for Market Structure."""

from __future__ import annotations

from sqre.market_structure.models import MarketStructure, StructureEventLink, StructuralUnit


class TraceabilityBuilder:
    """Build event links and structural units."""

    def build_event_links(self, structures: list[MarketStructure]) -> list[StructureEventLink]:
        links: list[StructureEventLink] = []

        for structure in structures:
            structural_event_ids = {point.event_id for point in structure.points}
            for index, event in enumerate(structure.events, start=1):
                role = "STRUCTURAL_POINT" if event.event_id in structural_event_ids else "CONTEXT"
                links.append(
                    StructureEventLink(
                        structure_id=structure.structure_id,
                        event_id=event.event_id,
                        event_time=event.date,
                        event_type=event.event_type,
                        event_price=event.price,
                        event_index=index,
                        role_in_structure=role,
                    )
                )

        return links

    def build_units(self, structures: list[MarketStructure]) -> list[StructuralUnit]:
        units: list[StructuralUnit] = []

        for structure in structures:
            units.append(
                StructuralUnit(
                    unit_id=f"{structure.structure_id}_UNIT",
                    structure_id=structure.structure_id,
                    unit_type="STRUCTURE",
                    start_time=structure.start_time,
                    end_time=structure.end_time,
                    duration_seconds=(structure.end_time - structure.start_time).total_seconds(),
                    start_price=structure.start_price,
                    end_price=structure.end_price,
                    price_displacement=structure.end_price - structure.start_price,
                    direction=structure.direction,
                    event_count=len(structure.events),
                    confidence=structure.metrics.structural_confidence if structure.metrics else 0.0,
                )
            )

            for leg in structure.legs:
                units.append(
                    StructuralUnit(
                        unit_id=leg.leg_id,
                        structure_id=structure.structure_id,
                        unit_type="LEG",
                        start_time=leg.start_time,
                        end_time=leg.end_time,
                        duration_seconds=leg.duration_seconds,
                        start_price=leg.start_price,
                        end_price=leg.end_price,
                        price_displacement=leg.end_price - leg.start_price,
                        direction=leg.direction,
                        event_count=leg.event_count,
                        confidence=leg.confidence,
                    )
                )

        return units
