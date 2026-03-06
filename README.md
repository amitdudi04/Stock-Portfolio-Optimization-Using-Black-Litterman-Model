![Python](https://img.shields.io/badge/Python-3.10-blue)
![Finance](https://img.shields.io/badge/Field-Quantitative%20Finance-green)
![Model](https://img.shields.io/badge/Model-Black--Litterman-orange)
![Research](https://img.shields.io/badge/Type-Reproducible%20Research-red)

# Regime-Sensitive Black–Litterman Tri-Market Portfolio Allocation Study

**Author:** Amit Kumar Dudi

## Research Motivation
Classical unconstrained Mean-Variance optimization models frequently exhibit severe structural vulnerability out-of-sample due to inherent estimation error maximization and instability during macroeconomic regime transitions. The Black–Litterman Bayesian allocation framework significantly improves portfolio stability by anchoring expected returns to an implied equilibrium prior, mitigating parameter uncertainty and reducing allocation fragility.

## Research Questions
This project investigates the following core hypotheses:
* **H1** — Black-Litterman improves risk-adjusted performance out-of-sample compared to classical Mean-Variance.
* **H2** — Black-Litterman reduces allocation instability (ASI) by mathematically smoothing period-to-period drift.
* **H3** — Performance remains superior after applying linear transaction costs due to restricted turnover.
* **H4** — Chinese SOE ownership does not guarantee crisis stability relative to the Private sector during targeted liquidity contractions.

## Research Pipeline Diagram
```text
Market Data
↓
Return Calculation
↓
Covariance Estimation (Ledoit–Wolf)
↓
Black–Litterman Optimization
↓
Rolling Backtest
↓
Transaction Cost Adjustment
↓
Crisis Freeze Stress Testing
↓
SOE vs Private Structural Study
↓
Statistical Validation
↓
Export Results
```

## Research Pipeline Architecture
See the full pipeline diagram here:
`docs/research_pipeline_diagram.md`

## Repository Architecture
```text
config/
core/
models/
backtesting/
analysis/
pipelines/
experiments/
results/
    v1_final_results/
visualization/
tests/
docs/
legacy/

README.md
requirements.txt
```

## Running the Research Pipeline
Before initiating the pipelines, ensure all dependencies are met:

```bash
pip install -r requirements.txt
```

To fully regenerate the empirical conclusions and test results:

```bash
python -m pipelines.run_tri_market_pipeline
python -m pipelines.run_soe_pipeline
python -m pipelines.run_crisis_analysis
```

## Empirical Results Summary
The continuous rolling out-of-sample evaluations recorded the following annualized Tri-Market Sharpe adjustments (accounting for frictional costs):

* **US (BL) vs Markowitz**: 1.208 vs 1.201
* **China (BL) vs Markowitz**: 0.669 vs 0.563
* **India (BL) vs Markowitz**: 1.075 vs 0.905

The empirical findings dictate that Bayesian shrinkage persistently improves absolute stability constraints and risk-adjusted performance by restricting parameter maximization.

## Structural Ownership Study
An isolated evaluation mapping Chinese State-Owned Enterprises versus their strictly Private operating counterparts inside the acute 2015 liquidity contraction demonstrated that State ownership does not eliminate exposure to systematic risk during market stress. Explicit downside isolation boundaries were structurally rejected.

## Documentation
The full research documentation exists natively inside `docs/`, including the core methodology logic, pipeline execution mapping, and the final peer-review-style research manuscript:

`docs/`
* `FINAL_PROJECT_IMPLEMENTATION.md`
* `FINAL_RESEARCH_RESULTS_COMPENDIUM.docx` 
* `Research_Pipeline_Architecture_Documentation.docx`
