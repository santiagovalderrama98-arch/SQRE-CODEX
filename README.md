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

## Master Historical Calibration Review

Phase 7.4.5 builds a deduplicated master historical calibration summary from
multiple validation summary CSV files. It is useful when historical validation
results are split across initial multi-scenario validation, temporal
out-of-sample validation, and expanded historical validation outputs.

Some scenarios can appear in more than one summary. The master builder
deduplicates by `Scenario_ID` so the expanded calibration review consumes one
retained row per scenario while still recording source-file provenance.

Input summary examples:

```text
data/validation/multi_scenario_validation_summary.csv
data/validation/temporal_oos_validation_summary.csv
data/validation/expanded_historical_consolidated/all_timeframes_expanded_summary.csv
```

Build the master summary:

```bash
python3 scripts/build_master_calibration_summary.py \
  --summary-csv data/validation/multi_scenario_validation_summary.csv \
  --summary-csv data/validation/temporal_oos_validation_summary.csv \
  --summary-csv data/validation/expanded_historical_consolidated/all_timeframes_expanded_summary.csv \
  --output data/validation/master_historical_calibration/master_historical_summary.csv \
  --report data/validation/master_historical_calibration/master_historical_summary_report.txt
```

The default dedupe policy is `last`, which keeps the later occurrence of a
duplicate scenario. This is intended for research workflows where later
validation summaries may contain refined or more complete runs.

Available dedupe policies:

```text
first
last
error
```

If some expected input files are not available locally, run with:

```bash
--allow-missing-inputs
```

The builder writes:

```text
data/validation/master_historical_calibration/master_historical_summary.csv
data/validation/master_historical_calibration/master_historical_summary_report.txt
```

Run the expanded calibration review on the master summary:

```bash
python3 scripts/run_expanded_calibration_review.py \
  --summary-csv data/validation/master_historical_calibration/master_historical_summary.csv \
  --output data/validation/master_historical_calibration/master_expanded_calibration_review_summary.csv \
  --report data/validation/master_historical_calibration/master_expanded_calibration_review_report.txt
```

This phase is diagnostic and research-only. It does not change production
defaults, does not modify thresholds, and does not introduce trading logic.

## H1/M5 Duration Calibration Experiments

Phase 7.4.6 adds a controlled duration calibration experiment workflow for H1
and M5 only. The purpose is to compare candidate duration profiles against each
timeframe's own baseline reference and produce descriptive diagnostics for
structural fragmentation, structural compression, duration utilization, low
sample pressure, and state diversity.

H1 and M5 are targeted because prior calibration reviews identified H1 as a
timeframe-specific duration calibration candidate and M5 as a microstructure
calibration candidate. H4 and D1 remain monitoring references and are not varied
in this phase.

Duration profiles:

```text
H1:
- h1_duration_18h: 64800 seconds
- h1_duration_24h_baseline: 86400 seconds
- h1_duration_30h: 108000 seconds

M5:
- m5_duration_2h: 7200 seconds
- m5_duration_3h: 10800 seconds
- m5_duration_4h_baseline: 14400 seconds
- m5_duration_6h: 21600 seconds
```

Expected configured run count when all inputs exist:

```text
H1: 7 scenarios x 3 profiles = 21 runs
M5: 7 scenarios x 4 profiles = 28 runs
Total: 49 runs
```

Run the duration calibration experiments:

```bash
python3 scripts/run_calibration_experiments.py \
  --config configs/validation/h1_m5_duration_calibration_experiments.yaml \
  --output-dir data/validation/h1_m5_duration_calibration \
  --summary-csv data/validation/h1_m5_duration_calibration/h1_m5_duration_experiment_summary.csv \
  --report data/validation/h1_m5_duration_calibration/h1_m5_duration_experiment_report.txt
```

Run the duration calibration review:

```bash
python3 scripts/run_timeframe_duration_calibration_review.py \
  --experiment-summary data/validation/h1_m5_duration_calibration/h1_m5_duration_experiment_summary.csv \
  --output data/validation/h1_m5_duration_calibration/h1_m5_duration_review_summary.csv \
  --report data/validation/h1_m5_duration_calibration/h1_m5_duration_review_report.txt
```

The experiment writes:

```text
data/validation/h1_m5_duration_calibration/h1_m5_duration_experiment_summary.csv
data/validation/h1_m5_duration_calibration/h1_m5_duration_experiment_report.txt
```

The review writes:

```text
data/validation/h1_m5_duration_calibration/h1_m5_duration_review_summary.csv
data/validation/h1_m5_duration_calibration/h1_m5_duration_review_report.txt
```

The review computes structure count CV, duration utilization, state diversity,
state composition ratios, forward range metrics, direction alignment, low sample
pressure, and relative changes versus the timeframe baseline reference.

Diagnostic flags include:

```text
Structure_Stability_Flag
Duration_Utilization_Flag
Low_Sample_Pressure_Flag
Fragmentation_Flag
Compression_Flag
```

