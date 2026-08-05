from pathlib import Path

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.research_dashboard_prototype_pipeline import ResearchDashboardPrototypePipeline

from test_research_dashboard_prototype_loader import write_minimal_snapshot_inputs


EXPECTED_OUTPUTS = [
    "research_dashboard_source_inventory.csv",
    "research_dashboard_snapshot_panel.csv",
    "research_dashboard_reference_cards.csv",
    "research_dashboard_evidence_panel.csv",
    "research_dashboard_behavior_panel.csv",
    "research_dashboard_fallback_panel.csv",
    "research_dashboard_diagnostic_panel.csv",
    "research_dashboard_summary.csv",
]


def test_pipeline_writes_all_expected_outputs(tmp_path):
    snapshot_dir = tmp_path / "snapshot"
    out = tmp_path / "out"
    write_minimal_snapshot_inputs(snapshot_dir)
    config = ResearchDashboardPrototypeConfig(
        snapshot_research_dir=snapshot_dir,
        query_interface_dir=tmp_path / "query",
        reference_store_dir=tmp_path / "reference",
        output_dir=out,
        report_path=out / "research_dashboard_prototype_report.txt",
        html_path=out / "research_dashboard_prototype.html",
    )

    result = ResearchDashboardPrototypePipeline(config).run()

    assert result.summary is not None
    assert result.summary.dashboard_readiness_flag == "READY_FOR_MANUAL_RESEARCH_REVIEW"
    for filename in EXPECTED_OUTPUTS:
        assert (out / filename).exists()
    assert config.report_path.exists()
    assert config.html_path.exists()
    summary = pd.read_csv(out / "research_dashboard_summary.csv")
    assert summary.iloc[0]["Reference_Card_Count"] == 1


def assert_dashboard_outputs_exist(out: Path) -> None:
    for filename in EXPECTED_OUTPUTS:
        assert (out / filename).exists()
