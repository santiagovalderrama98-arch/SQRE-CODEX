"""Configuration for H4 targeted partial expansion validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class H4TargetedPartialExpansionValidationConfig:
    feasibility_dir: Path = Path("data/research/h4_expanded_sample_feasibility_review")
    baseline_validation_dir: Path = Path("data/validation/h4_d1_structural_research")
    baseline_research_dir: Path = Path("data/research/h4_d1_structural_research")
    output_dir: Path = Path("data/validation/h4_targeted_partial_expansion_validation")
    research_output_dir: Path = Path("data/research/h4_targeted_partial_expansion_validation")
    report_path: Path = Path(
        "data/research/h4_targeted_partial_expansion_validation/"
        "h4_targeted_partial_expansion_validation_report.txt"
    )
    candidate_id: str = "eurusd_h4_period_5_partial"
    raw_data_dir: Path = Path("data/raw")
    partial_data_dir: Path = Path("data/raw/partial")
    pip_size: float = 0.0001
    forward_candles: list[int] = field(default_factory=lambda: [3, 6, 12])
    minimum_sample_size: int = 5
    max_structure_duration_seconds: int = 86400
    partial_sample_label: str = "PARTIAL_SAMPLE"
    allow_partial_validation: bool = True