This phase is diagnostic and research-only. It does not change production
defaults, does not modify thresholds, and does not add operational logic.

## M15 Timeframe Introduction & Validation

Phase 7.4.7 introduces EURUSD M15 as a descriptive intraday research timeframe.
M15 is reviewed separately before any later aggregation because prior work
paused M5 taxonomy compression review and identified a need for a cleaner
intraday bridge between M5 and H1 context.

M15 historical sample plan:

```text
configs/validation/eurusd_m15_historical_samples.yaml
```

Configured M15 periods:

```text
eurusd_m15_period_1: 2026-06-01 -> 2026-06-30
eurusd_m15_period_2: 2026-05-01 -> 2026-05-31
eurusd_m15_period_3: 2026-04-01 -> 2026-04-30
eurusd_m15_period_4: 2026-03-01 -> 2026-03-31
eurusd_m15_period_5: 2026-02-01 -> 2026-02-28
eurusd_m15_period_6: 2025-12-01 -> 2025-12-31
eurusd_m15_period_7: 2025-09-01 -> 2025-09-30
```

Generate download commands for missing M15 samples:

```bash
python3 scripts/generate_expanded_sample_download_commands.py \
  --config configs/validation/eurusd_m15_historical_samples.yaml \
  --timeframe M15 \
  --missing-only \
  --output-script data/validation/download_m15_samples.sh
```

Check M15 sample availability:

```bash
python3 scripts/check_expanded_sample_data.py \
  --samples-config configs/validation/eurusd_m15_historical_samples.yaml \
  --validation-config configs/validation/eurusd_m15_validation.yaml \
  --output data/validation/m15_data_availability.csv \
  --report data/validation/m15_data_availability_report.txt \
  --min-coverage-ratio 0.90 \
  --max-start-gap-days 7 \
  --max-end-gap-days 7
```

Run M15 validation after the raw M15 CSV files exist:

```bash
python3 scripts/run_multi_scenario_validation.py \
  --config configs/validation/eurusd_m15_validation.yaml \
  --output-dir data/validation/m15_introduction \
  --report data/validation/m15_introduction/m15_validation_report.txt \
  --summary-csv data/validation/m15_introduction/m15_validation_summary.csv
```

M15 validation parameters:

```text
max_structure_duration_seconds: 28800
forward_candles: [3, 6, 12]
minimum_sample_size: 5
pip_size: 0.0001
```

Run the M15 introduction review:

```bash
python3 scripts/run_m15_introduction_review.py \
  --m15-summary-csv data/validation/m15_introduction/m15_validation_summary.csv \
  --master-summary-csv data/validation/master_historical_calibration/master_historical_summary.csv \
  --output data/validation/m15_introduction/m15_introduction_review_summary.csv \
  --report data/validation/m15_introduction/m15_introduction_review_report.txt
```

The M15 review writes:

```text
data/validation/m15_introduction/m15_introduction_review_summary.csv
data/validation/m15_introduction/m15_introduction_review_report.txt
```

The summary includes M15 scenario coverage, structure count stability, duration
utilization, state diversity, state composition ratios, forward range
stability, low sample pressure, and optional descriptive M5/H1 context.

Diagnostic flags include:

```text
Structure_Stability_Flag
Duration_Utilization_Flag
State_Diversity_Flag
Low_Sample_Pressure_Flag
Forward_Range_Stability_Flag
M15_Diagnostic_Profile
```

This phase does not include M5 period 8 and does not include H1, H4, or D1 as
M15 scenarios. It does not change production defaults, thresholds, production
taxonomy, Event Detection defaults, Market Structure defaults, H1/H4/D1
behavior, or existing validation behavior. It does not add operational logic,
automated threshold changes, model selection, machine learning, backtesting, or
a decision layer. No comparative ordering is produced.

## M15 Duration Calibration Experiments

Phase 7.4.8 adds a controlled M15 duration calibration experiment workflow.
The purpose is to review how alternative maximum structure durations affect M15
structure formation, duration utilization, state diversity, low sample pressure,
and descriptive forward range measurements.

M15 needs this separate duration review because the introduction phase showed a
stable intraday sample set with high duration utilization and high state
diversity. The baseline is useful as a reference, but M15 requires a dedicated
duration profile review before any later calibration decision.

Duration profiles:

```text
m15_duration_4h: 14400 seconds
m15_duration_6h: 21600 seconds
m15_duration_8h_baseline: 28800 seconds
m15_duration_10h: 36000 seconds
m15_duration_12h: 43200 seconds
```

Expected configured run count when all seven M15 raw files exist:

```text
7 M15 scenarios x 5 duration profiles = 35 runs
```

Run the M15 duration calibration experiment:

```bash
python3 scripts/run_calibration_experiments.py \
  --config configs/validation/m15_duration_calibration_experiments.yaml \
  --output-dir data/validation/m15_duration_calibration \
  --summary-csv data/validation/m15_duration_calibration/m15_duration_experiment_summary.csv \
  --report data/validation/m15_duration_calibration/m15_duration_experiment_report.txt
```

