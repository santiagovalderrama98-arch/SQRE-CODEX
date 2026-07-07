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

## Market Structure

After `data/processed/events.csv` exists, run:

```bash
python3 scripts/run_market_structure.py \
  --events data/processed/events.csv \
  --output-dir data/processed \
  --report data/reports/market_structure_report.txt \
  --max-structure-duration-seconds 14400
```

The Market Structure pipeline groups structural highs/lows into descriptive
legs and structures, then writes:

```text
data/processed/structures.csv
data/processed/structure_events.csv
data/processed/structural_units.csv
data/processed/structural_fingerprints.csv
data/reports/market_structure_report.txt
```

This module is descriptive only. It does not implement trading signals, Market
States, Coverage, a Transition Engine, backtesting, optimization, or portfolio
logic.

## Market States

After `data/processed/structures.csv` exists, run:

```bash
python3 scripts/run_market_states.py \
  --structures data/processed/structures.csv \
  --output data/processed/market_states.csv \
  --report data/reports/market_states_report.txt
```

The Market States pipeline classifies each Market Structure into one
descriptive v1.0 state and writes:

```text
data/processed/market_states.csv
data/reports/market_states_report.txt
```

The v1.0 taxonomy is:

```text
DIRECTIONAL_EXPANSION
DIRECTIONAL_DISPLACEMENT
DIRECTIONAL_DRIFT
NEUTRAL_COMPRESSION
COMPLEX_CONSOLIDATION
VOLATILE_ROTATION
LOW_QUALITY_STRUCTURE
UNCLASSIFIED
```

`DIRECTIONAL_DISPLACEMENT` describes efficient directional displacement without
enough persistence to qualify as Directional Expansion.

This module is descriptive only and does not generate trading signals.

## Transition Engine

Phase 6 measures observed transitions between Market States. It does not
generate trading signals or operational recommendations.

Input file:

```text
data/processed/market_states.csv
```

Run:

```bash
python3 scripts/run_transition_engine.py \
  --states data/processed/market_states.csv \
  --output-dir data/processed \
  --report data/reports/transition_engine_report.txt
```

The Transition Engine writes:

```text
data/processed/state_transitions.csv
data/processed/transition_matrix.csv
data/processed/transition_sequences.csv
data/reports/transition_engine_report.txt
```

Transition frequencies are descriptive frequencies inside the processed
dataset only. They are not predictive probabilities. Transitions are built only
within the same `Symbol` and `Timeframe`; states from different symbols or
timeframes are never linked together.

## Research Engine

Phase 7.1 summarizes historical state and transition conditions from the
processed SQRE dataset. It is descriptive only and does not generate trading
signals, price outcome research, backtesting, machine learning, or portfolio
logic.

Input files:

```text
data/processed/market_states.csv
data/processed/state_transitions.csv
```

Run:

```bash
python3 scripts/run_research_engine.py \
  --states data/processed/market_states.csv \
  --transitions data/processed/state_transitions.csv \
  --output-dir data/research \
  --report data/reports/research_engine_report.txt
```

The Research Engine writes:

```text
data/research/forward_state_distributions.csv
data/research/forward_transition_distributions.csv
data/research/preceding_state_distributions.csv
data/research/sequence_outcomes.csv
data/research/condition_summaries.csv
data/reports/research_engine_report.txt
```

The generated frequencies describe observed historical occurrence inside the
processed dataset only. Low sample size conditions are flagged for review.

## Price Outcome Research

Phase 7.2 connects market states and state transitions with observed forward
price behavior inside the processed dataset. It measures historical price
outcome fields such as observed forward close return, observed forward range,
observed favorable displacement, observed adverse displacement, and direction
alignment rate.

Input files:

```text
data/processed/market_states.csv
data/processed/state_transitions.csv
data/raw/EURUSD_H1.csv
```

Run:

```bash
python3 scripts/run_price_outcome_research.py \
  --states data/processed/market_states.csv \
  --transitions data/processed/state_transitions.csv \
  --ohlc data/raw/EURUSD_H1.csv \
  --output-dir data/research \
  --report data/reports/price_outcome_research_report.txt \
  --pip-size 0.0001 \
  --forward-candles 3,6,12 \
  --minimum-sample-size 5
```

For each state or transition occurrence, `Reference_Time` is the occurrence
`End_Time`. SQRE aligns that timestamp to the first OHLC candle where `Date` is
greater than or equal to `Reference_Time`. Forward candles start after the
reference candle; the reference candle is not included in the forward window.

`pip_size` controls pip conversion for return, range, and displacement fields.
Incomplete forward windows near the end of a dataset are retained and marked
explicitly. Low sample size groups are also marked explicitly.

The Price Outcome Research pipeline writes:

```text
data/research/price_outcomes.csv
data/research/condition_price_outcome_summary.csv
data/research/price_outcome_distributions.csv
data/reports/price_outcome_research_report.txt
```

This phase is descriptive only. It does not run backtesting, profitability
analysis, position sizing, machine learning, optimization, or decision
guidance.
