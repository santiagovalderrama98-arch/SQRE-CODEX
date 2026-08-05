"""Configuration for Current Market State Snapshot Research."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CurrentMarketStateSnapshotResearchConfig:
    reference_store_dir: Path = Path("data/research/research_reference_store_design")
    query_interface_dir: Path = Path("data/research/research_query_interface_design")
    usage_review_dir: Path = Path("data/research/research_reference_store_usage_review")
    same_time_alignment_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    timestamped_state_regime_dir: Path = Path("data/research/h4_d1_timestamped_state_regime_table")
    output_dir: Path = Path("data/research/current_market_state_snapshot_research")
    report_path: Path = Path(
        "data/research/current_market_state_snapshot_research/current_market_state_snapshot_research_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    preferred_horizons: list[int] = field(default_factory=lambda: [1, 2, 3, 6, 12])
    maximum_results_per_snapshot_query: int = 5
    minimum_reference_sample_size: int = 10
    minimum_core_reference_sample_size: int = 20
    maximum_reference_dispersion_pips: float = 80.0
    snapshot_mode: str = "LATEST_AVAILABLE_SNAPSHOT"
    snapshot_timestamp: str | None = None
    snapshot_h4_transition_label: str | None = None
    snapshot_h4_market_state: str | None = None
    snapshot_d1_market_state: str | None = None
    snapshot_d1_regime_label: str | None = None
    snapshot_d1_structure_direction: str | None = None
    snapshot_forward_horizon: int | None = None

    def normalized_snapshot_mode(self) -> str:
        mode = self.snapshot_mode.strip().upper()
        valid = {
            "LATEST_AVAILABLE_SNAPSHOT",
            "USER_SUPPLIED_SNAPSHOT",
            "FALLBACK_REFERENCE_USAGE_SNAPSHOT",
            "INPUT_MISSING",
        }
        return mode if mode in valid else "INPUT_MISSING"
