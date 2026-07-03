# SQRE Data Acquisition

SQRE uses a provider-agnostic Market Data Manager. Downstream modules consume the
same standardized CSV format regardless of provider:

```text
Date,Open,High,Low,Close,Volume
```

## Manual HistData ingestion

Download a HistData ZIP/CSV manually, place the extracted CSV under
`data/external`, then run:

```bash
python3 scripts/ingest_histdata_file.py \
  --file data/external/DAT_ASCII_EURUSD_M1_2020.csv \
  --symbol EURUSD \
  --timeframe M1 \
  --output data/raw/EURUSD_M1.csv
```

Use `--overwrite` to replace an existing output file.

## Automatic download attempt

```bash
python3 scripts/download_market_data.py \
  --provider histdata \
  --symbol EURUSD \
  --timeframe M5 \
  --start 2020-01-01 \
  --end 2020-12-31
```

HistData automatic download intentionally fails gracefully in SQRE v1.0 and
prints the manual ingestion command. Dukascopy is kept as an optional
experimental provider and is disabled by default.

## Tests

```bash
pytest
```