Run the M15 duration review:

```bash
python3 scripts/run_m15_duration_calibration_review.py \
  --experiment-summary data/validation/m15_duration_calibration/m15_duration_experiment_summary.csv \
  --output data/validation/m15_duration_calibration/m15_duration_review_summary.csv \
  --report data/validation/m15_duration_calibration/m15_duration_review_report.txt
```

The workflow writes:

```text
data/validation/m15_duration_calibration/m15_duration_experiment_summary.csv
data/validation/m15_duration_calibration/m15_duration_experiment_report.txt
data/validation/m15_duration_calibration/m15_duration_review_summary.csv
data/validation/m15_duration_calibration/m15_duration_review_report.txt
```

The review computes profile-level structure counts, structure count CV,
duration utilization ratios, unique state counts, state composition totals and
ratios, low sample pressure, forward range averages, direction alignment, and
relative changes versus `m15_duration_8h_baseline`.

Diagnostic flags include:

```text
Structure_Stability_Flag
Duration_Utilization_Flag
State_Diversity_Flag
Low_Sample_Pressure_Flag
Fragmentation_Flag
Compression_Flag
Profile_Diagnostic
Recommended_Follow_Up
```

This phase is M15-only. It excludes M5 period 8, M5 scenarios, H1 scenarios,
H4 scenarios, and D1 scenarios. It does not change production defaults,
thresholds, production taxonomy, Event Detection defaults, Market Structure
defaults, H1/H4/D1 behavior, validation behavior, or production runtime
behavior. It does not add operational logic, automated threshold changes,
model selection, machine learning, backtesting, or a decision layer. No
comparative ordering is produced.

## H4/D1 Structural Research Program

Phase 7.5 starts a dedicated H4/D1 structural research workflow. Calibration
work is paused so SQRE can focus on descriptive historical behavior for the
most mature structural timeframes.

H4 is used as the main structural research timeframe. D1 is used as
higher-timeframe and regime context. M15 remains a secondary intraday candidate,
H1 remains useful intraday context, and M5 remains paused as microstructure
context.

H4 scenarios:

```text
eurusd_h4_period_1
eurusd_h4_period_2
eurusd_h4_period_3
eurusd_h4_period_4
```

D1 scenarios:

```text
eurusd_d1_period_1
eurusd_d1_period_2
eurusd_d1_period_3
eurusd_d1_period_4
```

Run H4/D1 validation:

```bash
python3 scripts/run_multi_scenario_validation.py \
  --config configs/validation/h4_d1_structural_research_validation.yaml \
  --output-dir data/validation/h4_d1_structural_research \
  --report data/validation/h4_d1_structural_research/h4_d1_validation_report.txt \
  --summary-csv data/validation/h4_d1_structural_research/h4_d1_validation_summary.csv
```

Run H4/D1 structural research:

```bash
python3 scripts/run_h4_d1_structural_research.py \
  --validation-summary data/validation/h4_d1_structural_research/h4_d1_validation_summary.csv \
  --validation-output-dir data/validation/h4_d1_structural_research \
  --output-dir data/research/h4_d1_structural_research \
  --report data/research/h4_d1_structural_research/h4_d1_structural_research_report.txt
```

The research workflow writes:

```text
data/research/h4_d1_structural_research/h4_d1_scenario_inventory.csv
data/research/h4_d1_structural_research/h4_d1_state_research_profiles.csv
data/research/h4_d1_structural_research/h4_d1_transition_research_profiles.csv
data/research/h4_d1_structural_research/h4_d1_price_outcome_profiles.csv
data/research/h4_d1_structural_research/h4_d1_sequence_research_profiles.csv
data/research/h4_d1_structural_research/h4_d1_timeframe_research_summary.csv
data/research/h4_d1_structural_research/h4_d1_structural_research_report.txt
```

The workflow computes scenario inventory, state profile counts and frequencies,
transition profile counts and frequencies, price outcome profile ranges and
magnitudes, sequence profile availability, sample adequacy, scenario
consistency, and regime sensitivity.

Diagnostic flags include:

```text
State_Sample_Adequacy_Flag
State_Scenario_Consistency_Flag
Transition_Sample_Adequacy_Flag
Transition_Consistency_Flag
Scenario_Sensitivity_Flag
Sample_Adequacy_Flag
Structural_Maturity_Flag
Research_Sample_Quality_Flag
```

This phase includes only H4 and D1 periods 1 through 4. It excludes M5, M15,
H1, H4 period 5, H4 period 6, and partial samples. It does not change
production defaults, thresholds, production taxonomy, Event Detection defaults,
Market Structure defaults, validation behavior, or production runtime behavior.
It does not add operational logic, automated threshold changes, model
selection, machine learning, backtesting, or a Decision Engine. No comparative
ordering is produced.

## D1 Regime-Normalized Price Outcome Research

