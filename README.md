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

## Multi-Scenario Validation

Phase 7.3A runs the SQRE pipeline across configured scenarios and timeframes,
then writes a consolidated validation summary.

Config file:

```text
configs/validation/eurusd_multitimeframe_validation.yaml
```

Run all configured scenarios:

```bash
python3 scripts/run_multi_scenario_validation.py \
  --config configs/validation/eurusd_multitimeframe_validation.yaml \
  --output-dir data/validation \
  --report data/validation/multi_scenario_validation_report.txt
```

Run one scenario:

```bash
python3 scripts/run_multi_scenario_validation.py \
  --config configs/validation/eurusd_multitimeframe_validation.yaml \
  --scenario eurusd_m5_period_2 \
  --output-dir data/validation \
  --report data/validation/multi_scenario_validation_report.txt
```

The runner writes per-scenario artifacts under:

```text
data/validation/<scenario_id>/processed
data/validation/<scenario_id>/research
data/validation/<scenario_id>/reports
```

It also writes:

```text
data/validation/multi_scenario_validation_summary.csv
data/validation/multi_scenario_validation_report.txt
```

Missing input files are marked as `MISSING_INPUT` in non-strict mode. Use
`--strict` to stop on the first missing input or failed scenario. Use
`--skip-existing` to keep existing scenario outputs.

This phase is a descriptive validation orchestrator. It does not add execution
guidance, portfolio logic, backtesting, machine learning, optimization, or a
decision layer.

## Calibration Review

Phase 7.4 reads consolidated validation summaries and produces a diagnostic
calibration review across scenarios and timeframes.

Run after multi-scenario validation and temporal OOS validation summaries exist:

```bash
python3 scripts/run_calibration_review.py \
  --summary-csv data/validation/multi_scenario_validation_summary.csv \
  --summary-csv data/validation/temporal_oos_validation_summary.csv \
  --output data/validation/calibration_review_summary.csv \
  --report data/validation/calibration_review_report.txt
```

Optional diagnostic thresholds:

```bash
python3 scripts/run_calibration_review.py \
  --summary-csv data/validation/multi_scenario_validation_summary.csv \
  --summary-csv data/validation/temporal_oos_validation_summary.csv \
  --output data/validation/calibration_review_summary.csv \
  --report data/validation/calibration_review_report.txt \
  --duration-near-max-threshold 0.85 \
  --state-dominance-threshold 0.60 \
  --low-state-diversity-threshold 4 \
  --low-sample-rate-threshold 0.50 \
  --high-directional-ratio-threshold 0.75
```

The runner writes:

```text
data/validation/calibration_review_summary.csv
data/validation/calibration_review_report.txt
```

This phase is diagnostic only. It compares validation metrics, highlights
low-sample and concentration patterns, and leaves all SQRE runtime behavior
unchanged.

## Calibration Adjustment Experiments

Phase 7.4.1 follows Calibration Review with controlled diagnostic experiments.
It compares duration sensitivity and minimum sample size sensitivity across
configured H4 and D1 scenarios.

Config file:

```text
configs/validation/calibration_experiments.yaml
```

Run all configured experiments:

```bash
python3 scripts/run_calibration_experiments.py \
  --config configs/validation/calibration_experiments.yaml \
  --output-dir data/validation/calibration_experiments \
  --summary-csv data/validation/calibration_experiments/calibration_experiment_summary.csv \
  --report data/validation/calibration_experiments/calibration_experiment_report.txt
```

Run only duration experiments:

```bash
python3 scripts/run_calibration_experiments.py \
  --config configs/validation/calibration_experiments.yaml \
  --output-dir data/validation/calibration_experiments \
  --summary-csv data/validation/calibration_experiments/calibration_experiment_summary.csv \
  --report data/validation/calibration_experiments/calibration_experiment_report.txt \
  --experiment-type DURATION
```

Run one scenario:

```bash
python3 scripts/run_calibration_experiments.py \
  --config configs/validation/calibration_experiments.yaml \
  --output-dir data/validation/calibration_experiments \
  --summary-csv data/validation/calibration_experiments/calibration_experiment_summary.csv \
  --report data/validation/calibration_experiments/calibration_experiment_report.txt \
  --scenario eurusd_h4_period_1
```

The runner writes experiment outputs under:

```text
data/validation/calibration_experiments/<experiment_id>/<scenario_id>/processed
data/validation/calibration_experiments/<experiment_id>/<scenario_id>/research
data/validation/calibration_experiments/<experiment_id>/<scenario_id>/reports
```

It also writes:

```text
data/validation/calibration_experiments/calibration_experiment_summary.csv
data/validation/calibration_experiments/calibration_experiment_report.txt
```

This phase does not modify production thresholds or runtime defaults. Market
State threshold experiments are deferred to a later configuration phase.

## Timeframe-Aware State Threshold Experiments

Phase 7.4.2 adds optional Market State threshold profiles while preserving the
default production behavior. Running Market States without a config still uses
the original v1.0 thresholds.

Run Market States with an explicit threshold profile:

```bash
python3 scripts/run_market_states.py \
  --structures data/processed/structures.csv \
  --output data/processed/market_states.csv \
  --report data/reports/market_states_report.txt \
  --state-config configs/validation/state_threshold_profiles.yaml \
  --state-profile balanced_high_tf \
  --timeframe H4
```

Run all configured state threshold experiments:

```bash
python3 scripts/run_state_threshold_experiments.py \
  --config configs/validation/state_threshold_experiments.yaml \
  --output-dir data/validation/state_threshold_experiments \
  --summary-csv data/validation/state_threshold_experiments/state_threshold_experiment_summary.csv \
  --report data/validation/state_threshold_experiments/state_threshold_experiment_report.txt
```

Run a single profile and scenario:

```bash
python3 scripts/run_state_threshold_experiments.py \
  --config configs/validation/state_threshold_experiments.yaml \
  --output-dir data/validation/state_threshold_experiments \
  --summary-csv data/validation/state_threshold_experiments/state_threshold_experiment_summary.csv \
  --report data/validation/state_threshold_experiments/state_threshold_experiment_report.txt \
  --profile directional_stricter \
  --scenario eurusd_h4_period_1
```

The runner writes profile/scenario outputs under:

```text
data/validation/state_threshold_experiments/<profile_id>/<scenario_id>/processed
data/validation/state_threshold_experiments/<profile_id>/<scenario_id>/research
data/validation/state_threshold_experiments/<profile_id>/<scenario_id>/reports
```

It also writes:

```text
data/validation/state_threshold_experiments/state_threshold_experiment_summary.csv
data/validation/state_threshold_experiments/state_threshold_experiment_report.txt
```

This phase is diagnostic only. It does not modify default thresholds, does not
change production runtime behavior, and does not add operational market action
logic.

## Expanded Historical Sample Validation

Phase 7.4.3 adds configuration and utility scripts for expanding EURUSD
historical validation coverage across M5, H1, H4, and D1 samples. It prepares a
larger research sample set without changing production defaults or runtime
thresholds.

Expanded sample plan:

```text
configs/validation/eurusd_expanded_historical_samples.yaml
```

Generate download commands without executing them:

```bash
python3 scripts/generate_expanded_sample_download_commands.py \
  --config configs/validation/eurusd_expanded_historical_samples.yaml
```

Generate commands for one timeframe:

```bash
python3 scripts/generate_expanded_sample_download_commands.py \
  --config configs/validation/eurusd_expanded_historical_samples.yaml \
  --timeframe H4
```

Write a shell script containing only currently missing sample downloads:

```bash
python3 scripts/generate_expanded_sample_download_commands.py \
  --config configs/validation/eurusd_expanded_historical_samples.yaml \
  --missing-only \
  --output-script scripts/download_expanded_historical_samples.sh
```

