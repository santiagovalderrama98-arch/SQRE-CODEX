from __future__ import annotations

import json
from datetime import date

from sqre.data_acquisition.metadata import MetadataWriter


def test_metadata_writer_creates_sidecar_json(tmp_path) -> None:
    output_path = tmp_path / "EURUSD_M1.csv"
    output_path.write_text("Date,Open,High,Low,Close,Volume\n", encoding="utf-8")

    metadata_path = MetadataWriter().write(
        output_path=output_path,
        provider="histdata",
        symbol="eurusd",
        timeframe="m1",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 1, 2),
        rows=10,
        source="manual.csv",
        validation_summary={"valid": True, "errors": [], "rows": 10},
    )

    payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert metadata_path.name == "EURUSD_M1.metadata.json"
    assert payload["provider"] == "histdata"
    assert payload["symbol"] == "EURUSD"
    assert payload["validation_summary"]["valid"] is True