Phase 7.5.1 adds a D1-only research workflow for reviewing price outcome
behavior by scenario-period regime. Calibration work remains paused. The goal is
to compare D1 condition outcomes across historical scenario labels without
changing production behavior.

D1 is used because the H4/D1 structural research program marked it as the
higher-timeframe regime context. Regime normalization helps separate descriptive
outcome dispersion by scenario period before later research review.

Regime labels are scenario-period labels only:

```text
eurusd_d1_period_1 -> D1_REGIME_2021_2026 -> 2021_2026_recent_regime
eurusd_d1_period_2 -> D1_REGIME_2015_2020 -> 2015_2020_pre_recent_regime
eurusd_d1_period_3 -> D1_REGIME_2010_2015 -> 2010_2015_mid_history_regime
eurusd_d1_period_4 -> D1_REGIME_2004_2009 -> 2004_2009_early_history_regime
```

These labels do not make macroeconomic causal claims.

Run D1 regime-normalized research after the H4/D1 validation outputs exist:

```bash
python3 scripts/run_d1_regime_normalized_research.py \
  --config configs/validation/d1_regime_normalized_research.yaml \
  --validation-summary data/validation/h4_d1_structural_research/h4_d1_validation_summary.csv \
  --validation-output-dir data/validation/h4_d1_structural_research \
  --output-dir data/research/d1_regime_normalized_research \
  --report data/research/d1_regime_normalized_research/d1_regime_normalized_research_report.txt
```

The workflow writes:

```text
data/research/d1_regime_normalized_research/d1_regime_scenario_inventory.csv
data/research/d1_regime_normalized_research/d1_regime_condition_outcomes.csv
data/research/d1_regime_normalized_research/d1_regime_normalized_condition_profiles.csv
data/research/d1_regime_normalized_research/d1_regime_state_outcome_profiles.csv
data/research/d1_regime_normalized_research/d1_regime_transition_outcome_profiles.csv
data/research/d1_regime_normalized_research/d1_regime_research_summary.csv
data/research/d1_regime_normalized_research/d1_regime_normalized_research_report.txt
```

Metrics include sample size, average forward close return, average forward
range, outcome magnitude, direction alignment rate, coefficient of variation,
range dispersion, outcome magnitude dispersion, and regime coverage.

Flags include:

```text
Sample_Adequacy_Flag
Regime_Coverage_Flag
Regime_Sensitivity_Flag
Research_Readiness_Flag
Regime_Sensitivity_Profile
```

This phase includes D1 scenario periods 1 through 4 only. It excludes H4, H1,
M15, M5, and partial samples. It does not change production defaults,
thresholds, production taxonomy, validation behavior, Event Detection defaults,
Market Structure defaults, or production runtime behavior. It does not add
operational logic, automated threshold changes, model selection, machine
learning, backtesting, or a Decision Engine. No comparative ordering is
produced.

## D1 Regime Outcome Dispersion & Sample Adequacy Review

Phase 7.5.2 adds a D1-only review layer on top of the regime-normalized
research outputs. It separates descriptive condition profiles by sample
adequacy, regime coverage, outcome dispersion, and regime sensitivity.

Run after `data/research/d1_regime_normalized_research` exists:

```bash
python3 scripts/run_d1_regime_outcome_review.py \
  --input-dir data/research/d1_regime_normalized_research \
  --output-dir data/research/d1_regime_outcome_review \
  --report data/research/d1_regime_outcome_review/d1_regime_outcome_review_report.txt
```

The workflow writes:

```text
data/research/d1_regime_outcome_review/d1_condition_quality_inventory.csv
data/research/d1_regime_outcome_review/d1_research_ready_condition_profiles.csv
data/research/d1_regime_outcome_review/d1_regime_sensitive_condition_profiles.csv
data/research/d1_regime_outcome_review/d1_low_sample_condition_profiles.csv
data/research/d1_regime_outcome_review/d1_limited_coverage_condition_profiles.csv
data/research/d1_regime_outcome_review/d1_state_condition_quality_summary.csv
data/research/d1_regime_outcome_review/d1_transition_condition_quality_summary.csv
data/research/d1_regime_outcome_review/d1_outcome_dispersion_summary.csv
data/research/d1_regime_outcome_review/d1_sample_adequacy_summary.csv
data/research/d1_regime_outcome_review/d1_regime_outcome_review_summary.csv
data/research/d1_regime_outcome_review/d1_regime_outcome_review_report.txt
```

Default review thresholds:

```text
minimum_total_sample_size = 20
minimum_regime_count = 2
full_regime_count = 4
moderate_dispersion_threshold = 0.20
high_dispersion_threshold = 0.35
moderate_sensitivity_threshold = 0.20
high_sensitivity_threshold = 0.35
low_sample_share_threshold = 0.50
```

This phase is descriptive only. It does not change production defaults,
Market State thresholds, Event Detection defaults, Market Structure defaults,
validation behavior, or production runtime behavior. It does not add
operational logic, automated threshold changes, machine learning, backtesting,
or a Decision Engine. No comparative ordering is produced.