Check which expanded sample files are available locally:

```bash
python3 scripts/check_expanded_sample_data.py \
  --samples-config configs/validation/eurusd_expanded_historical_samples.yaml \
  --validation-config configs/validation/eurusd_expanded_historical_validation.yaml \
  --output data/validation/expanded_historical_data_availability.csv \
  --report data/validation/expanded_historical_data_availability_report.txt
```

### Historical Sample Coverage Completeness

File existence is not enough for expanded historical validation. A sample also
needs to cover the configured expected date range. The availability checker
compares each file's actual first and last timestamps against the configured
sample window, then classifies each file as:

```text
AVAILABLE_FULL
AVAILABLE_PARTIAL
MISSING
INVALID_COLUMNS
EMPTY_FILE
READ_ERROR
```

`AVAILABLE_PARTIAL` means the file exists and has valid OHLC columns, but the
actual date range does not sufficiently cover the expected date range. Partial
files should not be interpreted as full historical samples. This helps identify
provider historical limitations before running expanded validation.

Run the coverage completeness check with explicit tolerances:

```bash
python3 scripts/check_expanded_sample_data.py \
  --samples-config configs/validation/eurusd_expanded_historical_samples.yaml \
  --validation-config configs/validation/eurusd_expanded_historical_validation.yaml \
  --output data/validation/expanded_historical_data_availability.csv \
  --report data/validation/expanded_historical_data_availability_report.txt \
  --min-coverage-ratio 0.90 \
  --max-start-gap-days 7 \
  --max-end-gap-days 7
```

Run expanded multi-scenario validation after the required raw CSV files exist:

```bash
python3 scripts/run_multi_scenario_validation.py \
  --config configs/validation/eurusd_expanded_historical_validation.yaml \
  --output-dir data/validation/expanded_historical \
  --report data/validation/expanded_historical/multi_scenario_validation_report.txt \
  --summary-csv data/validation/expanded_historical/multi_scenario_validation_summary.csv
```

The expanded validation config includes 25 scenarios: the existing EURUSD
validation scenarios plus 18 additional historical sample targets. This phase is
research-only and does not introduce automated threshold changes, model
selection, backtesting, or a decision layer.

## Expanded Historical Calibration Review

Phase 7.4.4 reads expanded historical validation summary CSV files and produces
a diagnostic calibration review by timeframe. It is designed for descriptive
review of structural stability, state diversity, low sample pressure, and
forward range regime sensitivity across expanded EURUSD samples.

Input summary CSV example:

```text
data/validation/expanded_historical_consolidated/all_timeframes_expanded_summary.csv
```

Run:

```bash
python3 scripts/run_expanded_calibration_review.py \
  --summary-csv data/validation/expanded_historical_consolidated/all_timeframes_expanded_summary.csv \
  --output data/validation/expanded_historical_calibration_review/expanded_calibration_review_summary.csv \
  --report data/validation/expanded_historical_calibration_review/expanded_calibration_review_report.txt
```

The runner writes:

```text
data/validation/expanded_historical_calibration_review/expanded_calibration_review_summary.csv
data/validation/expanded_historical_calibration_review/expanded_calibration_review_report.txt
```

The summary includes timeframe-level metrics for scenario count, OHLC rows,
structure count variation, average structure duration, state diversity, state
composition ratios, forward range variation, direction alignment rate, and low
sample pressure.

Diagnostic flags include:

```text
Structural_Stability_Flag
State_Diversity_Flag
Low_Sample_Pressure_Flag
Forward_Range_Regime_Sensitivity_Flag
Unclassified_Pressure_Flag
Low_Quality_Pressure_Flag
```

The review also emits descriptive diagnostic profiles and non-operational
follow-up text. This phase does not change production defaults, does not modify
thresholds, and does not introduce trading logic.
