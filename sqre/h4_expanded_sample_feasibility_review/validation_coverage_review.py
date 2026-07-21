"""Validation and research evidence review for H4 samples."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.loader import integer_value, text_value
from sqre.h4_expanded_sample_feasibility_review.models import AvailabilityReviewRow, ValidationCoverageRow


def build_validation_coverage_review(
    availability_rows: list[AvailabilityReviewRow],
    evidence_frames: list[pd.DataFrame],
    h4_d1_research_dir: Path | str,
) -> list[ValidationCoverageRow]:
    evidence = _evidence_by_scenario(evidence_frames)
    inventory_path = Path(h4_d1_research_dir) / "h4_d1_scenario_inventory.csv"
    if inventory_path.exists():
        try:
            evidence.update(_evidence_by_scenario([pd.read_csv(inventory_path)]))
        except Exception:
            pass

    rows: list[ValidationCoverageRow] = []
    for item in availability_rows:
        record = evidence.get(item.scenario_id, {})
        validated = bool(record)
        validation_status = "VALIDATED" if validated else (
            "NOT_VALIDATED" if item.availability_status in {"AVAILABLE_FULL", "AVAILABLE_PARTIAL"} else "UNKNOWN_VALIDATION_STATUS"
        )
        rows.append(
            ValidationCoverageRow(
                scenario_id=item.scenario_id,
                symbol=item.symbol,
                timeframe="H4",
                validation_status=validation_status,
                ohlc_rows=int(record.get("ohlc_rows", 0)),
                structure_count=int(record.get("structure_count", 0)),
                state_count=int(record.get("state_count", 0)),
                transition_count=int(record.get("transition_count", 0)),
                research_output_status="PRESENT" if validated else "MISSING",
                validation_coverage_diagnostic=_diagnostic(validation_status),
            )
        )
    return rows


def _evidence_by_scenario(frames: list[pd.DataFrame]) -> dict[str, dict[str, int]]:
    evidence: dict[str, dict[str, int]] = {}
    for frame in frames:
        if frame.empty:
            continue
        for _, row in frame.iterrows():
            if text_value(row, "Timeframe", "timeframe", default="H4").upper() != "H4":
                continue
            scenario_id = text_value(row, "Scenario_ID", "scenario_id", "Scenario", "Sample_ID", "Name")
            if not scenario_id:
                continue
            evidence[scenario_id] = {
                "ohlc_rows": integer_value(row, "OHLC_Rows", "Row_Count", "Rows"),
                "structure_count": integer_value(row, "Structure_Count", "Structures"),
                "state_count": integer_value(row, "State_Count", "States"),
                "transition_count": integer_value(row, "Transition_Count", "Transitions"),
            }
    return evidence


def _diagnostic(validation_status: str) -> str:
    return {
        "VALIDATED": "H4 sample already has validation/research evidence",
        "NOT_VALIDATED": "H4 sample appears available but lacks validation output evidence",
        "UNKNOWN_VALIDATION_STATUS": "H4 validation status cannot be determined from available diagnostics",
    }.get(validation_status, "H4 validation coverage requires review")