## Phase 7.5.7 — H4 Transition Outcome Deep Dive

Phase 7.5.7 adds a research-only H4 transition outcome deep dive after the H4
scenario-sensitive state profile review. Phase 7.5.6 found that isolated H4
state profiles remain scenario-sensitive, so this phase reviews whether H4
`TRANSITION_CONDITION` profiles provide clearer descriptive structure than
isolated H4 state labels.

Run after `data/research/h4_d1_structural_research` and
`data/validation/h4_d1_structural_research` exist:

```bash
python3 scripts/run_h4_transition_outcome_deep_dive.py \
  --h4-d1-research-dir data/research/h4_d1_structural_research \
  --validation-output-dir data/validation/h4_d1_structural_research \
  --output-dir data/research/h4_transition_outcome_deep_dive \
  --report data/research/h4_transition_outcome_deep_dive/h4_transition_outcome_deep_dive_report.txt
```

Required input:

```text
data/research/h4_d1_structural_research/h4_d1_price_outcome_profiles.csv
```

Optional inputs include:

```text
data/research/h4_d1_structural_research/h4_d1_transition_research_profiles.csv
data/research/h4_d1_structural_research/h4_d1_timeframe_research_summary.csv
data/research/h4_d1_structural_research/h4_d1_scenario_inventory.csv
data/validation/h4_d1_structural_research/<scenario>/research/condition_price_outcome_summary.csv
data/validation/h4_d1_structural_research/<scenario>/research/price_outcomes.csv
data/validation/h4_d1_structural_research/<scenario>/processed/state_transitions.csv
```

Selected profiles are filtered from `Timeframe=H4` and
`Condition_Type=TRANSITION_CONDITION`. Transition labels are parsed into:

```text
Source_State
Target_State
Transition_Family
```

Supported label shapes include arrow labels, `_TO_` labels, pipe-separated
labels, double-underscore labels, slash-separated labels, and
`TRANSITION:SOURCE:TARGET` labels. Unknown labels are retained with
`UNKNOWN` source and target values so the workflow does not fabricate
structure.

The workflow writes:

```text
data/research/h4_transition_outcome_deep_dive/h4_transition_deep_dive_profile_inventory.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_scenario_breakdown.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_outcome_statistics.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_scenario_comparison_matrix.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_family_summary.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_deep_dive_summary.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_outcome_deep_dive_report.txt
```

Classification rules remain descriptive:

```text
Profile_Type:
  SAMPLE_CONSTRAINED_OBSERVATION when total sample or scenario coverage is limited
  SCENARIO_SENSITIVE_OBSERVATION when adequate-sample profiles have high dispersion
  RESEARCH_READY otherwise

Dispersion_Class:
  HIGH_DISPERSION
  MODERATE_DISPERSION
  STABLE_DESCRIPTIVE

Transition_Research_Class:
  RESEARCH_READY_DESCRIPTIVE
  SCENARIO_SENSITIVE_REVIEW
  SAMPLE_REVIEW
```

Metrics include scenario sample size, forward close return, forward range,
favorable and adverse displacement, outcome magnitude, direction alignment,
forward range CV, outcome magnitude CV, scenario-period deviation classes,
transition family summaries, and transition deep dive summaries.

This phase is descriptive only. Scenario periods are descriptive partitions and
not causal claims. It does not change production defaults, thresholds,
production taxonomy, Event Detection defaults, Market Structure defaults,
validation behavior, H4/D1 structural research outputs, H4 state deep dive
outputs, H4 scenario dispersion outputs, H4 scenario-sensitive state review
outputs, or production runtime behavior. It does not add operational logic,
automated threshold changes, machine learning, backtesting, or a Decision
Engine. No comparative ordering is produced.

## Phase 7.5.8 — H4 Transition Scenario Dispersion Review

Phase 7.5.8 adds a research-only review layer after the H4 transition outcome
deep dive. Phase 7.5.7 identified H4 `TRANSITION_CONDITION` profiles and
scenario-period outcome differences. This phase reviews whether those
transition profiles remain stable across scenario periods, which transition
families carry elevated dispersion, and which profiles require scenario-aware
interpretation before any later descriptive aggregation review.

Run after `data/research/h4_transition_outcome_deep_dive` exists:

```bash
python3 scripts/run_h4_transition_scenario_dispersion_review.py \
  --input-dir data/research/h4_transition_outcome_deep_dive \
  --output-dir data/research/h4_transition_scenario_dispersion_review \
  --report data/research/h4_transition_scenario_dispersion_review/h4_transition_scenario_dispersion_review_report.txt
```

Required inputs:

```text
data/research/h4_transition_outcome_deep_dive/h4_transition_outcome_statistics.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_scenario_comparison_matrix.csv
```

Optional inputs:

```text
data/research/h4_transition_outcome_deep_dive/h4_transition_deep_dive_profile_inventory.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_scenario_breakdown.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_family_summary.csv
data/research/h4_transition_outcome_deep_dive/h4_transition_deep_dive_summary.csv
```

The workflow writes:

```text
data/research/h4_transition_scenario_dispersion_review/h4_transition_profile_dispersion_diagnostics.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_scenario_dispersion_contribution.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_family_dispersion_summary.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_source_state_dispersion_summary.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_target_state_dispersion_summary.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_forward_window_dispersion_summary.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_aggregation_candidate_profiles.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_scenario_sensitive_profiles.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_sample_constrained_profiles.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_scenario_dispersion_review_summary.csv
data/research/h4_transition_scenario_dispersion_review/h4_transition_scenario_dispersion_review_report.txt
```

Classification rules remain descriptive:

```text
Profile_Dispersion_Class:
  HIGH_DISPERSION when range CV or outcome magnitude CV reaches the high threshold
  MODERATE_DISPERSION when either CV reaches the moderate threshold
  STABLE_DESCRIPTIVE otherwise

Dispersion_Driver_Class:
  RANGE_DRIVEN
  MAGNITUDE_DRIVEN
  MIXED_DRIVEN
  LOW_DISPERSION

Transition_Profile_Readiness_Class:
  SAMPLE_REVIEW
  SCENARIO_SENSITIVE_REVIEW
  AGGREGATION_CANDIDATE
  GENERAL_REVIEW

Scenario_Contribution_Class:
  HIGH_CONTRIBUTION
  MODERATE_CONTRIBUTION
  LOW_CONTRIBUTION
```

Metrics include transition profile dispersion diagnostics, scenario-period
deviation contribution, transition-family dispersion summaries, source-state
dispersion summaries, target-state dispersion summaries, forward-window
dispersion summaries, aggregation candidate profiles, scenario-sensitive
transition profiles, and sample-constrained transition profiles.

Scenario periods are descriptive partitions and not causal claims. This phase
does not change production defaults, thresholds, production taxonomy, Event
Detection defaults, Market Structure defaults, validation behavior, H4 state
outputs, H4 transition outcome outputs, or production runtime behavior. It
does not add operational logic, automated threshold changes, machine learning,
backtesting, or a Decision Engine. No comparative ordering is produced.

## Phase 7.5.6 — H4 Scenario-Sensitive State Profile Review

Phase 7.5.6 adds a research-only review layer after the H4 scenario dispersion
review. Phase 7.5.5 separates H4 state/window profiles into aggregation
candidates, scenario-sensitive profiles, and sample-constrained profiles. This
phase focuses on the scenario-sensitive H4 state profiles and describes which
metric families contribute to the observed scenario-period deviation.

Run after `data/research/h4_scenario_dispersion_review` and
`data/research/h4_state_outcome_deep_dive` exist:

```bash
python3 scripts/run_h4_scenario_sensitive_state_review.py \
  --dispersion-review-dir data/research/h4_scenario_dispersion_review \
  --state-deep-dive-dir data/research/h4_state_outcome_deep_dive \
  --output-dir data/research/h4_scenario_sensitive_state_review \
  --report data/research/h4_scenario_sensitive_state_review/h4_scenario_sensitive_state_review_report.txt
```

Required inputs:

```text
data/research/h4_scenario_dispersion_review/h4_scenario_sensitive_profiles.csv
data/research/h4_state_outcome_deep_dive/h4_state_scenario_comparison_matrix.csv
data/research/h4_state_outcome_deep_dive/h4_state_scenario_breakdown.csv
```

Optional inputs:

```text
data/research/h4_scenario_dispersion_review/h4_profile_dispersion_diagnostics.csv
data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_contribution.csv
data/research/h4_scenario_dispersion_review/h4_state_dispersion_summary.csv
data/research/h4_scenario_dispersion_review/h4_forward_window_dispersion_summary.csv
data/research/h4_scenario_dispersion_review/h4_sample_constrained_profiles.csv
data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_review_summary.csv
data/research/h4_state_outcome_deep_dive/h4_state_outcome_statistics.csv
data/research/h4_state_outcome_deep_dive/h4_state_deep_dive_profile_inventory.csv
```

The workflow writes:

```text
data/research/h4_scenario_sensitive_state_review/h4_scenario_sensitive_profile_review.csv
data/research/h4_scenario_sensitive_state_review/h4_profile_scenario_deviation_detail.csv
data/research/h4_scenario_sensitive_state_review/h4_scenario_recurrent_deviation_summary.csv
data/research/h4_scenario_sensitive_state_review/h4_state_sensitivity_summary.csv
data/research/h4_scenario_sensitive_state_review/h4_forward_window_sensitivity_summary.csv
data/research/h4_scenario_sensitive_state_review/h4_near_aggregation_candidate_review.csv
data/research/h4_scenario_sensitive_state_review/h4_scenario_sensitive_state_review_summary.csv
data/research/h4_scenario_sensitive_state_review/h4_scenario_sensitive_state_review_report.txt
```

