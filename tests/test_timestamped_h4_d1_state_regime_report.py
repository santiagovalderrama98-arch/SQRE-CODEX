from pathlib import Path

from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.reports import build_report_text
from sqre.timestamped_h4_d1_state_regime_generation.timestamped_h4_d1_state_regime_pipeline import (
    run_timestamped_h4_d1_state_regime_generation,
)
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_report_includes_required_scope_language(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync")
    result = run_timestamped_h4_d1_state_regime_generation(
        TimestampedH4D1StateRegimeGenerationConfig(
            synchronized_data_dir=input_dir,
            output_dir=tmp_path / "out",
            report_path=tmp_path / "out" / "report.txt",
        )
    )

    text = build_report_text(result)

    assert "SQRE Timestamped H4/D1 State & Regime Table Generation" in text
    assert "This phase generates timestamped H4/D1 state/regime tables only." in text
    assert "This phase does not perform H4/D1 same-time alignment." in text
    assert "This phase does not perform H4/D1 contextual interpretation." in text
    assert "This phase does not generate trading signals." in text
    assert "Generated timestamps are future alignment keys only." in text
    assert "Same-time H4/D1 review must occur in a later phase." in text


def test_report_avoids_forbidden_operational_language(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync")
    result = run_timestamped_h4_d1_state_regime_generation(
        TimestampedH4D1StateRegimeGenerationConfig(
            synchronized_data_dir=input_dir,
            output_dir=tmp_path / "out",
            report_path=tmp_path / "out" / "report.txt",
        )
    )
    text = result.report_path.read_text(encoding="utf-8").lower()

    for forbidden in [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "trade setup",
        "take profit",
        "stop loss",
        "profitable",
        "opportunity",
        "predicts",
        "optimal",
        "should trade",
    ]:
        assert forbidden not in text
