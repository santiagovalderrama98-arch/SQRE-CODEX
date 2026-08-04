"""Configuration for Research Query Interface Design."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ResearchQueryInterfaceDesignConfig:
    reference_store_dir: Path = Path("data/research/research_reference_store_design")
    usage_review_dir: Path = Path("data/research/research_reference_store_usage_review")
    interpretation_dir: Path = Path("data/research/h4_d1_forward_outcome_interpretation_review")
    same_time_alignment_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    output_dir: Path = Path("data/research/research_query_interface_design")
    report_path: Path = Path("data/research/research_query_interface_design/research_query_interface_design_report.txt")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    preferred_horizons: list[int] = field(default_factory=lambda: [1, 2, 3, 6, 12])
    maximum_query_scenarios: int = 500
    maximum_results_per_query: int = 5
    minimum_reference_sample_size: int = 10
    minimum_core_reference_sample_size: int = 20
    maximum_reference_dispersion_pips: float = 80.0
    query_h4_transition_label: str | None = None
    query_d1_market_state: str | None = None
    query_d1_regime_label: str | None = None
    query_d1_structure_direction: str | None = None
    query_forward_horizon: int | None = None

    @property
    def has_single_query(self) -> bool:
        return any(
            item is not None
            for item in [
                self.query_h4_transition_label,
                self.query_d1_market_state,
                self.query_d1_regime_label,
                self.query_d1_structure_direction,
                self.query_forward_horizon,
            ]
        )