Classification rules remain descriptive:

```text
Primary_Deviating_Metric:
  RANGE
  MAGNITUDE
  ALIGNMENT
  MIXED

Scenario_Sensitivity_Class:
  HIGH_SCENARIO_SENSITIVITY
  MODERATE_SCENARIO_SENSITIVITY
  LOW_SCENARIO_SENSITIVITY

Scenario_Recurrent_Deviation_Class:
  HIGH_RECURRENT_DEVIATION
  MODERATE_RECURRENT_DEVIATION
  LOW_RECURRENT_DEVIATION

H4_Review_Readiness_Flag:
  READY_FOR_TARGETED_REVIEW
  REQUIRES_SCENARIO_SENSITIVE_REVIEW
```

Metrics include forward range CV, outcome magnitude CV, direction alignment
dispersion, scenario-period deviation intensity, recurrent deviation classes,
state sensitivity summaries, forward-window sensitivity summaries, and
near-aggregation candidate counts. Near-candidate review is descriptive only;
no scenario-period is excluded or filtered automatically.

This phase is descriptive only. It does not change production defaults,
thresholds, production taxonomy, Event Detection defaults, Market Structure
defaults, validation behavior, Phase 7.5.5 outputs, H4 state deep dive outputs,
or production runtime behavior. It does not add operational logic, automated
threshold changes, machine learning, backtesting, or a Decision Engine.
Scenario periods are descriptive partitions and not causal claims. No
comparative ordering is produced.

## Phase 7.5.5 — H4 Scenario Dispersion Review

Phase 7.5.5 adds a research-only review layer after the H4
research-ready state outcome deep dive. Phase 7.5.4 identifies H4 state
outcome profiles and scenario-period deviations. This phase reviews whether
those profiles remain descriptively stable across H4 scenario periods or need
separate scenario dispersion review before any later aggregation study.

Run after `data/research/h4_state_outcome_deep_dive` exists:

```bash
python3 scripts/run_h4_scenario_dispersion_review.py \
  --input-dir data/research/h4_state_outcome_deep_dive \
  --output-dir data/research/h4_scenario_dispersion_review \
  --report data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_review_report.txt
```

Required inputs:

```text
data/research/h4_state_outcome_deep_dive/h4_state_outcome_statistics.csv
data/research/h4_state_outcome_deep_dive/h4_state_scenario_comparison_matrix.csv
```

Optional inputs:

```text
data/research/h4_state_outcome_deep_dive/h4_state_deep_dive_profile_inventory.csv
data/research/h4_state_outcome_deep_dive/h4_state_scenario_breakdown.csv
data/research/h4_state_outcome_deep_dive/h4_state_deep_dive_summary.csv
```

The workflow writes:

```text
data/research/h4_scenario_dispersion_review/h4_profile_dispersion_diagnostics.csv
data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_contribution.csv
data/research/h4_scenario_dispersion_review/h4_state_dispersion_summary.csv
data/research/h4_scenario_dispersion_review/h4_forward_window_dispersion_summary.csv
data/research/h4_scenario_dispersion_review/h4_aggregation_candidate_profiles.csv
data/research/h4_scenario_dispersion_review/h4_scenario_sensitive_profiles.csv
data/research/h4_scenario_dispersion_review/h4_sample_constrained_profiles.csv
data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_review_summary.csv
data/research/h4_scenario_dispersion_review/h4_scenario_dispersion_review_report.txt
```

Classification rules remain descriptive:

```text
Profile_Dispersion_Class:
  HIGH_DISPERSION when range CV or outcome magnitude CV reaches the high threshold
  MODERATE_DISPERSION when either CV reaches the moderate threshold
  STABLE_DESCRIPTIVE otherwise

Dispersion_Driver_Class:
  RANGE_DRIVEN
  MAGNITUDE_DRIVEN
  MIXED_DRIVEN
  LOW_DISPERSION

Profile_Research_Readiness_Class:
  SAMPLE_REVIEW
  SCENARIO_SENSITIVE_REVIEW
  AGGREGATION_CANDIDATE
  GENERAL_REVIEW
```

Metrics include forward range CV, outcome magnitude CV, direction alignment
dispersion, high/moderate/low scenario-period deviation counts, scenario
contribution classes, state-level dispersion summaries, and forward-window
dispersion summaries.

This phase is descriptive only. It does not change production defaults,
thresholds, production taxonomy, Event Detection defaults, Market Structure
defaults, validation behavior, H4 state deep dive outputs, D1 outputs, or
production runtime behavior. It does not add operational logic, automated
threshold changes, machine learning, backtesting, or a Decision Engine.
Scenario periods are descriptive partitions and not causal claims. No
comparative ordering is produced.

## Phase 7.5.4 — H4 Research-Ready State Outcome Deep Dive

Phase 7.5.4 adds an H4-only research deep dive after the H4/D1 structural
research phase and the D1 state outcome review. It reviews H4
`STATE_CONDITION` outcome profiles across the available H4 scenario periods,
separating research-ready, scenario-sensitive, and sample-constrained
observations.

Run after `data/research/h4_d1_structural_research` and
`data/validation/h4_d1_structural_research` exist:

```bash
python3 scripts/run_h4_state_outcome_deep_dive.py \
  --h4-d1-research-dir data/research/h4_d1_structural_research \
  --validation-output-dir data/validation/h4_d1_structural_research \
  --output-dir data/research/h4_state_outcome_deep_dive \
  --report data/research/h4_state_outcome_deep_dive/h4_state_outcome_deep_dive_report.txt
```

Required input:

```text
data/research/h4_d1_structural_research/h4_d1_price_outcome_profiles.csv
```

Optional inputs include the H4/D1 state research profiles, timeframe research
summary, scenario inventory, and scenario-level condition price outcome
summaries under each H4 validation scenario directory.

Selected H4 state profiles are filtered from `Timeframe=H4` and
`Condition_Type=STATE_CONDITION`. The review classifies them as:

```text
RESEARCH_READY
SAMPLE_CONSTRAINED_OBSERVATION
SCENARIO_SENSITIVE_OBSERVATION
```

The workflow writes:

```text
data/research/h4_state_outcome_deep_dive/h4_state_deep_dive_profile_inventory.csv
data/research/h4_state_outcome_deep_dive/h4_state_scenario_breakdown.csv
data/research/h4_state_outcome_deep_dive/h4_state_outcome_statistics.csv
data/research/h4_state_outcome_deep_dive/h4_state_scenario_comparison_matrix.csv
data/research/h4_state_outcome_deep_dive/h4_state_deep_dive_summary.csv
data/research/h4_state_outcome_deep_dive/h4_state_outcome_deep_dive_report.txt
```

Metrics include scenario sample size, forward close return, forward range,
outcome magnitude, direction alignment, dispersion, profile stability, and
scenario-period deviation from each selected profile average.

This phase is research-only. It does not change production defaults,
thresholds, production taxonomy, Event Detection defaults, Market Structure
defaults, validation behavior, or production runtime behavior. It does not add
operational logic, automated threshold changes, machine learning, backtesting,
or a Decision Engine. H4 state labels do not make macro causal claims. No
comparative ordering is produced.

## Phase 7.5.3 — D1 Research-Ready State Outcome Deep Dive

Phase 7.5.3 adds a focused D1 state outcome deep dive after the Phase 7.5.2
sample adequacy and dispersion review. It reviews research-ready D1
`STATE_CONDITION` profiles and one configured regime-sensitive observation
profile using the regime-level condition outcomes from Phase 7.5.1.

Required inputs:

```text
data/research/d1_regime_outcome_review/d1_research_ready_condition_profiles.csv
data/research/d1_regime_normalized_research/d1_regime_condition_outcomes.csv
```

Optional inputs include the regime-sensitive profile file, state quality
summary, condition inventory, review summary, and D1 state outcome profile
exports from the prior phases.

Selected state profiles:

```text
DIRECTIONAL_EXPANSION / FW=3
DIRECTIONAL_EXPANSION / FW=6
DIRECTIONAL_EXPANSION / FW=12
DIRECTIONAL_DISPLACEMENT / FW=6
DIRECTIONAL_DISPLACEMENT / FW=12
DIRECTIONAL_DISPLACEMENT / FW=3 as a regime-sensitive observation
```

Run:

```bash
python3 scripts/run_d1_state_outcome_deep_dive.py \
  --outcome-review-dir data/research/d1_regime_outcome_review \
  --regime-research-dir data/research/d1_regime_normalized_research \
  --output-dir data/research/d1_state_outcome_deep_dive \
  --report data/research/d1_state_outcome_deep_dive/d1_state_outcome_deep_dive_report.txt
```

The workflow writes:

```text
data/research/d1_state_outcome_deep_dive/d1_state_deep_dive_profile_inventory.csv
data/research/d1_state_outcome_deep_dive/d1_state_regime_breakdown.csv
data/research/d1_state_outcome_deep_dive/d1_state_outcome_statistics.csv
data/research/d1_state_outcome_deep_dive/d1_state_regime_comparison_matrix.csv
data/research/d1_state_outcome_deep_dive/d1_state_deep_dive_summary.csv
data/research/d1_state_outcome_deep_dive/d1_state_outcome_deep_dive_report.txt
```

Metrics include regime sample size, forward close return, forward range,
outcome magnitude, direction alignment, dispersion, profile stability, and
regime-period deviation from each selected profile average.

Regimes are scenario-period labels only, not macro causal classifications.
This phase is research-only. It does not change production defaults,
thresholds, production taxonomy, Event Detection defaults, Market Structure
defaults, validation behavior, or production runtime behavior. It does not add
operational logic, automated threshold changes, machine learning, backtesting,
or a Decision Engine. No comparative ordering is produced.
